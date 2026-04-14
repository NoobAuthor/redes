# Resolver DNS - Actividad de Redes

Implementación de un resolver DNS simple para la actividad de la clase de Redes.

## Requisitos

- Python 3.x
- dnslib: `pip3 install dnslib`

## Instalación

### Opción 1: Usar el script de instalación

```bash
cd dns
./setup.sh
```

### Opción 2: Manual

```bash
cd dns
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

### 1. Ejecutar el resolver

En una terminal:

```bash
cd dns
python3 resolver.py
```

El resolver escuchará en el puerto 8000.

### 2. Hacer consultas con dig

En otra terminal:

```bash
# Consultar www.uchile.cl
dig -p8000 @127.0.0.1 www.uchile.cl

# Consultar eol.uchile.cl
dig -p8000 @127.0.0.1 eol.uchile.cl

# Consultar cc4303.bachmann.cl
dig -p8000 @127.0.0.1 cc4303.bachmann.cl

# Consultar example.com
dig -p8000 @127.0.0.1 example.com
```

### 3. Usar el script de prueba

Alternativamente, puedes usar el script de prueba:

```bash
python3 test_resolver.py
```

## Características

### ✅ Funcionalidades implementadas

1. **Resolución recursiva**: El resolver sigue la jerarquía DNS desde el servidor raíz
2. **Debug mode**: Muestra cada paso de la resolución
3. **Cache**: Almacena los 3 dominios más frecuentes de las últimas 20 consultas
4. **Manejo de delegaciones**: Sigue referencias NS con o sin glue records
5. **Compatibilidad con dig**: Responde en el formato esperado

### Modo Debug

El resolver imprime información útil durante la resolución:

```
(debug) Resolviendo dominio: www.uchile.cl
(debug) Consultando 'www.uchile.cl' a '.' con dirección IP '192.33.4.12'
(debug) Consultando 'www.uchile.cl' a 'ns1.nic.cl' con dirección IP '200.7.18.38'
(debug) Respuesta encontrada: 200.89.76.36
```

Cuando usa el cache:

```
(debug) Resolviendo dominio: www.uchile.cl
(debug) Respuesta obtenida del cache
```

### Cache

El resolver mantiene un cache de los 3 dominios más consultados entre las últimas 20 consultas. Esto reduce el tiempo de respuesta para consultas repetidas.

## Pruebas de funcionalidad

Según la actividad, se deben verificar los siguientes casos:

1. ✅ `dig -p8000 @127.0.0.1 eol.uchile.cl` → 146.83.63.70
2. ✅ Segunda consulta a eol.uchile.cl usa el cache
3. ✅ `dig -p8000 @127.0.0.1 www.uchile.cl` → 200.89.76.36
4. ✅ `dig -p8000 @127.0.0.1 cc4303.bachmann.cl` → 104.248.65.245

## Notas de implementación

- **Tipo de socket**: UDP (SOCK_DGRAM) - DNS utiliza UDP en el puerto 53
- **Puerto del resolver**: 8000 (no se usa el 53 porque está reservado)
- **Servidor raíz**: 192.33.4.12 (c.root-servers.net)
- **Librería**: dnslib para facilitar el parsing de mensajes DNS

## Estructura del código

- `resolver.py`: Implementación principal del resolver
- `test_resolver.py`: Script de prueba
- `README.md`: Este archivo

## Experimentos (para el informe)

1. **www.webofscience.com**: Puede fallar si hay problemas con CNAMEs o múltiples redirecciones
2. **www.cc4303.bachmann.cl**: Comparar con `dig @8.8.8.8` para ver diferencias
3. **Múltiples consultas**: Los Name Servers pueden variar por round-robin DNS

## Desactivar modo debug

Para desactivar los mensajes de debug, edita `resolver.py` y cambia:

```python
DEBUG = False
```
