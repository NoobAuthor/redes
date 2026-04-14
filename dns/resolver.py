#!/usr/bin/env python3
import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

from collections import Counter

ROOT_DNS_SERVER = "192.33.4.12"
DNS_PORT = 53
RESOLVER_PORT = 8000
DEBUG = True
BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 5
RECORD_TYPE_A = 'A'
RECORD_TYPE_NS = 'NS'
MAX_HISTORY = 20
CACHE_SIZE = 3

query_history = []
cache = {}


def print_debug(message):
    if DEBUG:
        print(f"(debug) {message}")


def update_cache(domain, ip):
    global query_history, cache
    query_history.append((domain, ip))
    if len(query_history) > MAX_HISTORY:
        query_history.pop(0)
    domain_count = Counter(d for d, _ in query_history)
    domain_ips = {}
    for d, ip_addr in reversed(query_history):
        if d not in domain_ips:
            domain_ips[d] = ip_addr
    top_domains = [d for d, _ in domain_count.most_common(CACHE_SIZE)]
    cache = {d: domain_ips[d] for d in top_domains if d in domain_ips}


def check_cache(domain):
    domain_str = str(domain).rstrip('.')
    if domain_str in cache:
        print_debug(f"Respuesta obtenida del cache")
        return cache[domain_str]
    return None


def send_dns_query(query_name, address, port=DNS_PORT):
    q = DNSRecord.question(query_name)
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(SOCKET_TIMEOUT)
    try:
        sock.sendto(bytes(q.pack()), server_address)
        data, _ = sock.recvfrom(BUFFER_SIZE)
        d = DNSRecord.parse(data)
        return d
    except socket.timeout:
        print_debug(f"Timeout al consultar {address}")
        return None
    finally:
        sock.close()


def resolver(mensaje_consulta):
    query = DNSRecord.parse(mensaje_consulta)
    qname = query.q.qname
    domain_name = str(qname).rstrip('.')
    print_debug(f"Resolviendo dominio: {domain_name}")
    cached_ip = check_cache(qname)
    if cached_ip:
        response = query.reply()
        response.add_answer(*dnslib.RR.fromZone(f"{qname} A {cached_ip}"))
        return response.pack()
    current_server = ROOT_DNS_SERVER
    current_name = "."
    while True:
        print_debug(f"Consultando '{domain_name}' a '{current_name}' con dirección IP '{current_server}'")
        response = send_dns_query(str(qname), current_server)
        if response is None:
            return None
        if response.header.a > 0:
            for rr in response.rr:
                if QTYPE.get(rr.rtype) == RECORD_TYPE_A:
                    ip_address = str(rr.rdata)
                    print_debug(f"Respuesta encontrada: {ip_address}")
                    update_cache(domain_name, ip_address)
                    return response.pack()
        if response.header.auth > 0:
            additional_ips = {}
            if response.header.ar > 0:
                for ar_rr in response.ar:
                    if QTYPE.get(ar_rr.rtype) == RECORD_TYPE_A:
                        ar_name = str(ar_rr.rname).rstrip('.')
                        additional_ips[ar_name] = str(ar_rr.rdata)
            for auth_rr in response.auth:
                if QTYPE.get(auth_rr.rtype) == RECORD_TYPE_NS:
                    ns_domain = str(auth_rr.rdata)
                    current_name = ns_domain.rstrip('.')
                    if current_name in additional_ips:
                        current_server = additional_ips[current_name]
                    else:
                        print_debug(f"Resolviendo NS: {current_name}")
                        ns_query = DNSRecord.question(ns_domain)
                        ns_response_data = resolver(ns_query.pack())
                        if ns_response_data:
                            ns_response = DNSRecord.parse(ns_response_data)
                            if ns_response.header.a > 0:
                                for rr in ns_response.rr:
                                    if QTYPE.get(rr.rtype) == RECORD_TYPE_A:
                                        current_server = str(rr.rdata)
                                        break
                                else:
                                    print_debug(f"No se pudo resolver el NS: {current_name}")
                                    return None
                            else:
                                print_debug(f"No se pudo resolver el NS: {current_name}")
                                return None
                        else:
                            print_debug(f"No se pudo resolver el NS: {current_name}")
                            return None
                    break
            else:
                return None
        else:
            return None


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', RESOLVER_PORT)
    sock.bind(server_address)
    print(f"Resolver DNS escuchando en el puerto {RESOLVER_PORT}...")
    print(f"DEBUG mode: {DEBUG}")
    while True:
        try:
            data, client_address = sock.recvfrom(BUFFER_SIZE)
            print(f"\n{'='*60}")
            print(f"Consulta recibida desde {client_address}")
            response = resolver(data)
            if response:
                sock.sendto(response, client_address)
                print(f"Respuesta enviada a {client_address}")
            else:
                print(f"No se pudo resolver la consulta")
        except KeyboardInterrupt:
            print("\nCerrando resolver...")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    sock.close()


if __name__ == "__main__":
    main()
