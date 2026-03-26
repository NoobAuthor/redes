# HTTP Proxy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an HTTP proxy server that filters content by blocking forbidden sites and replacing forbidden words, while handling large HTTP messages with small buffers.

**Architecture:** Client-Proxy-Server architecture where proxy receives HTTP requests from clients, checks blocking rules, forwards approved requests to target servers, receives responses, performs word replacement, and sends modified responses back to clients. Uses JSON configuration for blocking rules and word replacements.

**Tech Stack:** Python 3, sockets, JSON

---

## File Structure

- **Create:** `proxy_config.json` - Configuration file with blocked sites and forbidden words
- **Modify:** `sockets_activity/tcp_socket_server.py` - Complete proxy implementation
- **Files to reference:** Activity PDF for requirements and test scenarios

## Task 1: Fix Existing HTTP Message Functions

**Files:**
- Modify: `sockets_activity/tcp_socket_server.py:160-176`

- [ ] **Step 1: Fix create_HTTP_message spacing bug**

Fix lines 164 and 166 - add spaces between HTTP message components:

```python
def create_HTTP_message(http_parsed_message):
    message = ""
    # Start line
    if 'method' in http_parsed_message:
        # Fix: add spaces between components
        message = f"{http_parsed_message['method']} {http_parsed_message['path']} {http_parsed_message['version']}\r\n"
    else:
        # Fix: add spaces between components
        message = f"{http_parsed_message['version']} {http_parsed_message['status_code']} {http_parsed_message['status_text']}\r\n"

    # Fix: 'header' -> 'headers' (typo on line 168)
    for header_name, header_value in http_parsed_message['headers'].items():
         message += f"{header_name}: {header_value}\r\n"

    message += "\r\n"

    if http_parsed_message.get('body'):
        message += http_parsed_message['body']

    return message
```

- [ ] **Step 2: Test the fix manually**

Add test code at the bottom of the file:

```python
# Test the functions
if __name__ == "__main__":
    test_request = "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
    parsed = parse_HTTP_message(test_request)
    print("Parsed:", parsed)
    recreated = create_HTTP_message(parsed)
    print("Recreated:", recreated)
    assert test_request == recreated, "Messages don't match!"
    print("✓ Test passed")
```

Run: `python3 sockets_activity/tcp_socket_server.py`
Expected: "✓ Test passed"

- [ ] **Step 3: Remove test code**

Remove the test code added in step 2, keeping only the original if __name__ == "__main__" block.

- [ ] **Step 4: Commit the fixes**

```bash
git add sockets_activity/tcp_socket_server.py
git commit -m "fix: correct spacing and typo in create_HTTP_message"
```

## Task 2: Create JSON Configuration File

**Files:**
- Create: `proxy_config.json`

- [ ] **Step 1: Create JSON configuration file**

Create the configuration file with blocked sites and forbidden words:

```json
{
  "user": "tu-email@ejemplo.com",
  "blocked": [
    "http://www.dcc.uchile.cl/",
    "http://cc4303.bachmann.cl/secret"
  ],
  "forbidden_words": [
    {"proxy": "[REDACTED]"},
    {"DCC": "[FORBIDDEN]"},
    {"biblioteca": "[???]"}
  ]
}
```

- [ ] **Step 2: Test JSON can be loaded**

Add temporary test code:

```python
import json

with open("proxy_config.json") as f:
    config = json.load(f)
    print("Config loaded:", config)
    print("Blocked sites:", config['blocked'])
    print("Forbidden words:", config['forbidden_words'])
```

Run: `python3 -c "import json; f=open('proxy_config.json'); print(json.load(f))"`
Expected: See the config printed

- [ ] **Step 3: Commit the config file**

```bash
git add proxy_config.json
git commit -m "feat: add proxy configuration file"
```

## Task 3: Implement HTTP Message Receiving with Content-Length

**Files:**
- Modify: `sockets_activity/tcp_socket_server.py:8-42`

