import socket
import random
import time
from socketUDP import SocketUDP
from slidingWindowCC import SlidingWindowCC
from CongestionControl import CongestionControl

BUFFER_SIZE = 1024
TIMEOUT = 1
MAX_RETRIES = 10
SEGMENT_SIZE = 16
MSS = 8
SEPARATOR = "|||"


class SocketTCP:
    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketUDP = None
        self.dest_address = None
        self.orig_address = None
        self.seq = 0
        self.peer_seq = 0
        self.remaining_buffer = b""
        self.remaining_length = 0
        self.timeout = TIMEOUT
        self.debug_mode = False
        self.number_of_sent_segments = 0

    @staticmethod
    def create_segment(syn, ack, fin, seq, data=""):
        return f"{syn}{SEPARATOR}{ack}{SEPARATOR}{fin}{SEPARATOR}{seq}{SEPARATOR}{data}"

    @staticmethod
    def parse_segment(segment):
        if isinstance(segment, bytes):
            segment = segment.decode()
        parts = segment.split(SEPARATOR, 4)
        return {
            "syn": int(parts[0]),
            "ack": int(parts[1]),
            "fin": int(parts[2]),
            "seq": int(parts[3]),
            "data": parts[4] if len(parts) > 4 else ""
        }

    def bind(self, address):
        self.orig_address = address
        self.udp_socket.bind(address)

    def connect(self, address):
        self.dest_address = address
        self.seq = random.randint(0, 100)

        syn_segment = self.create_segment(syn=1, ack=0, fin=0, seq=self.seq)

        self.udp_socket.settimeout(self.timeout)
        for attempt in range(MAX_RETRIES):
            self.udp_socket.sendto(syn_segment.encode(), self.dest_address)
            try:
                response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(response)

                if parsed["syn"] == 1 and parsed["ack"] == 1:
                    self.dest_address = addr
                    self.peer_seq = parsed["seq"]
                    break
            except socket.timeout:
                continue
        else:
            raise ConnectionError("No se pudo establecer conexion: timeout en SYN+ACK")

        ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=self.peer_seq + 1)
        self.udp_socket.sendto(ack_segment.encode(), self.dest_address)

        self.seq += 1

    def accept(self):
        self.udp_socket.settimeout(None)
        data, client_address = self.udp_socket.recvfrom(BUFFER_SIZE)
        parsed = self.parse_segment(data)

        if parsed["syn"] != 1:
            raise ValueError("Se esperaba un segmento SYN")

        client_seq = parsed["seq"]

        new_socket = SocketTCP()
        new_socket.udp_socket.bind(('', 0))
        new_socket.orig_address = new_socket.udp_socket.getsockname()
        new_socket.dest_address = client_address
        new_socket.seq = random.randint(0, 100)
        new_socket.peer_seq = client_seq

        synack_segment = new_socket.create_segment(syn=1, ack=1, fin=0, seq=new_socket.seq)
        new_socket.udp_socket.settimeout(new_socket.timeout)

        for attempt in range(MAX_RETRIES):
            new_socket.udp_socket.sendto(synack_segment.encode(), client_address)
            try:
                response, addr = new_socket.udp_socket.recvfrom(BUFFER_SIZE)
                parsed_ack = new_socket.parse_segment(response)

                if parsed_ack["ack"] == 1:
                    break
            except socket.timeout:
                continue
        else:
            raise ConnectionError("No se recibio ACK final del handshake")

        new_socket.seq += 1
        new_socket.peer_seq = client_seq + 1

        return new_socket, client_address

    def send(self, message, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            self.send_using_stop_and_wait(message)
        elif mode == "go_back_n":
            self.send_using_go_back_n(message)
        else:
            raise ValueError(f"Modo desconocido: {mode}")

    def recv(self, buff_size, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            return self.recv_using_stop_and_wait(buff_size)
        elif mode == "go_back_n":
            return self.recv_using_go_back_n(buff_size)
        else:
            raise ValueError(f"Modo desconocido: {mode}")

    def send_using_stop_and_wait(self, message):
        if isinstance(message, str):
            message = message.encode()

        length_str = str(len(message))
        length_segment = self.create_segment(syn=0, ack=0, fin=0, seq=self.seq, data=length_str)
        self._send_and_wait_ack(length_segment, self.seq + len(length_str))
        self.seq += len(length_str)

        chunks = [message[i:i+SEGMENT_SIZE] for i in range(0, len(message), SEGMENT_SIZE)]

        for chunk in chunks:
            chunk_str = chunk.decode('latin-1')
            data_segment = self.create_segment(syn=0, ack=0, fin=0, seq=self.seq, data=chunk_str)
            self._send_and_wait_ack(data_segment, self.seq + len(chunk))
            self.seq += len(chunk)

    def recv_using_stop_and_wait(self, buff_size):
        if self.remaining_length == 0 and not self.remaining_buffer:
            self.udp_socket.settimeout(None)
            data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            parsed = self.parse_segment(data)

            ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=parsed["seq"] + len(parsed["data"]))
            self.udp_socket.sendto(ack_segment.encode(), self.dest_address)

            self.remaining_length = int(parsed["data"])
            self.peer_seq = parsed["seq"] + len(parsed["data"])

        received_data = b""
        if self.remaining_buffer and self.remaining_buffer != b"FIN_RECEIVED":
            received_data = self.remaining_buffer
            self.remaining_buffer = b""

        bytes_to_receive = min(self.remaining_length, buff_size)

        while len(received_data) < bytes_to_receive and self.remaining_length > 0:
            data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            parsed = self.parse_segment(data)

            if parsed["fin"] == 1:
                self.remaining_buffer = b"FIN_RECEIVED"
                self.remaining_length = 0
                return received_data

            chunk_data = parsed["data"].encode('latin-1')
            received_data += chunk_data

            ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=parsed["seq"] + len(chunk_data))
            self.udp_socket.sendto(ack_segment.encode(), self.dest_address)

            self.peer_seq = parsed["seq"] + len(chunk_data)

            self.remaining_length -= len(chunk_data)

        if len(received_data) > buff_size:
            data_to_return = received_data[:buff_size]
            self.remaining_buffer = received_data[buff_size:]
        else:
            data_to_return = received_data

        return data_to_return

    def send_using_go_back_n(self, message):
        if isinstance(message, str):
            message = message.encode()

        if self.socketUDP is None:
            self.socketUDP = SocketUDP()
            self.socketUDP.socket = self.udp_socket
            self.socketUDP.settimeout(self.timeout)

        congestion_controler = CongestionControl(MSS)

        message_length = str(len(message)).encode()
        data_list = [message_length] + [message[i:i+MSS] for i in range(0, len(message), MSS)]

        initial_seq = self.seq
        data_window = SlidingWindowCC(congestion_controler.get_MSS_in_cwnd(), data_list, initial_seq)

        self.socketUDP.set_timer_list_length(data_window.window_size)

        base = 0
        current_seq_total = initial_seq

        if self.debug_mode:
            print(f"[DEBUG] Inicio: {congestion_controler}")
            print(f"[DEBUG] Ventana inicial: {data_window.window_size} segmentos")

        while base < len(data_list):
            sent_indices = set()
            for i in range(data_window.window_size):
                current_data = data_window.get_data(i)
                current_seq = data_window.get_sequence_number(i)

                if current_data is None:
                    break

                if i not in sent_indices:
                    if isinstance(current_data, str):
                        current_data = current_data.encode('latin-1')
                    segment = self.create_segment(syn=0, ack=0, fin=0, seq=current_seq,
                                                 data=current_data.decode('latin-1'))
                    self.socketUDP.sendto(segment.encode(), self.dest_address, timer_index=i)
                    sent_indices.add(i)
                    self.number_of_sent_segments += 1

                    if self.debug_mode:
                        print(f"[DEBUG] Enviado seg {base+i}, seq={current_seq}, timer={i}")

            try:
                answer, address = self.socketUDP.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(answer)

                if parsed["ack"] == 1:
                    ack_seq = parsed["seq"]

                    window_moved = False
                    for i in range(data_window.window_size):
                        current_seq = data_window.get_sequence_number(i)
                        current_data = data_window.get_data(i)

                        if current_seq is None:
                            break

                        data_len = len(current_data) if isinstance(current_data, bytes) else len(current_data.encode())

                        if ack_seq == current_seq + data_len:
                            steps_to_move = i + 1
                            old_size = data_window.window_size

                            base += steps_to_move
                            current_seq_total = ack_seq
                            data_window.move_window(steps_to_move)

                            for j in range(steps_to_move):
                                self.socketUDP.stop_timer(timer_index=j)

                            congestion_controler.event_ack_received()
                            new_window_size = congestion_controler.get_MSS_in_cwnd()

                            if new_window_size != old_size:
                                data_window.update_window_size(new_window_size)
                                self.socketUDP.set_timer_list_length(new_window_size)

                                if self.debug_mode:
                                    print(f"[DEBUG] Ventana cambió: {old_size} -> {new_window_size} MSS")
                                    print(f"[DEBUG] {congestion_controler}")

                                if new_window_size > old_size:
                                    extra_segments = new_window_size - old_size
                                    for k in range(extra_segments):
                                        idx = old_size + k
                                        if idx < data_window.window_size:
                                            extra_data = data_window.get_data(idx)
                                            extra_seq = data_window.get_sequence_number(idx)
                                            if extra_data is not None:
                                                if isinstance(extra_data, str):
                                                    extra_data = extra_data.encode('latin-1')
                                                segment = self.create_segment(syn=0, ack=0, fin=0,
                                                                            seq=extra_seq,
                                                                            data=extra_data.decode('latin-1'))
                                                self.socketUDP.sendto(segment.encode(), self.dest_address,
                                                                    timer_index=idx)
                                                self.number_of_sent_segments += 1

                                                if self.debug_mode:
                                                    print(f"[DEBUG] Nuevo seg {base+idx}, seq={extra_seq}")

                            sent_indices.clear()
                            window_moved = True

                            if self.debug_mode:
                                print(f"[DEBUG] ACK recibido para seq={ack_seq}, base ahora={base}")

                            break

                    if not window_moved:
                        first_seq = data_window.get_sequence_number(0)
                        if first_seq is not None and ack_seq > first_seq:
                            while data_window.get_sequence_number(data_window.window_size - 1) is None or \
                                  ack_seq > data_window.get_sequence_number(data_window.window_size - 1):
                                if base >= len(data_list):
                                    break

                                base += 1
                                data_window.move_window(1)
                                sent_indices.clear()

                                if self.debug_mode:
                                    print(f"[DEBUG] Ventana ajustada, base={base}")

            except TimeoutError:
                if self.debug_mode:
                    print(f"[DEBUG] TIMEOUT detectado")

                congestion_controler.event_timeout()
                new_window_size = congestion_controler.get_MSS_in_cwnd()

                if self.debug_mode:
                    print(f"[DEBUG] Despues de timeout: {congestion_controler}")

                if new_window_size != data_window.window_size:
                    data_window.update_window_size(new_window_size)
                    self.socketUDP.set_timer_list_length(new_window_size)

                for i in range(data_window.window_size):
                    current_data = data_window.get_data(i)
                    current_seq = data_window.get_sequence_number(i)

                    if current_data is None:
                        break

                    if isinstance(current_data, str):
                        current_data = current_data.encode('latin-1')

                    segment = self.create_segment(syn=0, ack=0, fin=0, seq=current_seq,
                                                 data=current_data.decode('latin-1'))
                    self.socketUDP.sendto(segment.encode(), self.dest_address, timer_index=i)
                    self.number_of_sent_segments += 1

                    if self.debug_mode:
                        print(f"[DEBUG] Retransmision seg {base+i}, seq={current_seq}")

                sent_indices.clear()

        self.seq = current_seq_total

    def recv_using_go_back_n(self, buff_size):
        if self.remaining_length == 0 and not self.remaining_buffer:
            self.udp_socket.settimeout(None)
            data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            parsed = self.parse_segment(data)

            ack_segment = self.create_segment(syn=0, ack=1, fin=0,
                                             seq=parsed["seq"] + len(parsed["data"]))
            self.udp_socket.sendto(ack_segment.encode(), self.dest_address)

            self.remaining_length = int(parsed["data"])
            self.peer_seq = parsed["seq"] + len(parsed["data"])

        received_data = b""
        if self.remaining_buffer and self.remaining_buffer != b"FIN_RECEIVED":
            received_data = self.remaining_buffer
            self.remaining_buffer = b""

        bytes_to_receive = min(self.remaining_length, buff_size)

        while len(received_data) < bytes_to_receive and self.remaining_length > 0:
            data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            parsed = self.parse_segment(data)

            if parsed["fin"] == 1:
                self.remaining_buffer = b"FIN_RECEIVED"
                self.remaining_length = 0
                return received_data

            chunk_data = parsed["data"].encode('latin-1')

            if parsed["seq"] == self.peer_seq:
                received_data += chunk_data
                self.peer_seq += len(chunk_data)
                self.remaining_length -= len(chunk_data)

            ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=self.peer_seq)
            self.udp_socket.sendto(ack_segment.encode(), self.dest_address)

        if len(received_data) > buff_size:
            data_to_return = received_data[:buff_size]
            self.remaining_buffer = received_data[buff_size:]
        else:
            data_to_return = received_data

        return data_to_return

    def close(self):
        fin_segment = self.create_segment(syn=0, ack=0, fin=1, seq=self.seq)

        self.udp_socket.settimeout(self.timeout)
        fin_ack_received = False

        for attempt in range(3):
            self.udp_socket.sendto(fin_segment.encode(), self.dest_address)
            try:
                response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(response)

                if parsed["fin"] == 1 and parsed["ack"] == 1:
                    fin_ack_received = True
                    break
            except socket.timeout:
                continue

        if fin_ack_received:
            ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=parsed["seq"] + 1)
            for _ in range(3):
                self.udp_socket.sendto(ack_segment.encode(), self.dest_address)
                time.sleep(self.timeout / 10)

        self.udp_socket.close()

    def recv_close(self):
        self.udp_socket.settimeout(None)

        data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
        parsed = self.parse_segment(data)

        if parsed["fin"] != 1:
            raise ValueError("Se esperaba un segmento FIN")

        finack_segment = self.create_segment(syn=0, ack=1, fin=1, seq=parsed["seq"] + 1)

        self.udp_socket.settimeout(self.timeout)

        for attempt in range(3):
            self.udp_socket.sendto(finack_segment.encode(), self.dest_address)
            try:
                response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                parsed_ack = self.parse_segment(response)

                if parsed_ack["ack"] == 1:
                    break
            except socket.timeout:
                continue

        self.udp_socket.close()

    def _send_and_wait_ack(self, segment, expected_ack_seq):
        self.udp_socket.settimeout(self.timeout)

        for attempt in range(MAX_RETRIES):
            self.udp_socket.sendto(segment.encode(), self.dest_address)
            try:
                response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(response)

                if parsed["syn"] == 1 and parsed["ack"] == 1:
                    ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=self.peer_seq + 1)
                    self.udp_socket.sendto(ack_segment.encode(), self.dest_address)
                    continue

                if parsed["ack"] == 1 and parsed["seq"] == expected_ack_seq:
                    return parsed
            except socket.timeout:
                pass

        raise ConnectionError("Se agotaron los reintentos esperando ACK")
