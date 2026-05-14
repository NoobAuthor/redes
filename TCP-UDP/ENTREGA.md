# Entrega: Control de Congestión TCP Tahoe con Go-Back-N

**Integrantes:** Igor Assis, Nelson Alejandro Navarro Barria

## Estructura de la Entrega

### Parte 1: Clase CongestionControl (1.5 pts)
**Archivo:** `CongestionControl.py`

Implementa control de congestión TCP Tahoe con:
- Estados: slow_start, congestion_avoidance
- Variables: MSS, cwnd, ssthresh, current_state
- Funciones:
  - `get_cwnd()` - retorna cwnd en bytes
  - `get_MSS_in_cwnd()` - retorna cantidad de MSS en cwnd
  - `get_ssthresh()` - retorna ssthresh
  - `is_state_slow_start()` - verifica si está en slow start
  - `is_state_congestion_avoidance()` - verifica si está en AIMD
  - `event_ack_received()` - maneja recepción de ACK
  - `event_timeout()` - maneja timeout

**Test:** `CongestionControl_test.py`

Ejecutar:
```bash
python3 CongestionControl_test.py
```

### Parte 2: Go-Back-N (1.5 pts)
**Archivo:** `SocketTCP_GBN.py`

Implementa Go-Back-N con:
- `send(message, mode="go_back_n")` - envío con Go-Back-N
- `recv(buff_size, mode="go_back_n")` - recepción con Go-Back-N
- `send_using_go_back_n()` - implementación de Go-Back-N
- `recv_using_go_back_n()` - recepción para Go-Back-N
- Ventana deslizante usando `SlidingWindowCC`
- Múltiples timers usando `SocketUDP`

**Respuestas a preguntas:**

1. Go-Back-N se parece a Stop & Wait porque ambos:
   - Usan números de secuencia
   - Esperan ACKs acumulativos
   - Retransmiten en caso de timeout
   - Stop & Wait es Go-Back-N con ventana = 1

2. La función recv no cambia mucho porque:
   - El receptor sigue esperando segmentos en orden
   - Envía ACKs acumulativos del último segmento correcto
   - SocketUDP y SlidingWindowCC se usan en el emisor

### Parte 3: Integración (1.5 pts)
**Archivo:** `SocketTCP_GBN.py` (misma implementación)

Integra control de congestión en Go-Back-N:
- Objeto CongestionControl con MSS = 8 bytes
- Ventana dinámica controlada por cwnd
- Llama `event_timeout()` cuando hay timeout
- Llama `event_ack_received()` cuando llega ACK
- Actualiza tamaño de ventana según cwnd
- Envía nuevos segmentos cuando la ventana crece
- Maneja caso borde de ventana que se reduce

**Modo debug:** `debug_mode = True` muestra evolución de cwnd

## Archivos Auxiliares

- `slidingWindowCC.py` - Ventana deslizante con números de secuencia
- `socketUDP.py` - Socket UDP con múltiples timers
- `cliente_gbn.py` - Cliente de prueba con contador de segmentos
- `servidor_gbn.py` - Servidor de prueba

## Pruebas (1.5 pts informe)

### Test 1: Sin pérdida
```bash
Terminal 1: python3 servidor_gbn.py
Terminal 2: python3 cliente_gbn.py test_100kb.bin
```

Resultado:
- Transmisión exitosa
- cwnd crece exponencialmente en slow start
- Transición a congestion avoidance
- Archivo recibido íntegro

### Test 2: Con pérdida
```bash
Terminal 2: python3 cliente_gbn.py test_100kb.bin debug
```

Interrumpir durante transmisión para simular pérdida.

Resultado:
- Timeout detectado
- ssthresh = cwnd/2
- cwnd vuelve a 1 MSS
- Retransmisión de ventana completa
- Recuperación gradual
- Archivo recibido íntegro

### Test 3: Modo debug
```bash
python3 cliente_gbn.py test_100kb.bin debug
```

Muestra:
- Estado de control de congestión
- Cambios en cwnd y ssthresh
- Envío de segmentos
- Timeouts y retransmisiones

### Test 4: Contador de segmentos
El cliente cuenta segmentos enviados para comparar eficiencia.

## Cómo Ejecutar

1. Test Parte 1:
```bash
python3 CongestionControl_test.py
```

2. Test Parte 2 y 3:
```bash
Terminal 1: python3 servidor_gbn.py
Terminal 2: python3 cliente_gbn.py test_100kb.bin
```

3. Con debug:
```bash
python3 cliente_gbn.py test_100kb.bin debug
```

## Observaciones

- Implementación simplificada para fines educativos
- No incluye fast retransmit ni fast recovery (solo TCP Tahoe básico)
- MSS = 8 bytes (en lugar de típicos 1460 bytes)
- Sin pérdida, cwnd crece rápidamente
- Con pérdida, control de congestión adapta la ventana
- Go-Back-N es más eficiente que Stop & Wait cuando no hay pérdidas
- Con pérdidas altas, retransmitir toda la ventana puede ser costoso

## Comparación: Go-Back-N con CC vs sin CC

**Con control de congestión:**
- Inicio conservador (cwnd = 1 MSS)
- Crecimiento adaptativo
- Recuperación ante pérdidas
- Fairness en la red

**Sin control de congestión:**
- Ventana fija
- Puede congestionar la red
- No se adapta a condiciones
- Potencialmente más rápido en redes sin pérdidas

Para redes reales, el control de congestión es esencial para evitar colapso de la red y garantizar fairness entre flujos.
