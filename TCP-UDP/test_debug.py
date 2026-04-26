#!/usr/bin/env python3
"""
Test debug para entender el problema con recv() multiple
"""
from SocketTCP import SocketTCP
import threading
import time


def test_recv_multiple():
    """Test de recv con buff_size < message_length"""
    print("="*60)
    print("Test Debug: Recv Multiple Calls")
    print("="*60)

    msg = "Mensaje de largo 19"
    buff_size = 14

    # Servidor
    def run_server():
        server = SocketTCP()
        server.bind(('', 8010))
        connection, addr = server.accept()
        print(f"[Servidor] Conexion aceptada")
        print(f"[Servidor] remaining_length inicial: {connection.remaining_length}")

        part1 = connection.recv(buff_size)
        print(f"[Servidor] Primera llamada recv({buff_size}): '{part1.decode()}' ({len(part1)} bytes)")
        print(f"[Servidor] remaining_length despues de recv 1: {connection.remaining_length}")
        print(f"[Servidor] remaining_buffer despues de recv 1: {connection.remaining_buffer}")

        part2 = connection.recv(buff_size)
        print(f"[Servidor] Segunda llamada recv({buff_size}): '{part2.decode()}' ({len(part2)} bytes)")
        print(f"[Servidor] remaining_length despues de recv 2: {connection.remaining_length}")
        print(f"[Servidor] remaining_buffer despues de recv 2: {connection.remaining_buffer}")

        full = part1 + part2
        print(f"[Servidor] Mensaje completo: '{full.decode()}' ({len(full)} bytes)")

        if full.decode() == msg:
            print(f"✓ Test Passed")
        else:
            print(f"✗ Test Failed - esperado '{msg}', recibido '{full.decode()}'")

        connection.recv_close()
        server.udp_socket.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(0.5)

    # Cliente
    print(f"[Cliente] Enviando mensaje: '{msg}' ({len(msg)} bytes)")
    client = SocketTCP()
    client.connect(('localhost', 8010))
    client.send(msg.encode())
    print(f"[Cliente] Mensaje enviado")
    client.close()

    server_thread.join()


if __name__ == "__main__":
    try:
        test_recv_multiple()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