- [ ] **Step 1: Create receive_http_message function**

Replace the old receive_full_message function with HTTP-specific receiving:

```python
def receive_http_message(connection_socket, buff_size):
    """
    Receives a complete HTTP message handling HEAD and BODY separately.

    How it works:
    1. Receive until we find \r\n\r\n (end of HEAD)
    2. Parse Content-Length from HEAD
    3. Continue receiving until we have all BODY bytes

    Args:
        connection_socket: Socket to receive from
        buff_size: Size of receive buffer

    Returns:
        Complete HTTP message as string
    """
    # Step 1: Receive HEAD
    full_message = b""
    head_end = b"\r\n\r\n"

    # Keep receiving until we have the complete HEAD
    while head_end not in full_message:
        chunk = connection_socket.recv(buff_size)
        if not chunk:
            break
        full_message += chunk

    # If no head_end found, return what we have
    if head_end not in full_message:
        return full_message.decode('utf-8', errors='ignore')

    # Step 2: Split HEAD and check Content-Length
    head, body_so_far = full_message.split(head_end, 1)
    head_str = head.decode('utf-8', errors='ignore')

    # Parse Content-Length
    content_length = 0
    for line in head_str.split('\r\n'):
        if line.lower().startswith('content-length:'):
            content_length = int(line.split(':', 1)[1].strip())
            break

    # Step 3: Receive remaining BODY bytes
    while len(body_so_far) < content_length:
        chunk = connection_socket.recv(buff_size)
        if not chunk:
            break
        body_so_far += chunk

    # Reconstruct and return complete message
    complete_message = head + head_end + body_so_far
    return complete_message.decode('utf-8', errors='ignore')
```

- [ ] **Step 2: Remove old helper functions**

Delete the functions `contains_end_of_message` and `remove_end_of_message` (lines 36-42) as they are no longer needed.

- [ ] **Step 3: Commit the new receive function**

```bash
git add sockets_activity/tcp_socket_server.py
git commit -m "feat: implement HTTP-aware message receiving with Content-Length"
```

## Task 4: Implement Core Proxy Functions

**Files:**
- Modify: `sockets_activity/tcp_socket_server.py` (add after parse/create functions)

- [ ] **Step 1: Add load_config function**

```python
def load_config(config_path):
    """Load proxy configuration from JSON file."""
    import json
    with open(config_path, 'r') as f:
        return json.load(f)
```

- [ ] **Step 2: Add is_blocked function**

```python
def is_blocked(url, blocked_list):
    """Check if URL is in the blocked list."""
    for blocked_url in blocked_list:
        if url.startswith(blocked_url):
            return True
    return False
```

- [ ] **Step 3: Add create_403_response function**

```python
def create_403_response():
    """Create a 403 Forbidden response with HTML."""
    html_body = """<!DOCTYPE html>
<html>
<head><title>403 Forbidden</title></head>
<body>
<h1>403 Forbidden</h1>
<p>This site has been blocked.</p>
<img src="blocked_cat.jpg" alt="Blocked" style="max-width: 400px;">
</body>
</html>"""

    response = {
        'version': 'HTTP/1.1',
        'status_code': '403',
        'status_text': 'Forbidden',
        'headers': {
            'Content-Type': 'text/html',
            'Content-Length': str(len(html_body))
        },
        'body': html_body
    }
    return create_HTTP_message(response)
```

- [ ] **Step 4: Add replace_forbidden_words function**

```python
def replace_forbidden_words(text, forbidden_words):
    """Replace forbidden words in text with their replacements."""
    for word_dict in forbidden_words:
        for original, replacement in word_dict.items():
            text = text.replace(original, replacement)
    return text
```

- [ ] **Step 5: Add extract_host_and_port function**

