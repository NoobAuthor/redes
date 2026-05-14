# TCP Go-Back-N con Control de Congestión (TCP Tahoe)

Implementación simplificada de TCP con Go-Back-N y control de congestión basado en TCP Tahoe.

## Archivos

### Clases auxiliares:
- `CongestionControl.py` - Control de congestión (slow start + AIMD)
- `slidingWindowCC.py` - Ventana deslizante con números de secuencia
- `socketUDP.py` - Socket UDP con múltiples timers

### Implementación principal:
- `SocketTCP_GBN.py` - SocketTCP con soporte para Go-Back-N y control de congestión

### Tests:
- `CongestionControl_test.py` - Tests unitarios para CongestionControl
- `cliente_gbn.py` - Cliente de prueba
- `servidor_gbn.py` - Servidor de prueba

## Instalación

```bash
cd TCP-UDP
```

## Tests

### Test Parte 1: CongestionControl
```bash
python3 CongestionControl_test.py
```

### Test Parte 2 y 3: Go-Back-N con Control de Congestión

Terminal 1:
```bash
python3 servidor_gbn.py
```

Terminal 2:
```bash
python3 cliente_gbn.py test_100kb.bin
```

Con debug:
```bash
python3 cliente_gbn.py test_100kb.bin debug
```

## Modo Debug

El modo debug muestra:
- Estado del control de congestión (slow_start o congestion_avoidance)
- Tamaño de cwnd en bytes y MSS
- Valor de ssthresh
- Cambios en el tamaño de la ventana
- Envío de segmentos y retransmisiones
- Detección de timeouts

## Características

### Control de Congestión (TCP Tahoe):
- **Slow Start**: cwnd crece exponencialmente (+1 MSS por ACK)
- **Congestion Avoidance**: cwnd crece linealmente (+1 MSS por cwnd ACKs)
- **Timeout**: ssthresh = cwnd/2, cwnd = 1 MSS, volver a slow start
- **MSS**: 8 bytes
- **cwnd inicial**: 1 MSS

### Go-Back-N:
- Ventana deslizante de tamaño variable (controlada por cwnd)
- ACKs acumulativos
- Retransmisión de toda la ventana en caso de timeout
- Un timer por segmento en la ventana

## Simulación de Pérdidas

### Con netem (Linux):
```bash
sudo tc qdisc add dev lo root netem loss 20%
```

Desactivar:
```bash
sudo tc qdisc del dev lo root
```

### Manual:
Interrumpir el cliente durante la transmisión para simular timeout.

## Resultados Esperados

Sin pérdida:
- Crecimiento exponencial de cwnd en slow start
- Transición suave a congestion avoidance
- Transmisión rápida

Con pérdida (20%):
- Detección de timeouts
- Reducción de cwnd y ajuste de ssthresh
- Recuperación gradual
- Transmisión más lenta pero confiable

## Limitaciones

Esta es una implementación simplificada para fines educativos:
- No implementa fast retransmit (3 ACKs duplicados)
- No implementa fast recovery (TCP Reno)
- MSS fijo de 8 bytes (en TCP real es ~1460 bytes)
- No maneja reordenamiento de paquetes
- No implementa selective ACK (SACK)
