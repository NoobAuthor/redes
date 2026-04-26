#!/usr/bin/env python3
"""
Servidor TCP-sobre-UDP
Escucha en un puerto y recibe archivos.
"""
import sys
from SocketTCP import SocketTCP


SERVER_ADDRESS = ('', 8000)  # Puerto por defecto
RECV_BUFFER = 4096


def main():
    # Permitir especificar puerto como argumento
    port = SERVER_ADDRESS[1]
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    # Crear socket servidor
    server = SocketTCP()
    server.bind(('', port))
    print(f"Servidor escuchando en puerto {port}...", file=sys.stderr)

    # Aceptar conexion
    connection, client_addr = server.accept()
    print(f"Conexion aceptada desde {client_addr}", file=sys.stderr)

    # Recibir datos
    full_message = b""
    while True:
        data = connection.recv(RECV_BUFFER)
        if not data:
            break
        full_message += data
        # Si ya recibimos todo el mensaje, salir
        if connection.remaining_length == 0 and not connection.remaining_buffer:
            break

    # Imprimir mensaje recibido a stdout
    sys.stdout.buffer.write(full_message)
    sys.stdout.flush()

    print(f"\nDatos recibidos: {len(full_message)} bytes", file=sys.stderr)

    # Cerrar conexion
    print(f"Cerrando conexion...", file=sys.stderr)
    connection.recv_close()
    print(f"Conexion cerrada", file=sys.stderr)


if __name__ == "__main__":
    main()
