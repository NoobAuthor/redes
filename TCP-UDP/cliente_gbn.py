#!/usr/bin/env python3
import sys
import time
from SocketTCP_GBN import SocketTCP

HOST = 'localhost'
PORT = 12345

if len(sys.argv) < 2:
    print("Uso: python3 cliente_gbn.py <archivo> [debug]")
    sys.exit(1)

archivo = sys.argv[1]
debug = len(sys.argv) > 2 and sys.argv[2] == "debug"

socket_cliente = SocketTCP()
socket_cliente.debug_mode = debug

socket_cliente.connect((HOST, PORT))
print(f"Conectado al servidor {HOST}:{PORT}")

with open(archivo, "rb") as f:
    datos = f.read()

print(f"Enviando archivo {archivo} ({len(datos)} bytes)...")

inicio = time.time()
socket_cliente.send(datos, mode="go_back_n")
fin = time.time()

tiempo = fin - inicio
print(f"Archivo enviado en {tiempo:.2f} segundos")
print(f"Segmentos enviados: {socket_cliente.number_of_sent_segments}")

socket_cliente.close()
print("Conexion cerrada")
