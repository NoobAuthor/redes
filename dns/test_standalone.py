#!/usr/bin/env python3
from dnslib import DNSRecord
from resolver import resolver, DEBUG

def test_domain(domain):
    print(f"\n{'='*60}")
    print(f"Probando: {domain}")
    print(f"{'='*60}")
    query = DNSRecord.question(domain)
    query_bytes = query.pack()
    response_bytes = resolver(query_bytes)
    if response_bytes:
        response = DNSRecord.parse(response_bytes)
        print(f"\nRespuesta para {domain}:")
        if response.header.a > 0:
            for rr in response.rr:
                print(f"  {rr.rname} -> {rr.rdata}")
        else:
            print("  No hay respuestas tipo A")
        return True
    else:
        print(f"  ERROR: No se pudo resolver {domain}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("TEST STANDALONE DEL RESOLVER DNS")
    print("="*60)
    print(f"DEBUG mode: {DEBUG}")
    tests = [("example.com", "Dominio simple"), ("www.uchile.cl", "Universidad de Chile"), ("eol.uchile.cl", "EOL UChile")]
    results = []
    for domain, description in tests:
        print(f"\n{description}:")
        success = test_domain(domain)
        results.append((domain, success))
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    for domain, success in results:
        status = "✅ OK" if success else "❌ FAIL"
        print(f"{status} - {domain}")
    print("="*60)
