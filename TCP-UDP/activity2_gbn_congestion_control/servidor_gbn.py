#!/usr/bin/env python3
from SocketTCP_GBN import SocketTCP

HOST = ''
PORT = 12345

socket_servidor = SocketTCP()
socket_servidor.bind((HOST, PORT))
print(f"Servidor escuchando en puerto {PORT}...")

socket_conexion, addr = socket_servidor.accept()
print(f"Cliente conectado desde {addr}")

archivo_recibido = b""
while True:
    datos = socket_conexion.recv(1024, mode="go_back_n")
    if not datos:
        break
    archivo_recibido += datos
    print(f"Recibidos {len(datos)} bytes (total: {len(archivo_recibido)})")

with open("recibido_gbn.txt", "wb") as f:
    f.write(archivo_recibido)

print(f"Archivo recibido: {len(archivo_recibido)} bytes")
print(f"Guardado en recibido_gbn.txt")

socket_conexion.recv_close()
print("Conexion cerrada")
