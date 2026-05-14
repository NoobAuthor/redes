#!/usr/bin/env python3
import subprocess
import time
import os
import signal

print("=" * 60)
print("TEST COMPLETO: Go-Back-N con Control de Congestión")
print("=" * 60)
print()

print("Test 1: CongestionControl")
print("-" * 60)
result = subprocess.run(["python3", "CongestionControl_test.py"], capture_output=True, text=True)
if result.returncode == 0:
    print("✓ CongestionControl tests PASARON")
else:
    print("✗ CongestionControl tests FALLARON")
    print(result.stdout)
    print(result.stderr)
print()

print("Test 2: Go-Back-N sin pérdidas")
print("-" * 60)

with open("test_small.txt", "w") as f:
    f.write("Hola mundo! " * 100)

servidor = subprocess.Popen(["python3", "servidor_gbn.py"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

time.sleep(1)

cliente = subprocess.run(["python3", "cliente_gbn.py", "test_small.txt"],
                        capture_output=True, text=True, timeout=10)

time.sleep(1)
servidor.send_signal(signal.SIGTERM)
servidor.wait(timeout=2)

if os.path.exists("recibido_gbn.txt"):
    with open("test_small.txt", "rb") as f:
        original = f.read()
    with open("recibido_gbn.txt", "rb") as f:
        recibido = f.read()

    if original == recibido:
        print("✓ Archivo transmitido correctamente")
        print(f"  Original: {len(original)} bytes")
        print(f"  Recibido: {len(recibido)} bytes")
    else:
        print("✗ Archivo corrupto")
        print(f"  Original: {len(original)} bytes")
        print(f"  Recibido: {len(recibido)} bytes")
else:
    print("✗ Archivo no recibido")

print()

print("=" * 60)
print("Tests completados")
print("=" * 60)
print()
print("Para ejecutar manualmente:")
print("  Terminal 1: python3 servidor_gbn.py")
print("  Terminal 2: python3 cliente_gbn.py test_100kb.bin")
print("  Terminal 2 (debug): python3 cliente_gbn.py test_100kb.bin debug")