```python
def extract_host_and_port(request_path):
    """
    Extract host and port from request path.
    Examples:
        http://example.com/path -> (example.com, 80, /path)
        http://example.com:8080/path -> (example.com, 8080, /path)
    """
    # Remove http:// prefix
    if request_path.startswith('http://'):
        request_path = request_path[7:]
    elif request_path.startswith('https://'):
        request_path = request_path[8:]

    # Split host and path
    if '/' in request_path:
        host_port, path = request_path.split('/', 1)
        path = '/' + path
    else:
        host_port = request_path
        path = '/'

    # Split host and port
    if ':' in host_port:
        host, port = host_port.split(':', 1)
        port = int(port)
    else:
        host = host_port
        port = 80

    return host, port, path
```

- [ ] **Step 6: Commit proxy helper functions**

```bash
git add sockets_activity/tcp_socket_server.py
git commit -m "feat: add proxy helper functions"
```

## Task 5: Implement Main Proxy Logic

**Files:**
- Modify: `sockets_activity/tcp_socket_server.py` (replace __main__ section)

- [ ] **Step 1: Add handle_client_request function**

```python
def handle_client_request(client_socket, config, buff_size):
    """
    Handle a single client request through the proxy.

    Flow:
    1. Receive request from client
    2. Parse request
    3. Check if URL is blocked
    4. If blocked, return 403
    5. If not blocked, forward to target server
    6. Receive response from server
    7. Replace forbidden words
    8. Add custom header
    9. Send response to client
    """
    try:
        # Step 1: Receive request from client
        request_message = receive_http_message(client_socket, buff_size)
        if not request_message:
            return

        print(f"\n>>> Received request:\n{request_message[:200]}...\n")

        # Step 2: Parse request
        parsed_request = parse_HTTP_message(request_message)
        if not parsed_request:
            return

        # Get full URL from request path or Host header
        request_path = parsed_request['path']

        # Build full URL for blocking check
        if request_path.startswith('http://'):
            full_url = request_path
        else:
            host = parsed_request['headers'].get('Host', '')
            full_url = f"http://{host}{request_path}"

        # Step 3: Check if blocked
        if is_blocked(full_url, config['blocked']):
            print(f"!!! BLOCKED: {full_url}")
            response = create_403_response()
            client_socket.send(response.encode())
            return

        # Step 4: Extract host and port
        if request_path.startswith('http://'):
            host, port, path = extract_host_and_port(request_path)
            parsed_request['path'] = path  # Update path to relative
        else:
            host = parsed_request['headers'].get('Host', '')
            if ':' in host:
                host, port = host.split(':', 1)
                port = int(port)
            else:
                port = 80
            path = request_path

        print(f">>> Forwarding to: {host}:{port}{path}")

        # Step 5: Add custom header to request
        parsed_request['headers']['X-ElQuePregunta'] = config['user']

        # Step 6: Forward request to target server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, port))

        modified_request = create_HTTP_message(parsed_request)
        server_socket.send(modified_request.encode())

        # Step 7: Receive response from server
        response_message = receive_http_message(server_socket, buff_size)
        server_socket.close()

        if not response_message:
            return

        print(f"<<< Received response: {len(response_message)} bytes")

        # Step 8: Parse and modify response
        parsed_response = parse_HTTP_message(response_message)
        if not parsed_response:
            client_socket.send(response_message.encode())
            return

        # Step 9: Replace forbidden words in body
        if parsed_response.get('body'):
            original_body = parsed_response['body']
            modified_body = replace_forbidden_words(original_body, config['forbidden_words'])
            parsed_response['body'] = modified_body

            # Update Content-Length if body changed
            if len(modified_body) != len(original_body):
                parsed_response['headers']['Content-Length'] = str(len(modified_body))

        # Step 10: Send response to client
        final_response = create_HTTP_message(parsed_response)
        client_socket.send(final_response.encode())

        print(f"<<< Sent response to client: {len(final_response)} bytes\n")

    except Exception as e:
        print(f"Error handling request: {e}")
        import traceback
        traceback.print_exc()
```

- [ ] **Step 2: Update main execution block**

Replace the existing `if __name__ == "__main__":` block:

