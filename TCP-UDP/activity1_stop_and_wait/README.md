# TCP sobre UDP con Stop & Wait

Implementación de una capa TCP simplificada sobre sockets UDP usando el protocolo Stop & Wait para comunicación confiable.

## Archivos Principales

- **`SocketTCP.py`** - Clase que implementa TCP sobre UDP (318 líneas)
- **`cliente.py`** - Cliente para enviar archivos (40 líneas)
- **`servidor.py`** - Servidor para recibir archivos (51 líneas)
- **`INFORME.md`** - Documentación completa del diseño e implementación

## Uso Rápido

### Servidor
```bash
python3 servidor.py 8000
```

### Cliente
```bash
python3 cliente.py localhost 8000 < archivo.txt
```

### Tests
```bash
python3 test_basico.py
```

## Características

✅ 3-way handshake (SYN, SYN+ACK, ACK)  
✅ Stop & Wait con ACKs y retransmisiones  
✅ Manejo de pérdidas con timeouts  
✅ Cierre de conexión de 4 vías (FIN, FIN+ACK, ACK)  
✅ Segmentación en chunks de 16 bytes  
✅ Soporte para `recv(buff_size)` con `buff_size < message_length`  

## Formato de Segmentos

```
SYN|||ACK|||FIN|||SEQ|||DATOS
```

Ejemplo:
- SYN: `1|||0|||0|||42|||`
- SYN+ACK: `1|||1|||0|||78|||`
- Datos: `0|||0|||0|||98|||Mensaje de prueba`
- FIN: `0|||0|||1|||150|||`

## Pruebas con Pérdidas

### Usando netem (Linux/Mac con privilegios)
```bash
# Activar pérdida del 20%
sudo tc qdisc add dev lo root netem loss 20.0% delay 0.5s

# Ejecutar tests
python3 test_basico.py

# Desactivar
sudo tc qdisc del dev lo root netem
```

## Resultados de Tests

Todos los tests pasan exitosamente:
- ✓ Test 1: 3-way Handshake
- ✓ Test 2: Send/recv con 16 bytes (1 chunk)
- ✓ Test 3: Send/recv con 19 bytes (2 chunks)
- ✓ Test 4: Recv múltiple con buff_size < message_length
- ✓ Test 5: Cierre de conexión

## Documentación Completa

Ver **`INFORME.md`** para:
- Diagramas del handshake y cierre
- Explicación detallada del protocolo Stop & Wait
- Casos borde y soluciones
- Decisiones de diseño
- Manejo de `buff_size < message_length`

## Commits

El proyecto sigue conventional commits:
```
:sparkles: feat: add SocketTCP class with segment parsing and creation
:sparkles: feat: add cliente.py and servidor.py
:bug: fix: correct recv buffer management and close handling
:memo: docs: add comprehensive INFORME.md
```
