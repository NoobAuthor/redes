def ip_to_bytes(ip_str):
    return bytes(int(part) for part in ip_str.split('.'))

def bytes_to_ip(ip_bytes):
    return '.'.join(str(b) for b in ip_bytes[:4])

def create_packet(dest_ip, dest_port, message, ttl):
    packet = ip_to_bytes(dest_ip)
    packet += dest_port.to_bytes(2, byteorder='big')
    packet += ttl.to_bytes(1, byteorder='big')
    packet += message.encode('utf-8')
    return packet

def parse_packet(packet_bytes):
    ip = bytes_to_ip(packet_bytes[:4])
    port = int.from_bytes(packet_bytes[4:6], byteorder='big')
    ttl = packet_bytes[6]
    message = packet_bytes[7:].decode('utf-8')
    return {'ip': ip, 'port': port, 'ttl': ttl, 'message': message}
