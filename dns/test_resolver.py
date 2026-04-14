#!/usr/bin/env python3
import socket
from dnslib import DNSRecord

RESOLVER_IP = '127.0.0.1'
RESOLVER_PORT = 8000
SOCKET_TIMEOUT = 10
BUFFER_SIZE = 4096

def test_resolver(domain, resolver_ip=RESOLVER_IP, resolver_port=RESOLVER_PORT):
    print(f"\n{'='*60}")
    print(f"Consultando: {domain}")
    print(f"Servidor: {resolver_ip}:{resolver_port}")
    print(f"{'='*60}")
    q = DNSRecord.question(domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(SOCKET_TIMEOUT)
    try:
        sock.sendto(bytes(q.pack()), (resolver_ip, resolver_port))
        data, _ = sock.recvfrom(BUFFER_SIZE)
        response = DNSRecord.parse(data)
        print("\nRespuesta recibida:")
        print(response)
        if response.header.a > 0:
            print("\nDirecciones IP:")
            for rr in response.rr:
                print(f"  {rr.rname} -> {rr.rdata}")
        else:
            print("\nNo se encontraron respuestas tipo A")
    except socket.timeout:
        print("ERROR: Timeout - El resolver no respondió")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    print("Iniciando pruebas del resolver DNS...")
    print("(Asegúrate de que resolver.py esté corriendo en otra terminal)")
    test_resolver("www.uchile.cl")
    test_resolver("eol.uchile.cl")
    test_resolver("example.com")
    test_resolver("cc4303.bachmann.cl")
    print("\n" + "="*60)
    print("Pruebas completadas")
    print("="*60)
