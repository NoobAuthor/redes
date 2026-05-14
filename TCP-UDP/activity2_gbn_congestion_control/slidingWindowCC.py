class SlidingWindowCC:
    def __init__(self, window_size, data_list, initial_seq):
        self.window_size = window_size
        self.data_list = data_list
        self.initial_seq = initial_seq
        self.current_position = 0

        self.window_data = []
        self.window_seq = []
        self._fill_window()

    def _fill_window(self):
        self.window_data = []
        self.window_seq = []

        seq = self.initial_seq
        for i in range(self.window_size):
            idx = self.current_position + i
            if idx < len(self.data_list):
                data = self.data_list[idx]
                self.window_data.append(data)
                self.window_seq.append(seq)
                seq += len(data) if data else 0
            else:
                self.window_data.append(None)
                self.window_seq.append(None)

    def move_window(self, steps_to_move):
        if steps_to_move > self.window_size:
            raise ValueError(f"No se puede avanzar mas que el tamaño de la ventana ({self.window_size})")

        self.current_position += steps_to_move

        for i in range(steps_to_move):
            if i < len(self.window_data) and self.window_data[i] is not None:
                self.initial_seq += len(self.window_data[i])

        self._fill_window()

    def get_sequence_number(self, window_index):
        if 0 <= window_index < len(self.window_seq):
            return self.window_seq[window_index]
        return None

    def get_data(self, window_index):
        if 0 <= window_index < len(self.window_data):
            return self.window_data[window_index]
        return None

    def put_data(self, data, seq, window_index):
        if window_index >= self.window_size:
            raise ValueError(f"window_index {window_index} fuera de rango")

        while len(self.window_data) <= window_index:
            self.window_data.append(None)
            self.window_seq.append(None)

        if any(s is not None for s in self.window_seq):
            min_seq = min(s for s in self.window_seq if s is not None)
            max_possible_seq = min_seq + sum(
                len(d) for d in self.window_data if d is not None
            ) * self.window_size

            if not (min_seq <= seq <= max_possible_seq):
                raise ValueError(f"Numero de secuencia {seq} fuera de rango valido")

        self.window_data[window_index] = data
        self.window_seq[window_index] = seq

    def update_window_size(self, new_size):
        old_size = self.window_size
        self.window_size = new_size

        if new_size > old_size:
            self._fill_window()
        elif new_size < old_size:
            self.window_data = self.window_data[:new_size]
            self.window_seq = self.window_seq[:new_size]

    def __str__(self):
        header = "+------+" + "".join(["-" * 9 + "+" for _ in range(self.window_size)])

        data_row = "| Data |"
        for data in self.window_data:
            if data is None:
                data_row += " None    |"
            else:
                data_str = str(data)
                if len(data_str) > 7:
                    data_str = data_str[:7]
                data_row += f" {data_str:<7} |"

        seq_row = "| Seq  |"
        for seq in self.window_seq:
            if seq is None:
                seq_row += " None    |"
            else:
                seq_row += f" {seq:<7} |"

        return f"{header}\n{data_row}\n{header}\n{seq_row}\n{header}"
