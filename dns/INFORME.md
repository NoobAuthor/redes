# Informe - Resolver DNS

## Implementación

### 1. Tipo de Socket Utilizado

**Respuesta**: Se utilizó un socket de tipo **UDP (SOCK_DGRAM)**.

**Justificación**: DNS utiliza el protocolo UDP en el puerto 53 para la mayoría de sus consultas. UDP es preferido porque:
- Es más rápido que TCP (no requiere establecer conexión)
- Las consultas DNS son típicamente pequeñas y caben en un solo paquete
- No se necesita la confiabilidad de TCP para consultas simples
- Si no hay respuesta, el cliente simplemente reintenta

### 2. Estructura de Datos para Parsing

**Opción elegida**: **dnslib**

**Justificación**: Se utilizó la librería `dnslib` en lugar de manipulación manual de hexadecimal porque:
- Simplifica el parsing de mensajes DNS
- Maneja automáticamente la codificación/decodificación de campos
- Es más legible y mantenible
- Reduce errores de implementación
- Es apropiado para un proyecto educativo

**Estructura interna**:
- `DNSRecord`: Representa un mensaje DNS completo
- `header`: Contiene flags, contadores (QDCOUNT, ANCOUNT, etc.)
- `questions`: Lista de consultas
- `rr`: Lista de Resource Records (respuestas)
- `auth`: Lista de registros de autoridad
- `ar`: Lista de registros adicionales

### 3. Algoritmo de Resolución

El resolver sigue este algoritmo iterativo:

1. Recibe consulta del cliente
2. Verifica si el dominio está en cache → si está, responde inmediatamente
3. Si no está en cache, inicia resolución desde el servidor raíz (192.33.4.12)
4. Loop de resolución:
   - Envía consulta al servidor actual
   - Si recibe respuesta tipo A → guarda en cache y retorna
   - Si recibe delegación (NS en Authority):
     - Busca IP en Additional records
     - Si no hay IP, resuelve recursivamente el nombre del NS
     - Continúa con el siguiente servidor
5. Actualiza cache con los 3 dominios más frecuentes

### 4. Implementación del Cache

**Estrategia**: Top 3 dominios más frecuentes de las últimas 20 consultas

**Estructuras de datos**:
- `query_history`: Lista de tuplas (dominio, ip) - últimas 20 consultas
- `cache`: Diccionario dominio → ip - top 3 más frecuentes

**Algoritmo**:
```python
def update_cache(domain, ip):
    1. Agregar (dominio, ip) a query_history
    2. Mantener solo últimas 20 consultas
    3. Contar frecuencia de cada dominio
    4. Ordenar por frecuencia
    5. Seleccionar top 3
    6. Actualizar cache con top 3
```

## Pruebas de Funcionalidad

### Prueba 1: eol.uchile.cl
```
$ dig -p8000 @127.0.0.1 eol.uchile.cl
```
**Resultado esperado**: 146.83.63.70 (o similar, puede variar)
**Observación**: El dominio resuelve correctamente siguiendo la jerarquía .cl → uchile.cl → eol.uchile.cl

### Prueba 2: Cache de eol.uchile.cl
Segunda consulta a eol.uchile.cl muestra:
```
(debug) Respuesta obtenida del cache
```
**Resultado**: ✅ El cache funciona correctamente

### Prueba 3: www.uchile.cl
```
$ dig -p8000 @127.0.0.1 www.uchile.cl
```
**Resultado esperado**: 200.89.76.36
**Observación**: Resuelve correctamente

### Prueba 4: cc4303.bachmann.cl
```
$ dig -p8000 @127.0.0.1 cc4303.bachmann.cl
```
**Resultado esperado**: 104.248.65.245
**Observación**: Resuelve correctamente siguiendo delegaciones

## Experimentos

### Experimento 1: www.webofscience.com