```python
if __name__ == "__main__":
    import sys

    # Load configuration
    config_path = sys.argv[1] if len(sys.argv) > 1 else "proxy_config.json"
    config = load_config(config_path)

    print(f"Loaded config from: {config_path}")
    print(f"User: {config['user']}")
    print(f"Blocked sites: {len(config['blocked'])}")
    print(f"Forbidden words: {len(config['forbidden_words'])}")

    # Proxy configuration
    buff_size = 4096  # Can be changed to test with smaller buffers
    proxy_address = ('0.0.0.0', 8000)  # Listen on all interfaces

    print(f'\n=== HTTP Proxy Server ===')
    print(f'Listening on {proxy_address[0]}:{proxy_address[1]}')
    print(f'Buffer size: {buff_size} bytes')
    print(f'===========================\n')

    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(proxy_address)
    server_socket.listen(5)

    print('Waiting for clients...\n')

    # Main server loop
    while True:
        try:
            # Accept client connection
            client_socket, client_address = server_socket.accept()
            print(f'\n>>> New connection from {client_address}')

            # Handle the request
            handle_client_request(client_socket, config, buff_size)

            # Close client connection
            client_socket.close()
            print(f'>>> Connection closed: {client_address}')

        except KeyboardInterrupt:
            print('\n\nShutting down proxy server...')
            break
        except Exception as e:
            print(f'Error in main loop: {e}')
            import traceback
            traceback.print_exc()

    server_socket.close()
    print('Proxy server stopped.')
```

- [ ] **Step 3: Commit main proxy logic**

```bash
git add sockets_activity/tcp_socket_server.py
git commit -m "feat: implement main proxy logic with request handling"
```

## Task 6: Test Basic Proxy Functionality

**Files:**
- Modify: `sockets_activity/tcp_socket_server.py` (testing only)

- [ ] **Step 1: Test proxy with example.com**

Run proxy:
```bash
python3 sockets_activity/tcp_socket_server.py proxy_config.json
```

In another terminal, test with curl:
```bash
curl http://example.com -x localhost:8000 -i
```

Expected: See example.com HTML response

- [ ] **Step 2: Test blocking functionality**

Test blocked site:
```bash
curl http://cc4303.bachmann.cl/secret -x localhost:8000 -i
```

Expected: HTTP 403 Forbidden response with HTML

- [ ] **Step 3: Test custom header**

Test that X-ElQuePregunta is added:
```bash
curl http://cc4303.bachmann.cl/ -x localhost:8000 -i
```

Expected: Response should show modified content (welcome message changes)

- [ ] **Step 4: Document test results**

Create `test_results.txt` with observations from tests.

## Task 7: Test Word Replacement

**Files:**
- Test only

- [ ] **Step 1: Test word replacement on replace endpoint**

```bash
curl http://cc4303.bachmann.cl/replace -x localhost:8000
```

Expected: Words like "proxy", "DCC", "biblioteca" should be replaced with [REDACTED], [FORBIDDEN], [???]

- [ ] **Step 2: Verify Content-Length is updated**

Check that the Content-Length header matches the new body length after replacement:

```bash
curl http://cc4303.bachmann.cl/replace -x localhost:8000 -i | head -20
```

Expected: Content-Length should match actual body length

- [ ] **Step 3: Document word replacement tests**

Add observations to `test_results.txt`.

## Task 8: Test with Small Buffer Sizes

**Files:**
- Modify: `sockets_activity/tcp_socket_server.py:318` (buff_size variable)

- [ ] **Step 1: Test with buffer smaller than message but larger than HEAD**

Edit line 318, change buff_size to 512:
```python
buff_size = 512  # Smaller than message, larger than HEAD
```

Restart proxy and test:
```bash
curl http://cc4303.bachmann.cl/ -x localhost:8000 -i
```

Expected: Still works correctly

- [ ] **Step 2: Test with buffer smaller than HEAD**

Change buff_size to 50:
```python
buff_size = 50  # Smaller than HEAD
```

