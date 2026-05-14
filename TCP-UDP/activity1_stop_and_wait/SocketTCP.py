import socket
import random
import time

# Constantes
BUFFER_SIZE = 1024       # Tamano del buffer UDP interno
TIMEOUT = 1              # Timeout en segundos
MAX_RETRIES = 10         # Reintentos maximos
SEGMENT_SIZE = 16        # Maximo de datos por segmento
SEPARATOR = "|||"        # Separador de campos del header


class SocketTCP:
    def __init__(self):
        """Constructor sin parametros. Inicializa recursos necesarios."""
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_address = None
        self.orig_address = None
        self.seq = 0
        self.peer_seq = 0  # Numero de secuencia del peer
        self.remaining_buffer = b""
        self.remaining_length = 0
        self.timeout = TIMEOUT

    @staticmethod
    def create_segment(syn, ack, fin, seq, data=""):
        """Crea un segmento TCP con el formato SYN|||ACK|||FIN|||SEQ|||DATOS"""
        return f"{syn}{SEPARATOR}{ack}{SEPARATOR}{fin}{SEPARATOR}{seq}{SEPARATOR}{data}"

    @staticmethod
    def parse_segment(segment):
        """
        Parsea un segmento TCP y retorna un diccionario.
        Usa maxsplit=4 para permitir que los datos contengan |||
        """
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
        """Asocia el socket a una direccion."""
        self.orig_address = address
        self.udp_socket.bind(address)

    def connect(self, address):
        """
        Lado cliente del 3-way handshake.
        Establece conexion con el servidor en address.
        """
        self.dest_address = address
        self.seq = random.randint(0, 100)

        # Paso 1: Enviar SYN
        syn_segment = self.create_segment(syn=1, ack=0, fin=0, seq=self.seq)

        # Paso 2: Esperar SYN+ACK con reintentos
        self.udp_socket.settimeout(self.timeout)
        for attempt in range(MAX_RETRIES):
            self.udp_socket.sendto(syn_segment.encode(), self.dest_address)
            try:
                response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(response)

                if parsed["syn"] == 1 and parsed["ack"] == 1:
                    # Actualizar dest_address al nuevo puerto del servidor
                    self.dest_address = addr
                    self.peer_seq = parsed["seq"]
                    break
            except socket.timeout:
                continue
        else:
            raise ConnectionError("No se pudo establecer conexion: timeout en SYN+ACK")

        # Paso 3: Enviar ACK final
        ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=self.peer_seq + 1)
        self.udp_socket.sendto(ack_segment.encode(), self.dest_address)

        # Actualizar seq (SYN consume 1 numero de secuencia)
        self.seq += 1

    def accept(self):
        """
        Lado servidor del 3-way handshake.
        Espera una conexion y retorna un nuevo SocketTCP y la direccion del cliente.
        """
        # Paso 1: Esperar SYN (blocking)
        self.udp_socket.settimeout(None)
        data, client_address = self.udp_socket.recvfrom(BUFFER_SIZE)
        parsed = self.parse_segment(data)

        if parsed["syn"] != 1:
            raise ValueError("Se esperaba un segmento SYN")

        client_seq = parsed["seq"]

        # Paso 2: Crear nuevo socket para la conexion
        new_socket = SocketTCP()
        new_socket.udp_socket.bind(('', 0))  # Puerto 0 = OS asigna puerto libre
        new_socket.orig_address = new_socket.udp_socket.getsockname()
        new_socket.dest_address = client_address
        new_socket.seq = random.randint(0, 100)
        new_socket.peer_seq = client_seq

        # Paso 3: Enviar SYN+ACK y esperar ACK con reintentos
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

        # Actualizar seq (SYN consume 1 numero de secuencia)
        new_socket.seq += 1
        new_socket.peer_seq = client_seq + 1

        return new_socket, client_address

    def send(self, message):
        """
        Envia un mensaje usando Stop & Wait.
        Primero envia el largo del mensaje, luego lo divide en chunks de 16 bytes.
        """
        if isinstance(message, str):
            message = message.encode()

        # Paso 1: Enviar largo del mensaje
        length_str = str(len(message))
        length_segment = self.create_segment(syn=0, ack=0, fin=0, seq=self.seq, data=length_str)
        self._send_and_wait_ack(length_segment, self.seq + len(length_str))
        self.seq += len(length_str)

        # Paso 2: Dividir mensaje en chunks de 16 bytes
        chunks = [message[i:i+SEGMENT_SIZE] for i in range(0, len(message), SEGMENT_SIZE)]

        # Paso 3: Enviar cada chunk con Stop & Wait
        for chunk in chunks:
            chunk_str = chunk.decode('latin-1')  # Usamos latin-1 para preservar bytes
            data_segment = self.create_segment(syn=0, ack=0, fin=0, seq=self.seq, data=chunk_str)
            self._send_and_wait_ack(data_segment, self.seq + len(chunk))
            self.seq += len(chunk)

    def recv(self, buff_size):
        """
        Recibe datos usando Stop & Wait.
        Retorna hasta buff_size bytes. Si el mensaje es mas largo, se puede llamar
        multiples veces para recibir el resto.
        """
        # Si no hay mensaje pendiente, recibir el largo del mensaje
        if self.remaining_length == 0 and not self.remaining_buffer:
            self.udp_socket.settimeout(None)  # Blocking
            data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            parsed = self.parse_segment(data)

            # Enviar ACK
            ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=parsed["seq"] + len(parsed["data"]))
            self.udp_socket.sendto(ack_segment.encode(), self.dest_address)

            self.remaining_length = int(parsed["data"])
            self.peer_seq = parsed["seq"] + len(parsed["data"])

        # Comenzar con datos del buffer si los hay
        received_data = b""
        if self.remaining_buffer and self.remaining_buffer != b"FIN_RECEIVED":
            received_data = self.remaining_buffer
            self.remaining_buffer = b""

        # Calcular cuantos bytes mas necesitamos
        bytes_to_receive = min(self.remaining_length, buff_size)

        # Continuar recibiendo hasta tener suficientes datos
        while len(received_data) < bytes_to_receive and self.remaining_length > 0:
            data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            parsed = self.parse_segment(data)

            # Verificar si es un FIN
            if parsed["fin"] == 1:
                # Guardar para recv_close
                self.remaining_buffer = b"FIN_RECEIVED"
                self.remaining_length = 0
                return received_data

            # Decodificar datos usando latin-1 para preservar bytes
            chunk_data = parsed["data"].encode('latin-1')
            received_data += chunk_data

            # Enviar ACK
            ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=parsed["seq"] + len(chunk_data))
            self.udp_socket.sendto(ack_segment.encode(), self.dest_address)

            self.peer_seq = parsed["seq"] + len(chunk_data)

            # Actualizar remaining_length despues de cada chunk
            self.remaining_length -= len(chunk_data)

        # Si recibimos mas de lo necesario, guardar en buffer
        if len(received_data) > buff_size:
            data_to_return = received_data[:buff_size]
            self.remaining_buffer = received_data[buff_size:]
        else:
            data_to_return = received_data

        return data_to_return

    def close(self):
        """
        Lado que inicia el cierre de conexion (Host A).
        Implementa el cierre de 4 vias con manejo de perdidas.
        """
        # Paso 1: Enviar FIN
        fin_segment = self.create_segment(syn=0, ack=0, fin=1, seq=self.seq)

        # Paso 2: Esperar FIN+ACK con hasta 3 reintentos
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

        # Paso 3: Si se recibio FIN+ACK, enviar ACK 3 veces
        if fin_ack_received:
            ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=parsed["seq"] + 1)
            for _ in range(3):
                self.udp_socket.sendto(ack_segment.encode(), self.dest_address)
                time.sleep(self.timeout / 10)

        # Paso 4: Cerrar socket
        self.udp_socket.close()

    def recv_close(self):
        """
        Lado que responde al cierre de conexion (Host B).
        Maneja la recepcion de FIN y completa el cierre.
        """
        # Paso 1: Esperar FIN
        self.udp_socket.settimeout(None)

        # Si ya detectamos FIN en recv, solo esperamos que llegue de nuevo
        # (el cliente lo reenviara si no recibe FIN+ACK)
        data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
        parsed = self.parse_segment(data)

        if parsed["fin"] != 1:
            raise ValueError("Se esperaba un segmento FIN")

        # Paso 2: Enviar FIN+ACK
        finack_segment = self.create_segment(syn=0, ack=1, fin=1, seq=parsed["seq"] + 1)

        # Paso 3: Esperar ACK con hasta 3 reintentos
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

        # Paso 4: Cerrar socket
        self.udp_socket.close()

    def _send_and_wait_ack(self, segment, expected_ack_seq):
        """
        Metodo auxiliar que implementa el patron Stop & Wait:
        envia un segmento y espera su ACK con reintentos en caso de timeout.
        """
        self.udp_socket.settimeout(self.timeout)

        for attempt in range(MAX_RETRIES):
            self.udp_socket.sendto(segment.encode(), self.dest_address)
            try:
                response, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                parsed = self.parse_segment(response)

                # Caso borde: si recibimos SYN+ACK durante send (ACK del handshake perdido)
                if parsed["syn"] == 1 and parsed["ack"] == 1:
                    # Re-enviar ACK del handshake
                    ack_segment = self.create_segment(syn=0, ack=1, fin=0, seq=self.peer_seq + 1)
                    self.udp_socket.sendto(ack_segment.encode(), self.dest_address)
                    continue

                if parsed["ack"] == 1 and parsed["seq"] == expected_ack_seq:
                    return parsed
            except socket.timeout:
                pass

        raise ConnectionError("Se agotaron los reintentos esperando ACK")
