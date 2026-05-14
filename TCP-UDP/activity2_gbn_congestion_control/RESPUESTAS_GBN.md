# Respuestas Actividad Go-Back-N y Control de Congestión

**Integrantes:** Igor Assis, Nelson Alejandro Navarro Barria

---

## Parte 2: Preguntas sobre Go-Back-N

### Pregunta 1: ¿Por qué le puede servir usar como base para Go Back-N el código de Stop & Wait? ¿Qué similitud tiene Go Back-N con Stop & Wait?

Stop & Wait es básicamente Go-Back-N con ventana de tamaño 1. Ambos protocolos:
- Envían segmentos con números de secuencia
- Esperan ACKs acumulativos
- Retransmiten cuando hay timeout
- El receptor envía ACK del último segmento recibido en orden

La diferencia está en que Go-Back-N puede tener múltiples segmentos en vuelo (ventana > 1), mientras que Stop & Wait espera el ACK de cada segmento antes de enviar el siguiente. Por eso podemos reutilizar la lógica de crear segmentos, parsear ACKs, y manejar timeouts.

### Pregunta 2: ¿Qué ocurre con la función recv? ¿Esta función cambia con el uso de SocketUDP y SlidingWindowCC?

La función recv NO cambia mucho entre Stop & Wait y Go-Back-N. El receptor sigue esperando segmentos en orden y enviando ACKs acumulativos. 

La diferencia principal es que en Go-Back-N el receptor puede recibir segmentos fuera de orden (si hay pérdidas), pero solo acepta los que llegan en secuencia correcta y descarta los demás. El ACK siempre indica el próximo byte esperado.

SocketUDP y SlidingWindowCC se usan principalmente en el emisor para manejar la ventana deslizante y los múltiples timers. El receptor sigue usando el socket UDP normal.

---

## Implementación

### Archivos entregados:

1. **CongestionControl.py** - Clase de control de congestión TCP Tahoe
2. **slidingWindowCC.py** - Clase de ventana deslizante
3. **socketUDP.py** - Socket UDP con múltiples timers
4. **SocketTCP_GBN.py** - Implementación de SocketTCP con Go-Back-N y control de congestión
5. **cliente_gbn.py** - Cliente de prueba
6. **servidor_gbn.py** - Servidor de prueba

### Uso:

Terminal 1 (servidor):
```bash
python3 servidor_gbn.py
```

Terminal 2 (cliente):
```bash
python3 cliente_gbn.py test_100kb.bin
```

Para modo debug:
```bash
python3 cliente_gbn.py test_100kb.bin debug
```

### Características implementadas:

- Control de congestión TCP Tahoe (slow start + AIMD)
- Go-Back-N con ventana deslizante
- MSS = 8 bytes
- cwnd inicial = 1 MSS
- Timeout provoca ssthresh = cwnd/2, cwnd = 1 MSS, volver a slow start
- ACK exitoso en slow start: cwnd += 1 MSS
- ACK exitoso en AIMD: cwnd += MSS/cwnd (aumento lineal)
- Modo debug para visualizar evolución de la ventana
- Contador de segmentos enviados

---

## Pruebas Realizadas

### Test 1: Sin pérdida
- Archivo de 100KB enviado correctamente
- Control de congestión crece la ventana exponencialmente en slow start
- Transición a congestion avoidance cuando cwnd >= ssthresh

### Test 2: Con pérdida (20%)
- Timeout detectado correctamente
- ssthresh actualizado a cwnd/2
- cwnd vuelve a 1 MSS
- Retransmisión de toda la ventana (Go-Back-N)
- Archivo recibido íntegro

### Test 3: Comparación con Stop & Wait
- Go-Back-N con control de congestión es más rápido cuando no hay pérdidas
- Con pérdidas altas (>20%), Stop & Wait puede ser comparable porque Go-Back-N retransmite toda la ventana
- El control de congestión ayuda a adaptarse a las condiciones de la red
