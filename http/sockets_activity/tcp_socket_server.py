import socket
import json
import sys


def receive_http_message(sock, buff_size):
    """
    Recibe un mensaje HTTP completo manejando HEAD y BODY por separado.

    ¿Cómo sé si llegó el mensaje completo?
    - HEAD: Busco \r\n\r\n en los datos recibidos
    - BODY: Uso Content-Length para saber cuántos bytes debo recibir
    """
    full_message = b""

    # Recibir HEAD hasta encontrar \r\n\r\n
    while b"\r\n\r\n" not in full_message:
        chunk = sock.recv(buff_size)
        if not chunk:
            break
        full_message += chunk

    if b"\r\n\r\n" not in full_message:
        return full_message.decode('utf-8', errors='ignore')

    # Separar HEAD y BODY
    head, body = full_message.split(b"\r\n\r\n", 1)
    head_str = head.decode('utf-8', errors='ignore')

    # Buscar Content-Length en el HEAD
    content_length = 0
    for line in head_str.split('\r\n'):
        if line.lower().startswith('content-length:'):
            content_length = int(line.split(':', 1)[1].strip())
            break

    # Recibir el resto del BODY si falta
    while len(body) < content_length:
        chunk = sock.recv(buff_size)
        if not chunk:
            break
        body += chunk

    return (head + b"\r\n\r\n" + body).decode('utf-8', errors='ignore')


def parse_http(message):
    """Parsea un mensaje HTTP en sus componentes."""
    if "\r\n\r\n" not in message:
        return None

    head, body = message.split("\r\n\r\n", 1)
    lines = head.split("\r\n")
    start_line = lines[0].split()

    # Determinar si es request o response
    if "HTTP" in start_line[0]:  # Response
        data = {
            'type': 'response',
            'version': start_line[0],
            'status': start_line[1],
            'status_text': ' '.join(start_line[2:])
        }
    else:  # Request
        data = {
            'type': 'request',
            'method': start_line[0],
            'path': start_line[1],
            'version': start_line[2]
        }

    # Parsear headers
    data['headers'] = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            data['headers'][key.strip()] = value.strip()

    data['body'] = body
    return data


def create_http(data):
    """Crea un mensaje HTTP desde componentes parseados."""
    # Start line
    if data['type'] == 'request':
        message = f"{data['method']} {data['path']} {data['version']}\r\n"
    else:
        message = f"{data['version']} {data['status']} {data['status_text']}\r\n"

    # Headers
    for key, value in data['headers'].items():
        message += f"{key}: {value}\r\n"

    # Separador y body
    message += "\r\n" + data['body']
    return message


if __name__ == "__main__":
    # Cargar configuración
    config_file = sys.argv[1] if len(sys.argv) > 1 else "proxy_config.json"
    with open(config_file) as f:
        config = json.load(f)

    print(f"Proxy iniciado - Usuario: {config['user']}")
    print(f"Sitios bloqueados: {len(config['blocked'])}")
    print(f"Palabras prohibidas: {len(config['forbidden_words'])}\n")

    # Configuración del proxy
    buff_size = 4096  # Cambiar a 50 para probar con buffer pequeño
    proxy_addr = ('0.0.0.0', 8000)

    # Crear socket servidor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(proxy_addr)
    server.listen(5)

    print(f"Escuchando en {proxy_addr[0]}:{proxy_addr[1]}\n")

    while True:
        try:
            # Aceptar cliente
            client_sock, client_addr = server.accept()
            print(f"Cliente conectado: {client_addr}")

            # Recibir request del cliente
            request = receive_http_message(client_sock, buff_size)
            if not request:
                client_sock.close()
                continue

            # Parsear request
            req_data = parse_http(request)
            if not req_data:
                client_sock.close()
                continue

            print(f"Request: {req_data['method']} {req_data['path']}")

            # Construir URL completa para verificar bloqueo
            path = req_data['path']
            if path.startswith('http://'):
                full_url = path
            else:
                host = req_data['headers'].get('Host', '')
                full_url = f"http://{host}{path}"

            # Verificar si está bloqueado
            blocked = False
            for blocked_url in config['blocked']:
                if full_url.startswith(blocked_url):
                    blocked = True
                    break

            if blocked:
                # Retornar 403 Forbidden
                print(f"BLOQUEADO: {full_url}")
                html = """<!DOCTYPE html>
<html>
<head><title>403 Forbidden</title></head>
<body>
<h1>403 Forbidden</h1>
<p>Este sitio ha sido bloqueado.</p>
</body>
</html>"""
                response = f"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
                client_sock.send(response.encode())
                client_sock.close()
                continue

            # Extraer host y puerto del path o Host header
            if path.startswith('http://'):
                # Remover http://
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
                    target_port = 80

                req_data['path'] = new_path  # Actualizar a path relativo
            else:
                target_host = req_data['headers'].get('Host', 'example.com')
                if ':' in target_host:
                    target_host, port_str = target_host.split(':', 1)
                    target_port = int(port_str)
                else:
                    target_port = 80

            # Agregar header personalizado
            req_data['headers']['X-ElQuePregunta'] = config['user']

            # Conectar al servidor destino
            print(f"Conectando a {target_host}:{target_port}")
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.connect((target_host, target_port))

            # Enviar request modificada
            modified_request = create_http(req_data)
            target_sock.send(modified_request.encode())

            # Recibir response del servidor
            response = receive_http_message(target_sock, buff_size)
            target_sock.close()

            if not response:
                client_sock.close()
                continue

            # Parsear response
            resp_data = parse_http(response)
            if not resp_data:
                client_sock.send(response.encode())
                client_sock.close()
                continue

            # Reemplazar palabras prohibidas en el body
            if resp_data['body']:
                original_body = resp_data['body']
                modified_body = original_body

                for word_dict in config['forbidden_words']:
                    for original, replacement in word_dict.items():
                        modified_body = modified_body.replace(original, replacement)

                resp_data['body'] = modified_body

                # Actualizar Content-Length si cambió el tamaño
                if len(modified_body) != len(original_body):
                    resp_data['headers']['Content-Length'] = str(len(modified_body))

            # Enviar response al cliente
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
