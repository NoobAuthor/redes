#!/usr/bin/env python3
"""
Tests basicos para SocketTCP
"""
from SocketTCP import SocketTCP
import threading
import time


def test_handshake():
    """Test del 3-way handshake"""
    print("\n" + "="*60)
    print("Test 1: 3-way Handshake")
    print("="*60)

    # Servidor en thread separado
    def run_server():
        server = SocketTCP()
        server.bind(('', 8001))
        print("[Servidor] Esperando conexion...")
        connection, addr = server.accept()
        print(f"[Servidor] Conexion aceptada desde {addr}")
        connection.udp_socket.close()
        server.udp_socket.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(0.5)  # Dar tiempo al servidor

    # Cliente
    client = SocketTCP()
    print("[Cliente] Conectando...")
    client.connect(('localhost', 8001))
    print("[Cliente] Conexion establecida")
    client.udp_socket.close()

    server_thread.join()
    print("✓ Test 1: Passed\n")


def test_send_recv():
    """Test de send y recv con mensajes de diferentes tamanos"""
    print("="*60)
    print("Test 2, 3, 4: Send y Recv")
    print("="*60)

    messages = [
        ("Mensje de len=16", 16),  # Exactamente 16
        ("Mensaje de largo 19", 19),  # Mayor a 16
        ("Mensaje de largo 19", 14),  # buff_size menor que message
    ]

    for test_num, (msg, buff_size) in enumerate(messages, start=2):
        print(f"\n--- Test {test_num} ---")

        # Servidor
        def run_server(msg, buff_size, test_n):
            server = SocketTCP()
            server.bind(('', 8000 + test_n))
            connection, addr = server.accept()
            print(f"[Servidor] Test {test_n}: Conexion aceptada")

            if buff_size < len(msg):
                # Llamar recv 2 veces
                part1 = connection.recv(buff_size)
                part2 = connection.recv(buff_size)
                full = part1 + part2
                print(f"[Servidor] Recibido en 2 partes: {full.decode()}")
            else:
                full = connection.recv(buff_size)
                print(f"[Servidor] Recibido: {full.decode()}")

            if full.decode() == msg:
                print(f"✓ Test {test_n}: Passed")
            else:
                print(f"✗ Test {test_n}: Failed - esperado '{msg}', recibido '{full.decode()}'")

            connection.recv_close()
            server.udp_socket.close()

        server_thread = threading.Thread(target=run_server, args=(msg, buff_size, test_num))
        server_thread.start()
        time.sleep(0.5)

        # Cliente
        client = SocketTCP()
        client.connect(('localhost', 8000 + test_num))
        client.send(msg.encode())
        client.close()

        server_thread.join()


def test_cierre():
    """Test del cierre de conexion"""
    print("\n" + "="*60)
    print("Test 5: Cierre de Conexion")
    print("="*60)

    # Servidor
    def run_server():
        server = SocketTCP()
        server.bind(('', 8005))
        connection, addr = server.accept()
        print("[Servidor] Conexion aceptada")

        # Recibir mensaje simple
        data = connection.recv(100)
        print(f"[Servidor] Recibido: {data.decode()}")

        # Cerrar
        print("[Servidor] Cerrando conexion...")
        connection.recv_close()
        print("[Servidor] Conexion cerrada")
        server.udp_socket.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(0.5)

    # Cliente
    client = SocketTCP()
    client.connect(('localhost', 8005))
    client.send("Hola mundo".encode())
    print("[Cliente] Cerrando conexion...")
    client.close()
    print("[Cliente] Conexion cerrada")

    server_thread.join()
    print("✓ Test 5: Passed\n")


if __name__ == "__main__":
    print("\nEjecutando tests basicos para SocketTCP...\n")

    try:
        test_handshake()
        test_send_recv()
        test_cierre()
        print("="*60)
        print("Todos los tests pasaron exitosamente!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Error en los tests: {e}")
        import traceback
        traceback.print_exc()
