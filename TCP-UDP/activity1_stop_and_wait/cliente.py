#!/usr/bin/env python3
"""
Cliente TCP-sobre-UDP
Uso: python3 cliente.py <host> <puerto> < archivo.txt
"""
import sys
from SocketTCP import SocketTCP


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 cliente.py <host> <puerto> < archivo.txt", file=sys.stderr)
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    # Leer archivo desde stdin
    data = sys.stdin.buffer.read()

    # Crear socket y conectar
    client = SocketTCP()
    print(f"Conectando a {host}:{port}...", file=sys.stderr)
    client.connect((host, port))
    print(f"Conexion establecida", file=sys.stderr)

    # Enviar datos
    print(f"Enviando {len(data)} bytes...", file=sys.stderr)
    client.send(data)
    print(f"Datos enviados", file=sys.stderr)

    # Cerrar conexion
    print(f"Cerrando conexion...", file=sys.stderr)
    client.close()
    print(f"Conexion cerrada", file=sys.stderr)


if __name__ == "__main__":
    main()
