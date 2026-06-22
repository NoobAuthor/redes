import sys
import socket
from packet_utils import parse_packet, create_packet, ip_to_bytes

round_robin_state = {}

def load_routes(routes_file_name):
    routes = {}
    with open(routes_file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) == 5:
                    port_start = int(parts[1])
                    port_end = int(parts[2])
                    next_hop_ip = parts[3]
                    next_hop_port = int(parts[4])

                    port_range = (port_start, port_end)
                    if port_range not in routes:
                        routes[port_range] = []
                    routes[port_range].append((next_hop_ip, next_hop_port))
    return routes

def check_routes(routes, destination_address):
    dest_ip, dest_port = destination_address

    matching_routes = []
    for (port_start, port_end), next_hops in routes.items():
        if port_start <= dest_port <= port_end:
            matching_routes.extend(next_hops)

    if not matching_routes:
        return None

    route_key = (dest_ip, dest_port)
    idx = round_robin_state.get(route_key, 0) % len(matching_routes)
    round_robin_state[route_key] = idx + 1

    return matching_routes[idx]

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 router.py router_IP router_puerto router_rutas.txt")
        sys.exit(1)

    router_ip = sys.argv[1]
    router_port = int(sys.argv[2])
    routes_file = sys.argv[3]

    routes = load_routes(routes_file)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((router_ip, router_port))

    print(f"Router listening on {router_ip}:{router_port}", flush=True)

    while True:
        data, addr = sock.recvfrom(4096)

        parsed = parse_packet(data)
        dest = (parsed['ip'], parsed['port'])

        if parsed['ttl'] == 0:
            print(f"Se recibió paquete {parsed['ip']};{parsed['port']};{parsed['ttl']};{parsed['message']} con TTL 0", flush=True)
            continue

        if dest == (router_ip, router_port):
            print(parsed['message'], flush=True)
        else:
            next_hop = check_routes(routes, dest)

            if next_hop is None:
                print(f"No hay rutas hacia {dest} para paquete {parsed['ip']};{parsed['port']};{parsed['ttl']};{parsed['message']}", flush=True)
            else:
                print(f"redirigiendo paquete {parsed['ip']};{parsed['port']};{parsed['ttl']};{parsed['message']} con destino final {dest} desde {router_ip}:{router_port} hacia {next_hop[0]}:{next_hop[1]}", flush=True)

                parsed['ttl'] -= 1
                forwarded_packet = create_packet(parsed['ip'], parsed['port'], parsed['message'], parsed['ttl'])
                sock.sendto(forwarded_packet, next_hop)

if __name__ == "__main__":
    main()
