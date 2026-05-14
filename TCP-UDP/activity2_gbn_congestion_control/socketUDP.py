import socket
import time
import threading


class SocketUDP:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timeout_duration = 1.0
        self.timers = [None]
        self.timer_start_times = [None]
        self.stopped_timers = []
        self.lock = threading.Lock()

    def bind(self, address):
        self.socket.bind(address)

    def settimeout(self, timeout):
        if timeout is not None:
            self.timeout_duration = timeout
            self.socket.settimeout(timeout)
        else:
            self.socket.settimeout(None)

    def getsockname(self):
        return self.socket.getsockname()

    def set_timer_list_length(self, number_of_timers):
        with self.lock:
            self.timers = [None] * number_of_timers
            self.timer_start_times = [None] * number_of_timers

    def sendto(self, data, address, timer_index=0):
        self.socket.sendto(data, address)

        with self.lock:
            if timer_index < len(self.timers):
                self.timer_start_times[timer_index] = time.time()
                if timer_index in self.stopped_timers:
                    self.stopped_timers.remove(timer_index)

    def recvfrom(self, buffer_size):
        self.socket.settimeout(0.1)

        while True:
            with self.lock:
                current_time = time.time()
                for i, start_time in enumerate(self.timer_start_times):
                    if start_time is not None:
                        elapsed = current_time - start_time
                        if elapsed >= self.timeout_duration:
                            if i not in self.stopped_timers:
                                self.stopped_timers.append(i)
                            self.timer_start_times[i] = None

                if self.stopped_timers:
                    stopped = self.stopped_timers.copy()
                    self.stopped_timers.clear()
                    raise TimeoutError("Timeout en uno o mas timers")

            try:
                data, address = self.socket.recvfrom(buffer_size)
                return data, address
            except socket.timeout:
                continue
            except BlockingIOError:
                continue

    def stop_timer(self, timer_index=0):
        with self.lock:
            if timer_index < len(self.timer_start_times):
                self.timer_start_times[timer_index] = None
                if timer_index in self.stopped_timers:
                    self.stopped_timers.remove(timer_index)

    def get_stopped_timers(self):
        with self.lock:
            return self.stopped_timers.copy()

    def close(self):
        self.socket.close()
