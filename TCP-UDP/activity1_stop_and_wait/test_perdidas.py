#!/usr/bin/env python3
"""
Test de Stop & Wait con simulacion de perdidas de paquetes.
Verifica que el mecanismo de retransmision funciona correctamente.
"""
from SocketTCP import SocketTCP
import socket
import threading
import time
import random


def get_free_port():
    """Returns a free port assigned by the OS."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class LossySocket:
    """Proxy around a UDP socket that drops packets with a given probability."""

    def __init__(self, real_socket, loss_rate):
        self._socket = real_socket
        self.loss_rate = loss_rate
        self.stats = {"sent": 0, "dropped": 0}

    def sendto(self, data, addr):
        self.stats["sent"] += 1
        if random.random() < self.loss_rate:
            self.stats["dropped"] += 1
            return len(data)
        return self._socket.sendto(data, addr)

    def __getattr__(self, name):
        return getattr(self._socket, name)

    @property
    def real_socket(self):
        return self._socket


def test_send_con_perdidas(loss_rate=0.3):
    """Test: paquetes de datos del sender se pierden, retransmision los recupera."""
    print("=" * 60)
    print(f"Test 1: Perdida de datos del sender ({int(loss_rate*100)}%)")
    print("=" * 60)

    msg = "Hola mundo con perdidas!"
    result = {}
    port = get_free_port()

    def run_server():
        server = SocketTCP()
        server.bind(('', port))
        connection, addr = server.accept()
        received = connection.recv(1024)
        result["received"] = received.decode()
        connection.recv_close()
        server.udp_socket.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(0.3)

    client = SocketTCP()
    client.connect(('localhost', port))

    # Aplicar perdidas solo durante send
    lossy = LossySocket(client.udp_socket, loss_rate)
    client.udp_socket = lossy

    client.send(msg.encode())

    # Restaurar socket real para close
    client.udp_socket = lossy.real_socket
    client.close()

    server_thread.join(timeout=15)

    print(f"  Paquetes intentados: {lossy.stats['sent']}, Descartados: {lossy.stats['dropped']}")

    if result.get("received") == msg:
        print(f"  ✓ Mensaje recibido correctamente: '{result['received']}'")
        return True
    else:
        print(f"  ✗ Fallo - esperado '{msg}', recibido '{result.get('received', 'NADA')}'")
        return False


def test_send_largo_con_perdidas(loss_rate=0.3):
    """Test: mensaje largo (multiples chunks) con perdidas del sender."""
    print("\n" + "=" * 60)
    print(f"Test 2: Mensaje largo con {int(loss_rate*100)}% perdida (sender)")
    print("=" * 60)

    msg = "A" * 64 + "B" * 64  # 128 bytes = 8 chunks de 16 bytes
    result = {}
    port = get_free_port()

    def run_server():
        server = SocketTCP()
        server.bind(('', port))
        connection, addr = server.accept()
        received = connection.recv(1024)
        result["received"] = received.decode()
        connection.recv_close()
        server.udp_socket.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(0.3)

    client = SocketTCP()
    client.connect(('localhost', port))

    lossy = LossySocket(client.udp_socket, loss_rate)
    client.udp_socket = lossy

    client.send(msg.encode())

    client.udp_socket = lossy.real_socket
    client.close()

    server_thread.join(timeout=30)

    print(f"  Mensaje: {len(msg)} bytes ({len(msg)//16} chunks)")
    print(f"  Paquetes intentados: {lossy.stats['sent']}, Descartados: {lossy.stats['dropped']}")

    if result.get("received") == msg:
        print(f"  ✓ Mensaje largo recibido correctamente ({len(result['received'])} bytes)")
        return True
    else:
        received = result.get("received", "")
        print(f"  ✗ Fallo - esperado {len(msg)} bytes, recibido {len(received)} bytes")
        return False


def test_send_alta_perdida(loss_rate=0.5):
    """Test: alta tasa de perdida, verifica que retransmision sigue funcionando."""
    print("\n" + "=" * 60)
    print(f"Test 3: Alta perdida ({int(loss_rate*100)}%) - stress test")
    print("=" * 60)

    msg = "Mensaje que sobrevive 50% de perdida"
    result = {}
    port = get_free_port()

    def run_server():
        server = SocketTCP()
        server.bind(('', port))
        connection, addr = server.accept()
        received = connection.recv(1024)
        result["received"] = received.decode()
        connection.recv_close()
        server.udp_socket.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(0.3)

    client = SocketTCP()
    client.connect(('localhost', port))

    lossy = LossySocket(client.udp_socket, loss_rate)
    client.udp_socket = lossy

    client.send(msg.encode())

    client.udp_socket = lossy.real_socket
    client.close()

    server_thread.join(timeout=30)

    print(f"  Paquetes intentados: {lossy.stats['sent']}, Descartados: {lossy.stats['dropped']}")

    if result.get("received") == msg:
        print(f"  ✓ Mensaje recibido correctamente con {int(loss_rate*100)}% perdida")
        return True
    else:
        print(f"  ✗ Fallo - esperado '{msg}', recibido '{result.get('received', 'NADA')}'")
        return False


def test_ack_con_perdidas(loss_rate=0.3):
    """Test: ACKs del receiver se pierden. Expone si hay manejo de duplicados."""
    print("\n" + "=" * 60)
    print(f"Test 4: Perdida de ACKs ({int(loss_rate*100)}%) - receiver side")
    print("=" * 60)

    msg = "Test ACK loss"
    result = {}
    error_info = {}
    port = get_free_port()

    def run_server():
        server = SocketTCP()
        server.bind(('', port))
        connection, addr = server.accept()

        # Aplicar perdidas en ACKs del servidor
        lossy = LossySocket(connection.udp_socket, loss_rate)
        connection.udp_socket = lossy

        try:
            received = connection.recv(1024)
            result["received"] = received.decode()
            result["stats"] = lossy.stats
            # Restaurar para close
            connection.udp_socket = lossy.real_socket
            connection.recv_close()
        except Exception as e:
            error_info["error"] = str(e)
            result["stats"] = lossy.stats
        server.udp_socket.close()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(0.3)

    client = SocketTCP()
    client.connect(('localhost', port))
    try:
        client.send(msg.encode())
        client.close()
    except ConnectionError as e:
        error_info["client_error"] = str(e)
        try:
            client.udp_socket.close()
        except:
            pass

    server_thread.join(timeout=20)

    stats = result.get("stats", {"sent": 0, "dropped": 0})
    print(f"  ACKs intentados: {stats['sent']}, Descartados: {stats['dropped']}")

    if result.get("received") == msg:
        print(f"  ✓ Mensaje recibido correctamente (duplicados manejados)")
        return True
    elif error_info:
        print(f"  ⚠ Limitacion detectada: el receiver no descarta duplicados")
        if "client_error" in error_info:
            print(f"    Cliente: {error_info['client_error']}")
        if "error" in error_info:
            print(f"    Servidor: {error_info['error']}")
        print(f"    (Esto es esperado si recv() no verifica seq numbers)")
        return False
    else:
        received = result.get("received", "")
        print(f"  ✗ Datos corruptos: esperado '{msg}', recibido '{received}'")
        print(f"    (Duplicados no descartados por el receiver)")
        return False


if __name__ == "__main__":
    random.seed(42)
    results = []

    results.append(("Perdida sender", test_send_con_perdidas(0.3)))
    results.append(("Mensaje largo", test_send_largo_con_perdidas(0.3)))
    results.append(("Alta perdida", test_send_alta_perdida(0.5)))
    results.append(("Perdida ACKs", test_ack_con_perdidas(0.3)))

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for name, passed in results:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    passed_count = sum(1 for _, p in results if p)
    total = len(results)
    print(f"\n  {passed_count}/{total} tests pasaron")
    print("=" * 60)
