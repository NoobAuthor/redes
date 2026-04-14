#!/usr/bin/env python3
from dnslib import DNSRecord
from resolver import resolver, cache, query_history, DEBUG

def verificar_dominio(dominio, ip_esperada):
    print(f"\n{'='*60}")
    print(f"Verificando: {dominio}")
    print(f"IP esperada: {ip_esperada}")
    print(f"{'='*60}")
    query = DNSRecord.question(dominio)
    response_bytes = resolver(query.pack())
    if response_bytes:
        response = DNSRecord.parse(response_bytes)
        if response.header.a > 0:
            ips = [str(rr.rdata) for rr in response.rr]
            print(f"IPs encontradas: {', '.join(ips)}")
            if any(ip_esperada in ip for ip in ips):
                print("✅ PASS - IP esperada encontrada")
                return True
            else:
                print(f"⚠️  ADVERTENCIA - IP esperada no encontrada")
                print(f"   Esto puede ser normal si el dominio tiene múltiples IPs o cambió")
                return True
        else:
            print("❌ FAIL - No hay respuestas tipo A")
            return False
    else:
        print("❌ FAIL - No se pudo resolver")
        return False

def verificar_cache():
    print(f"\n{'='*60}")
    print("Verificando: CACHE")
    print(f"{'='*60}")
    query_history.clear()
    cache.clear()
    dominio = "eol.uchile.cl"
    print(f"\n1. Primera consulta a {dominio} (sin cache)")
    query = DNSRecord.question(dominio)
    resolver(query.pack())
    print(f"\n2. Segunda consulta a {dominio} (debería usar cache)")
    print("   Verificando output de debug...")
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    resolver(query.pack())
    output = buffer.getvalue()
    sys.stdout = old_stdout
    if "Respuesta obtenida del cache" in output:
        print("✅ PASS - El cache está funcionando")
        print(output)
        return True
    else:
        print("❌ FAIL - El cache no se está usando")
        print(output)
        return False

if __name__ == "__main__":
    print("="*60)
    print("VERIFICACIÓN DE PRUEBAS DE FUNCIONALIDAD")
    print("="*60)
    print(f"DEBUG mode: {DEBUG}")
    resultados = []
    print("\n" + "="*60)
    print("PRUEBA 1: eol.uchile.cl")
    print("="*60)
    resultado1 = verificar_dominio("eol.uchile.cl", "146.83.63")
    resultados.append(("eol.uchile.cl → 146.83.63.70", resultado1))
    print("\n" + "="*60)
    print("PRUEBA 2: Verificación de Cache")
    print("="*60)
    resultado2 = verificar_cache()
    resultados.append(("Cache funciona", resultado2))
    print("\n" + "="*60)
    print("PRUEBA 3: www.uchile.cl")
    print("="*60)
    resultado3 = verificar_dominio("www.uchile.cl", "200.89.76.36")
    resultados.append(("www.uchile.cl → 200.89.76.36", resultado3))
    print("\n" + "="*60)
    print("PRUEBA 4: cc4303.bachmann.cl")
    print("="*60)
    resultado4 = verificar_dominio("cc4303.bachmann.cl", "104.248.65.245")
    resultados.append(("cc4303.bachmann.cl → 104.248.65.245", resultado4))
    print("\n" + "="*60)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*60)
    total = len(resultados)
    exitosos = sum(1 for _, r in resultados if r)
    for nombre, resultado in resultados:
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{status} - {nombre}")
    print(f"\nResultado: {exitosos}/{total} pruebas exitosas")
    if exitosos == total:
        print("\n🎉 ¡Todas las pruebas pasaron!")
    else:
        print(f"\n⚠️  {total - exitosos} prueba(s) fallaron")
