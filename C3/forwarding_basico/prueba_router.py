import sys
import socket
import time
from packet_utils import create_packet

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 prueba_router.py headers IP_router_inicial puerto_router_inicial")
        print("headers format: dest_ip;dest_port;ttl")
        sys.exit(1)

    headers_str = sys.argv[1]
    router_ip = sys.argv[2]
    router_port = int(sys.argv[3])

    dest_ip, dest_port, ttl = headers_str.split(';')
    dest_port = int(dest_port)
    ttl = int(ttl)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        for line in sys.stdin:
            line = line.strip()
            if line:
                packet = create_packet(dest_ip, dest_port, line, ttl)
                sock.sendto(packet, (router_ip, router_port))
                print(f"Sent: {line}")
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStopped by user")

if __name__ == "__main__":
    main()
