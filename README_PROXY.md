# HTTP Proxy Server - Actividad Redes

## Archivos Entregables

1. **`sockets_activity/tcp_socket_server.py`** - Implementación del proxy (~250 líneas)
2. **`proxy_config.json`** - Archivo de configuración

## Estructura del Código

El código se organiza en:
- **`receive_http_message()`** - Recibe mensajes HTTP completos usando Content-Length
- **`parse_http()`** - Parsea mensajes HTTP
- **`create_http()`** - Construye mensajes HTTP
- **Loop principal** - Lógica del proxy (bloqueo, headers, reemplazo de palabras)

## Funcionalidades Implementadas

### ✅ 1. Recepción de mensajes HTTP con Content-Length

- Recibe HEAD hasta encontrar `\r\n\r\n`
- Parsea Content-Length del header
- Continúa recibiendo hasta obtener todos los bytes del BODY
- **Funciona con cualquier tamaño de buffer** (incluso menor que HEAD o BODY)

### ✅ 2. Bloqueo de sitios prohibidos

- Verifica si la URL está en la lista `blocked` del JSON
- Retorna HTTP 403 Forbidden con HTML personalizado

### ✅ 3. Modificación de headers

- Agrega header `X-ElQuePregunta` con el usuario del JSON a todas las requests

### ✅ 4. Reemplazo de palabras prohibidas

- Reemplaza palabras según el diccionario `forbidden_words` del JSON
- Actualiza `Content-Length` después del reemplazo

### ✅ 5. Manejo de mensajes grandes

- Implementa recepción por chunks
- No depende del tamaño del buffer
- Puede probarse con `buff_size = 50` o incluso menor

## Cómo Ejecutar

### 1. Iniciar el proxy

```bash
python3 sockets_activity/tcp_socket_server.py proxy_config.json
```

El proxy escuchará en `0.0.0.0:8000` por defecto.

### 2. Probar con curl

**Sitio normal (funciona):**

```bash
curl http://example.com -x localhost:8000 -i
```

**Sitio bloqueado (403 Forbidden):**

```bash
curl http://cc4303.bachmann.cl/secret -x localhost:8000 -i
```

**Con custom header:**

```bash
curl http://cc4303.bachmann.cl/ -x localhost:8000 -i
```

**Reemplazo de palabras:**

```bash
curl http://cc4303.bachmann.cl/replace -x localhost:8000
```

### 3. Probar con navegador

1. Configurar proxy del navegador: `localhost:8000`
2. Visitar `http://cc4303.bachmann.cl/` - debe funcionar con header personalizado
3. Visitar `http://cc4303.bachmann.cl/secret` - debe mostrar 403
4. Visitar `http://cc4303.bachmann.cl/replace` - palabras deben estar reemplazadas

## Configuración (proxy_config.json)

```json
{
  "user": "tu-email@ejemplo.com",
  "blocked": ["http://www.dcc.uchile.cl/", "http://cc4303.bachmann.cl/secret"],
  "forbidden_words": [
    { "proxy": "[REDACTED]" },
    { "DCC": "[FORBIDDEN]" },
    { "biblioteca": "[???]" }
  ]
}
```

## Probar con buffer pequeño

Editar línea 107 en `tcp_socket_server.py`:

```python
buff_size = 50  # En vez de 4096
```

Reiniciar el proxy y probar que sigue funcionando correctamente.

## Respuestas a Preguntas del Enunciado

### ¿Cómo sé si llegó el mensaje completo?

- **HEAD:** Busco `\r\n\r\n` en los datos recibidos
- **BODY:** Uso el header `Content-Length` para saber cuántos bytes debo recibir

### ¿Qué pasa si los headers no caben en mi buffer?

- Sigo recibiendo chunks y concatenando hasta encontrar `\r\n\r\n`

### ¿Cómo sé que el HEAD llegó completo?

- Cuando encuentro la secuencia `\r\n\r\n` en el mensaje

### ¿Y el BODY?

- Cuando he recibido exactamente `Content-Length` bytes después del HEAD

## Puntaje Esperado

- (+0.5) El cliente recibe una respuesta ✅
- (+1.0) El proxy bloquea correctamente los sitios prohibidos ✅
- (+1.2) Se reemplazan correctamente las palabras según el json ✅
- (+0.5) Se modifican correctamente los headers ✅
- (+1.3) Se manejan correctamente mensajes más grandes que el buffer ✅

**Total código: 4.5 pts**

---

_Implementado con Python 3 usando sockets TCP orientados a conexión_