Restart proxy and test:
```bash
curl http://cc4303.bachmann.cl/ -x localhost:8000 -i
```

Expected: Still works correctly (receives HEAD in multiple chunks)

- [ ] **Step 3: Test with very small buffer**

Change buff_size to 16:
```python
buff_size = 16  # Very small
```

Restart and test multiple endpoints:
```bash
curl http://example.com -x localhost:8000 -i
curl http://cc4303.bachmann.cl/replace -x localhost:8000 -i
```

Expected: All still work correctly

- [ ] **Step 4: Restore default buffer size**

Change back to reasonable default:
```python
buff_size = 4096  # Default
```

- [ ] **Step 5: Document buffer size tests**

Add observations to `test_results.txt` explaining:
- How we know HEAD is complete: Look for \r\n\r\n
- How we know BODY is complete: Use Content-Length header
- What happens if headers don't fit: Keep receiving until \r\n\r\n found
- What happens if body doesn't fit: Keep receiving until Content-Length bytes received

- [ ] **Step 6: Commit test documentation**

```bash
git add test_results.txt
git commit -m "docs: add proxy testing results and buffer handling explanation"
```

## Task 9: Create Test with Browser

**Files:**
- Documentation only

- [ ] **Step 1: Test with browser - unblocked site**

1. Start proxy: `python3 sockets_activity/tcp_socket_server.py`
2. Configure browser to use proxy: localhost:8000
3. Visit: http://cc4303.bachmann.cl/
4. Observe: Page loads, content modified (welcome message changes)

- [ ] **Step 2: Test with browser - blocked site**

Visit: http://cc4303.bachmann.cl/secret

Observe: 403 Forbidden page displayed

- [ ] **Step 3: Test with browser - word replacement**

Visit: http://cc4303.bachmann.cl/replace

Observe: Words are replaced ([REDACTED], [FORBIDDEN], [???])

- [ ] **Step 4: Document browser testing**

Add browser test observations to `test_results.txt`:
- Screenshot or description of blocked page
- Description of content modifications
- Description of word replacements

## Task 10: Final Code Review and Cleanup

**Files:**
- Modify: `sockets_activity/tcp_socket_server.py`

- [ ] **Step 1: Add docstrings to all functions**

Ensure every function has a clear docstring explaining:
- Purpose
- Parameters
- Return value
- Any important notes

- [ ] **Step 2: Remove any debug print statements**

Keep only informative print statements that help track proxy operation.

- [ ] **Step 3: Add error handling comments**

Add comments explaining error handling strategy in try/except blocks.

- [ ] **Step 4: Verify code follows activity requirements**

Check against activity PDF:
- ✓ Receives response from client
- ✓ Blocks forbidden sites correctly
- ✓ Replaces forbidden words from JSON
- ✓ Modifies headers correctly
- ✓ Handles messages larger than buffer

- [ ] **Step 5: Final commit**

```bash
git add sockets_activity/tcp_socket_server.py
git commit -m "refactor: add documentation and final cleanup"
```

---

## Summary of Deliverables

1. **proxy_config.json** - Configuration file
2. **sockets_activity/tcp_socket_server.py** - Complete proxy implementation
3. **test_results.txt** - Testing documentation with buffer handling explanations
4. **blocked_cat.jpg** (optional) - Image for 403 page

## Key Implementation Details

**Buffer Handling Strategy:**
- Read until `\r\n\r\n` found for HEAD (handles HEAD larger than buffer)
- Parse `Content-Length` from HEAD
- Continue reading until received `Content-Length` bytes for BODY
- Works with any buffer size >= 1 byte

**Proxy Flow:**
1. Client → Proxy: HTTP Request
2. Proxy: Check if blocked
3. Proxy → Server: Modified request (with X-ElQuePregunta header)
4. Server → Proxy: HTTP Response
5. Proxy: Replace forbidden words, update Content-Length
6. Proxy → Client: Modified response
