import sys
import socket
from packet_utils import create_packet

def main():
    if len(sys.argv) != 11:
        print("Usage: python3 send_message.py dest_ip dest_port message send_ip send_port ttl packet_id offset size flag")
        sys.exit(1)

    dest_ip = sys.argv[1]
    dest_port = int(sys.argv[2])
    message = sys.argv[3]
    send_ip = sys.argv[4]
    send_port = int(sys.argv[5])
    ttl = int(sys.argv[6])
    packet_id = int(sys.argv[7])
    offset = int(sys.argv[8])
    size = int(sys.argv[9])
    flag = int(sys.argv[10])

    packet = create_packet(dest_ip, dest_port, message, ttl, packet_id, offset, size, flag)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (send_ip, send_port))
    print(f"Sent packet to {send_ip}:{send_port} with destination {dest_ip}:{dest_port}")

if __name__ == "__main__":
    main()
