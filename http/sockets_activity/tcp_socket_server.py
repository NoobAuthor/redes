import socket
import json
import sys

BUFFER_SIZE = 4096
PROXY_PORT = 8000
HTTP_PORT = 80
HTTP_SEPARATOR = b"\r\n\r\n"
HTTP_VERSION = "HTTP/1.1"

def receive_http_message(sock, buff_size):
    chunks = []
    while HTTP_SEPARATOR not in b"".join(chunks):
        chunk = sock.recv(buff_size)
        if not chunk:
            break
        chunks.append(chunk)
    full_message = b"".join(chunks)
    if HTTP_SEPARATOR not in full_message:
        return full_message.decode('utf-8', errors='ignore')
    head, body = full_message.split(HTTP_SEPARATOR, 1)
    head_str = head.decode('utf-8', errors='ignore')
    content_length = 0
    for line in head_str.split('\r\n'):
        if line.lower().startswith('content-length:'):
            content_length = int(line.split(':', 1)[1].strip())
            break
    body_chunks = [body]
    while sum(len(c) for c in body_chunks) < content_length:
        chunk = sock.recv(buff_size)
        if not chunk:
            break
        body_chunks.append(chunk)
    body = b"".join(body_chunks)
    return (head + HTTP_SEPARATOR + body).decode('utf-8', errors='ignore')

def parse_http(message):
    if "\r\n\r\n" not in message:
        return None
    head, body = message.split("\r\n\r\n", 1)
    lines = head.split("\r\n")
    start_line = lines[0].split()
    if "HTTP" in start_line[0]:
        data = {'type': 'response', 'version': start_line[0], 'status': start_line[1], 'status_text': ' '.join(start_line[2:])}
    else:
        data = {'type': 'request', 'method': start_line[0], 'path': start_line[1], 'version': start_line[2]}
    data['headers'] = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            data['headers'][key.strip()] = value.strip()
    data['body'] = body
    return data

def create_http(data):
    parts = []
    if data['type'] == 'request':
        parts.append(f"{data['method']} {data['path']} {data['version']}\r\n")
    else:
        parts.append(f"{data['version']} {data['status']} {data['status_text']}\r\n")
    for key, value in data['headers'].items():
        parts.append(f"{key}: {value}\r\n")
    parts.append("\r\n")
    parts.append(data['body'])
    return "".join(parts)


if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "proxy_config.json"
    with open(config_file) as f:
        config = json.load(f)
    print(f"Proxy iniciado - Usuario: {config['user']}")
    print(f"Sitios bloqueados: {len(config['blocked'])}")
    print(f"Palabras prohibidas: {len(config['forbidden_words'])}\n")
    buff_size = BUFFER_SIZE
    proxy_addr = ('0.0.0.0', PROXY_PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(proxy_addr)
    server.listen(5)
    print(f"Escuchando en {proxy_addr[0]}:{proxy_addr[1]}\n")
    while True:
        try:
            client_sock, client_addr = server.accept()
            print(f"Cliente conectado: {client_addr}")
            request = receive_http_message(client_sock, buff_size)
            if not request:
                client_sock.close()
                continue
            req_data = parse_http(request)
            if not req_data:
                client_sock.close()
                continue
            print(f"Request: {req_data['method']} {req_data['path']}")
            path = req_data['path']
            if path.startswith('http://'):
                full_url = path
            else:
                host = req_data['headers'].get('Host', '')
                full_url = f"http://{host}{path}"
            blocked = False
            for blocked_url in config['blocked']:
                if full_url.startswith(blocked_url):
                    blocked = True
                    break
            if blocked:
                print(f"BLOQUEADO: {full_url}")
                html = """<!DOCTYPE html>
<html>
<head><title>403 Forbidden</title></head>
<body>
<h1>403 Forbidden</h1>
<p>Este sitio ha sido bloqueado.</p>
</body>
</html>"""
                response = f"{HTTP_VERSION} 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
                client_sock.send(response.encode())
                client_sock.close()
                continue
            if path.startswith('http://'):
                path_clean = path[7:]
                if '/' in path_clean:
                    host_port, new_path = path_clean.split('/', 1)
                    new_path = '/' + new_path
                else:
                    host_port = path_clean
                    new_path = '/'
                if ':' in host_port:
                    target_host, target_port = host_port.split(':', 1)
                    target_port = int(target_port)
                else:
                    target_host = host_port
                    target_port = HTTP_PORT
                req_data['path'] = new_path
            else:
                target_host = req_data['headers'].get('Host', 'example.com')
                if ':' in target_host:
                    target_host, port_str = target_host.split(':', 1)
                    target_port = int(port_str)
                else:
                    target_port = HTTP_PORT
            req_data['headers']['X-ElQuePregunta'] = config['user']
            print(f"Conectando a {target_host}:{target_port}")
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.connect((target_host, target_port))
            modified_request = create_http(req_data)
            target_sock.send(modified_request.encode())
            response = receive_http_message(target_sock, buff_size)
            target_sock.close()
            if not response:
                client_sock.close()
                continue
            resp_data = parse_http(response)
            if not resp_data:
                client_sock.send(response.encode())
                client_sock.close()
                continue
            if resp_data['body']:
                modified_body = resp_data['body']
                for word_dict in config['forbidden_words']:
                    for original, replacement in word_dict.items():
                        modified_body = modified_body.replace(original, replacement)
                if modified_body != resp_data['body']:
                    resp_data['body'] = modified_body
                    resp_data['headers']['Content-Length'] = str(len(modified_body.encode('utf-8')))
            final_response = create_http(resp_data)
            client_sock.send(final_response.encode())
            client_sock.close()
            print(f"Response enviada ({len(final_response)} bytes)\n")
        except KeyboardInterrupt:
            print("\nProxy detenido")
            break
        except Exception as e:
            print(f"Error: {e}")
            try:
                client_sock.close()
            except:
                pass
    server.close()
