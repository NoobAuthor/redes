# HTTP Proxy Server - Instrucciones de Uso

## Archivos de la Actividad

- **`sockets_activity/tcp_socket_server.py`** - Implementación del proxy HTTP (~260 líneas)
- **`proxy_config.json`** - Archivo de configuración del proxy

## Cómo Ejecutar el Proxy

### 1. Iniciar el servidor proxy

```bash
python3 sockets_activity/tcp_socket_server.py proxy_config.json
```

El proxy escuchará en `0.0.0.0:8000` por defecto y mostrará:
- Usuario configurado
- Cantidad de sitios bloqueados
- Cantidad de palabras prohibidas

### 2. Probar con curl

**Sitio normal (debe funcionar):**
```bash
curl http://example.com -x localhost:8000 -i
```

**Sitio bloqueado (debe retornar 403 Forbidden):**
```bash
curl http://cc4303.bachmann.cl/secret -x localhost:8000 -i
```

**Verificar header personalizado:**
```bash
curl http://cc4303.bachmann.cl/ -x localhost:8000 -i
# Buscar el header X-ElQuePregunta en la respuesta del servidor
```

**Probar reemplazo de palabras:**
```bash
curl http://cc4303.bachmann.cl/replace -x localhost:8000
# Las palabras configuradas deben aparecer reemplazadas
```

### 3. Probar con navegador

1. Configurar el proxy del navegador: `localhost:8000`
2. Visitar `http://cc4303.bachmann.cl/` - debe funcionar
3. Visitar `http://cc4303.bachmann.cl/secret` - debe mostrar página 403
4. Visitar `http://cc4303.bachmann.cl/replace` - palabras prohibidas deben estar reemplazadas

## Configuración (proxy_config.json)

```json
{
  "user": "tu-email@ejemplo.com",
  "blocked": [
    "http://www.dcc.uchile.cl/",
    "http://cc4303.bachmann.cl/secret"
  ],
  "forbidden_words": [
    { "proxy": "[REDACTED]" },
    { "DCC": "[FORBIDDEN]" },
    { "biblioteca": "[???]" }
  ]
}
```

**Personalización:**
- `user`: Tu correo o identificador
- `blocked`: Lista de URLs a bloquear (el proxy verifica si la URL comienza con alguna de estas)
- `forbidden_words`: Lista de diccionarios con palabras a reemplazar en las respuestas

## Probar con Buffer Pequeño

Para verificar que el proxy maneja correctamente mensajes más grandes que el buffer:

1. Editar la línea 111 en `tcp_socket_server.py`:
   ```python
   buff_size = 50  # Cambiar de 4096 a 50
   ```

2. Reiniciar el proxy y probar con cualquiera de los comandos anteriores

El proxy debe seguir funcionando correctamente incluso con un buffer muy pequeño.

## Funcionalidades Implementadas

### ✅ 1. Recepción completa de mensajes HTTP
- Recibe el HEAD hasta encontrar `\r\n\r\n`
- Extrae el valor de `Content-Length` del header
- Continúa recibiendo hasta obtener todos los bytes del BODY
- **Funciona con cualquier tamaño de buffer**

### ✅ 2. Bloqueo de sitios prohibidos
- Verifica si la URL solicitada está en la lista `blocked`
- Retorna HTTP 403 Forbidden con página HTML personalizada

### ✅ 3. Modificación de headers
- Agrega el header `X-ElQuePregunta` con el usuario configurado a todas las requests

### ✅ 4. Reemplazo de palabras prohibidas
- Reemplaza palabras según el diccionario `forbidden_words`
- Actualiza `Content-Length` si el tamaño del body cambia

### ✅ 5. Manejo de mensajes grandes
- Implementa recepción por chunks
- No depende del tamaño del buffer configurado

## Estructura del Código

### Funciones principales:

**`receive_http_message(sock, buff_size)`**
- Recibe un mensaje HTTP completo manejando HEAD y BODY por separado
- Usa Content-Length para determinar cuántos bytes del body recibir

**`parse_http(message)`**
- Parsea un mensaje HTTP (request o response)
- Extrae método/path/versión o status code
- Parsea todos los headers en un diccionario

**`create_http(data)`**
- Construye un mensaje HTTP a partir de datos parseados
- Formatea correctamente start line, headers y body

**Loop principal (líneas 122-259)**
- Acepta conexiones de clientes
- Verifica bloqueos
- Modifica headers
- Reenvía requests al servidor destino
- Reemplaza palabras prohibidas en respuestas
- Retorna respuesta modificada al cliente

## Detener el Proxy

Presionar `Ctrl+C` en la terminal donde está corriendo el proxy.

## Solución de Problemas

**"Address already in use":**
- El puerto 8000 está ocupado
- Espera unos segundos o cambia el puerto en línea 112

**"Connection refused" al servidor destino:**
- Verifica que la URL es accesible
- Verifica tu conexión a internet

**El navegador no se conecta:**
- Verifica la configuración del proxy en el navegador
- Asegúrate de usar `http://` (no `https://`)
