import sys
import socket
import time
from packet_utils import create_packet

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 prueba_router.py headers IP_router_inicial puerto_router_inicial")
        print("headers format: dest_ip;dest_port;ttl;packet_id")
        sys.exit(1)

    headers_str = sys.argv[1]
    router_ip = sys.argv[2]
    router_port = int(sys.argv[3])

    parts = headers_str.split(';')
    dest_ip = parts[0]
    dest_port = int(parts[1])
    ttl = int(parts[2])
    packet_id = int(parts[3]) if len(parts) > 3 else 1

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        for line in sys.stdin:
            line = line.strip()
            if line:
                message_size = len(line.encode('utf-8'))
                packet = create_packet(dest_ip, dest_port, line, ttl, packet_id, 0, message_size, 0)
                sock.sendto(packet, (router_ip, router_port))
                print(f"Sent: {line}")
                packet_id += 1
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStopped by user")

if __name__ == "__main__":
    main()
