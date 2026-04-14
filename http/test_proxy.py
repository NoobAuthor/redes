#!/usr/bin/env python3
import socket

PROXY_HOST = 'localhost'
PROXY_PORT = 8000
BUFFER_SIZE = 4096

request = "GET http://example.com/ HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((PROXY_HOST, PROXY_PORT))
    print(f"Connected to proxy at {PROXY_HOST}:{PROXY_PORT}")
    client.send(request.encode())
    print(f"Sent request:\n{request}")
    chunks = []
    while True:
        chunk = client.recv(BUFFER_SIZE)
        if not chunk:
            break
        chunks.append(chunk)
    response = b"".join(chunks)
    print(f"\nReceived response ({len(response)} bytes):")
    print(response.decode('utf-8', errors='ignore')[:500])
    client.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
