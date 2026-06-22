def ip_to_bytes(ip_str):
    return bytes(int(part) for part in ip_str.split('.'))

def bytes_to_ip(ip_bytes):
    return '.'.join(str(b) for b in ip_bytes[:4])

def create_packet(dest_ip, dest_port, message, ttl, packet_id, offset, size, flag):
    packet = ip_to_bytes(dest_ip)
    packet += dest_port.to_bytes(2, byteorder='big')
    packet += ttl.to_bytes(1, byteorder='big')
    packet += packet_id.to_bytes(2, byteorder='big')
    packet += offset.to_bytes(4, byteorder='big')
    packet += size.to_bytes(4, byteorder='big')
    packet += flag.to_bytes(1, byteorder='big')
    packet += message.encode('utf-8')
    return packet

def parse_packet(packet_bytes):
    ip = bytes_to_ip(packet_bytes[:4])
    port = int.from_bytes(packet_bytes[4:6], byteorder='big')
    ttl = packet_bytes[6]
    packet_id = int.from_bytes(packet_bytes[7:9], byteorder='big')
    offset = int.from_bytes(packet_bytes[9:13], byteorder='big')
    size = int.from_bytes(packet_bytes[13:17], byteorder='big')
    flag = int.from_bytes(packet_bytes[17:18], byteorder='big')
    message = packet_bytes[18:].decode('utf-8')
    return {
        'ip': ip,
        'port': port,
        'ttl': ttl,
        'id': packet_id,
        'offset': offset,
        'size': size,
        'flag': flag,
        'message': message
    }

def get_header_size():
    return 18

def fragment_IP_packet(IP_packet, MTU):
    header_size = get_header_size()
    packet_size = len(IP_packet)

    if packet_size <= MTU:
        return [IP_packet]

    parsed = parse_packet(IP_packet)
    message_bytes = parsed['message'].encode('utf-8')
    total_message_size = len(message_bytes)

    max_data_per_fragment = MTU - header_size
    fragments = []
    current_offset = parsed['offset']

    for i in range(0, total_message_size, max_data_per_fragment):
        fragment_data = message_bytes[i:i + max_data_per_fragment]
        fragment_size = len(fragment_data)

        is_last_fragment = (i + max_data_per_fragment >= total_message_size)
        fragment_flag = 0 if is_last_fragment and parsed['flag'] == 0 else 1

        fragment = create_packet(
            parsed['ip'],
            parsed['port'],
            fragment_data.decode('utf-8'),
            parsed['ttl'],
            parsed['id'],
            current_offset,
            fragment_size,
            fragment_flag
        )
        fragments.append(fragment)
        current_offset += fragment_size

    return fragments

def reassemble_IP_packet(fragment_list):
    if len(fragment_list) == 0:
        return None

    if len(fragment_list) == 1:
        parsed = parse_packet(fragment_list[0])
        if parsed['offset'] == 0 and parsed['flag'] == 0:
            return fragment_list[0]
        else:
            return None

    parsed_fragments = [parse_packet(f) for f in fragment_list]
    parsed_fragments.sort(key=lambda x: x['offset'])

    has_last = any(f['flag'] == 0 for f in parsed_fragments)
    if not has_last:
        return None

    expected_offset = 0
    for frag in parsed_fragments:
        if frag['offset'] != expected_offset:
            return None
        expected_offset += frag['size']

    first_frag = parsed_fragments[0]
    if first_frag['offset'] != 0:
        return None

    last_frag = parsed_fragments[-1]
    if last_frag['flag'] != 0:
        return None

    full_message = ''.join(f['message'] for f in parsed_fragments)
    full_size = sum(f['size'] for f in parsed_fragments)

    reassembled = create_packet(
        first_frag['ip'],
        first_frag['port'],
        full_message,
        first_frag['ttl'],
        first_frag['id'],
        0,
        full_size,
        0
    )

    return reassembled
