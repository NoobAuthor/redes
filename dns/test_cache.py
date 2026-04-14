#!/usr/bin/env python3
from dnslib import DNSRecord
from resolver import resolver, cache, query_history

def test_cache():
    print("="*60)
    print("TEST DEL CACHE")
    print("="*60)
    domains = ["example.com", "www.uchile.cl", "example.com", "google.com", "www.uchile.cl", "example.com", "facebook.com", "example.com"]
    print("\nRealizando consultas...")
    for i, domain in enumerate(domains, 1):
        print(f"\n{i}. Consultando: {domain}")
        query = DNSRecord.question(domain)
        response_bytes = resolver(query.pack())
        if response_bytes:
            response = DNSRecord.parse(response_bytes)
            if response.header.a > 0:
                for rr in response.rr:
                    print(f"   -> {rr.rdata}")
    print("\n" + "="*60)
    print("ESTADO DEL CACHE")
    print("="*60)
    print(f"\nTotal de consultas en historial: {len(query_history)}")
    print(f"Dominios en cache: {len(cache)}")
    print("\nContenido del cache (top 3 más frecuentes):")
    for domain, ip in cache.items():
        count = sum(1 for d, _ in query_history if d == domain)
        print(f"  {domain} -> {ip} (consultado {count} veces)")
    print("\n" + "="*60)
    print("VERIFICANDO USO DEL CACHE")
    print("="*60)
    print("\nConsultando nuevamente 'example.com' (debería usar cache):")
    query = DNSRecord.question("example.com")
    response_bytes = resolver(query.pack())
    print("  (Revise el debug output arriba - debe decir 'Respuesta obtenida del cache')")

if __name__ == "__main__":
    test_cache()