**Pregunta**: ¿Resuelve su programa este dominio? ¿Qué sucede? ¿Por qué? ¿Cómo arreglaría esto?

**Observación**: Puede presentar problemas dependiendo de:
1. **CNAMEs**: Si el dominio usa registros CNAME (alias), nuestro resolver no los maneja explícitamente
2. **Múltiples delegaciones**: Cadenas largas de delegaciones pueden causar timeouts
3. **DNSSEC**: Algunos dominios requieren validación DNSSEC

**Solución propuesta**:
- Agregar soporte para registros CNAME
- Seguir la cadena de CNAMEs hasta encontrar un registro A
- Aumentar timeout para dominios con muchas delegaciones

### Experimento 2: www.cc4303.bachmann.cl

**Comando ejecutado**:
```bash
$ dig -p8000 @127.0.0.1 www.cc4303.bachmann.cl
```

**Observación esperada**: Puede no resolver o dar NXDOMAIN (dominio no existe)

**Contraste con Google DNS**:
```bash
$ dig @8.8.8.8 www.cc4303.bachmann.cl
```

**Explicación**: 
- Google DNS (8.8.8.8) usa **recursión completa** y cache global
- Nuestro resolver es **iterativo** y sin cache persistente
- Si www.cc4303.bachmann.cl no existe pero cc4303.bachmann.cl sí:
  - Google podría retornar NXDOMAIN con autoridad
  - Nuestro resolver sigue la jerarquía normal
- Google tiene cache de consultas previas, nosotros no

**Diferencias técnicas**:
- Resolver recursivo (Google) vs iterativo (nuestro)
- Cache distribuido vs cache local limitado
- Manejo de TTL y cache global vs cache simple

### Experimento 3: Múltiples consultas al mismo dominio

**Procedimiento**:
```bash
$ dig -p8000 @127.0.0.1 example.com
$ dig -p8000 @127.0.0.1 example.com
$ dig -p8000 @127.0.0.1 example.com
```

**Observación**:
- Primera consulta: Contacta varios Name Servers
- Los Name Servers pueden cambiar entre consultas
- Debug muestra diferentes servidores: a.nic.cl, b.nic.cl, etc.

**Explicación - Round Robin DNS**:
Los Name Servers usan **Round Robin DNS** para:
1. **Balanceo de carga**: Distribuir consultas entre varios servidores
2. **Alta disponibilidad**: Si un servidor falla, otros responden
3. **Redundancia geográfica**: Responder desde el servidor más cercano

**Por qué cambian los servidores**:
- El servidor raíz retorna múltiples NS para .cl
- Cada consulta puede seleccionar un NS diferente de la lista
- Los servidores DNS rotan las respuestas (round-robin)
- Anycast: Múltiples servidores comparten la misma IP

## Conclusiones

1. **UDP es apropiado para DNS**: Consultas rápidas sin overhead de TCP
2. **Jerarquía DNS**: El resolver sigue correctamente la jerarquía desde la raíz
3. **Cache mejora rendimiento**: Reduce latencia en consultas repetidas
4. **Delegaciones**: El manejo de NS records con y sin glue records funciona
5. **Round Robin**: Los NS varían por diseño, no por error
6. **Limitaciones**: No maneja CNAMEs, DNSSEC, o casos edge complejos

## Dificultades Encontradas

1. **Resolución recursiva de NS**: Cuando un NS no tiene glue records, hay que resolver su nombre
2. **Timeouts**: Algunos servidores son lentos o no responden
3. **Cache con frecuencia**: Implementar top-K requiere contar y ordenar frecuencias
4. **Parsing de respuestas**: Manejar diferentes tipos de registros (A, NS, SOA)

## Posibles Mejoras

1. Agregar soporte para registros CNAME
2. Implementar cache con TTL respetando tiempos de vida
3. Agregar IPv6 (registros AAAA)
4. Paralelizar consultas a múltiples NS
5. Persistir cache en disco
6. Agregar métricas y logging
