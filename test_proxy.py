#!/usr/bin/env python3
import socket

# Simple test client that connects to the proxy
proxy_host = 'localhost'
proxy_port = 8000

# Create a GET request
request = "GET http://example.com/ HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"

try:
    # Connect to proxy
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((proxy_host, proxy_port))
    print(f"Connected to proxy at {proxy_host}:{proxy_port}")

    # Send request
    client.send(request.encode())
    print(f"Sent request:\n{request}")

    # Receive response
    response = b""
    while True:
        chunk = client.recv(4096)
        if not chunk:
            break
        response += chunk

    print(f"\nReceived response ({len(response)} bytes):")
    print(response.decode('utf-8', errors='ignore')[:500])

    client.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
