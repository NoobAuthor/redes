# Instrucciones de Uso - Resolver DNS

## 📋 Contenido del Directorio

```
dns/
├── resolver.py              # Código principal del resolver
├── requirements.txt         # Dependencias (dnslib)
├── setup.sh                 # Script de instalación
├── run.sh                   # Script para ejecutar el resolver
├── test_resolver.py         # Tests con el servidor corriendo
├── test_standalone.py       # Tests sin servidor (directo)
├── test_cache.py            # Tests del cache
├── verificacion_pruebas.py  # Verificación de pruebas oficiales
├── README.md                # Documentación completa
├── INFORME.md               # Informe de la actividad
└── INSTRUCCIONES.md         # Este archivo
```

## 🚀 Inicio Rápido

### 1. Instalación (solo la primera vez)

```bash
cd dns
./setup.sh
```

Esto creará un entorno virtual e instalará `dnslib`.

### 2. Ejecutar el Resolver

```bash
cd dns
./run.sh
```

El resolver quedará escuchando en el puerto 8000.

### 3. Hacer Consultas (en otra terminal)

```bash
# Consulta simple
dig -p8000 @127.0.0.1 example.com

# Consultas de las pruebas oficiales
dig -p8000 @127.0.0.1 eol.uchile.cl
dig -p8000 @127.0.0.1 www.uchile.cl
dig -p8000 @127.0.0.1 cc4303.bachmann.cl
```

## 🧪 Tests Automatizados

### Verificación de Pruebas Oficiales

```bash
source venv/bin/activate
python3 verificacion_pruebas.py
```

Este script verifica automáticamente las 4 pruebas oficiales:
1. ✅ eol.uchile.cl → 146.83.63.70
2. ✅ Cache funciona en segunda consulta
3. ✅ www.uchile.cl → 200.89.76.36
4. ✅ cc4303.bachmann.cl → 104.248.65.245

### Test Standalone (sin servidor)

```bash
source venv/bin/activate
python3 test_standalone.py
```

Prueba el resolver directamente sin necesidad de correrlo como servidor.

### Test de Cache

```bash
source venv/bin/activate
python3 test_cache.py
```

Verifica que el cache guarde los 3 dominios más frecuentes.

## 📖 Características Implementadas

### ✅ Requerimientos Cumplidos

1. **Socket UDP**: Usa `SOCK_DGRAM` en puerto 8000
2. **Resolución iterativa**: Sigue la jerarquía desde el servidor raíz
3. **Parsing DNS**: Usa dnslib para parsear mensajes
4. **Función resolver()**: Implementa el algoritmo especificado:
   - Consulta al servidor raíz (192.33.4.12)
   - Maneja respuestas tipo A
   - Maneja delegaciones NS con glue records
   - Maneja delegaciones NS sin glue records (recursión)
5. **Modo debug**: Muestra cada paso de la resolución
6. **Cache**: Almacena top 3 dominios de últimas 20 consultas
7. **Compatible con dig**: Responde en formato estándar DNS

### 🎯 Funcionalidades Extra

- Script de instalación automática
- Tests automatizados
- Documentación completa
- Informe con respuestas a experimentos
- Manejo robusto de errores
- Timeouts configurables

## 🔧 Configuración

### Cambiar Puerto

Edita `resolver.py`:
```python
RESOLVER_PORT = 8000  # Cambiar a otro puerto
```

### Desactivar Debug

Edita `resolver.py`:
```python
DEBUG = False  # Cambiar a False
```

### Cambiar Servidor Raíz

Edita `resolver.py`:
```python
ROOT_DNS_SERVER = "192.33.4.12"  # Cambiar si es necesario
```

## 📝 Modo Debug

Cuando DEBUG = True, el resolver muestra:

```
(debug) Resolviendo dominio: www.uchile.cl
(debug) Consultando 'www.uchile.cl' a '.' con dirección IP '192.33.4.12'
(debug) Consultando 'www.uchile.cl' a 'ns1.uchile.cl' con dirección IP '200.89.70.3'
(debug) Respuesta encontrada: 200.89.76.36
```

Cuando usa cache:
```
(debug) Resolviendo dominio: www.uchile.cl
(debug) Respuesta obtenida del cache
```

## 🐛 Troubleshooting

### Error: "Module not found: dnslib"

**Solución**: Ejecuta `./setup.sh` o activa el entorno virtual:
```bash
source venv/bin/activate
```

### Error: "Address already in use"

**Solución**: Otro proceso está usando el puerto 8000. Mátalo o cambia el puerto:
```bash
# Encontrar el proceso
lsof -i :8000

# Matarlo
kill -9 <PID>
```

### Error: "connection timed out"

**Solución**: 
1. Verifica que el resolver esté corriendo
2. Verifica que uses el puerto correcto (8000)
3. Usa 127.0.0.1 o localhost

### El resolver no responde

**Solución**:
1. Verifica que DEBUG = True para ver qué está pasando
2. Algunos dominios pueden tardar (servidores lentos)
3. Revisa la conexión a internet (necesita llegar al servidor raíz)

## 📚 Documentación Adicional

- **README.md**: Documentación técnica completa
- **INFORME.md**: Respuestas a preguntas de la actividad
- **resolver.py**: Código bien comentado

## 🎓 Para el Informe

El archivo `INFORME.md` contiene:
- Tipo de socket usado y justificación
- Estructura de datos para parsing
- Algoritmo de resolución
- Implementación del cache
- Resultados de pruebas
- Respuestas a los 3 experimentos
- Conclusiones y dificultades

## ✅ Checklist de Entrega

- [ ] Instalación exitosa (`./setup.sh`)
- [ ] Resolver se ejecuta sin errores (`./run.sh`)
- [ ] Las 4 pruebas oficiales pasan (`verificacion_pruebas.py`)
- [ ] Debug muestra pasos correctamente
- [ ] Cache funciona en consultas repetidas
- [ ] Informe completado con observaciones de experimentos

## 💡 Tips

1. **Para desarrollo**: Usa `test_standalone.py` para probar sin correr el servidor
2. **Para demo**: Usa `./run.sh` y `dig` para mostrar funcionamiento real
3. **Para debugging**: Activa DEBUG = True y observa cada paso
4. **Para el informe**: Ejecuta los experimentos y anota observaciones en INFORME.md

## 🚨 Nota sobre IP de VM

El código actual usa `0.0.0.0` para escuchar en todas las interfaces.

Si usas una VM real:
1. Obtén la IP de la VM: `ip addr` o `ifconfig`
2. En otra máquina consulta: `dig -p8000 @<IP_VM> example.com`
3. Para localhost siempre usa: `127.0.0.1`

## 📞 Comandos Útiles

```bash
# Ver tráfico DNS
sudo tcpdump -v -i lo port 8000

# Consulta verbose con dig
dig -p8000 @127.0.0.1 example.com

# Consulta solo IP
dig -p8000 @127.0.0.1 example.com +short

# Comparar con Google DNS
dig @8.8.8.8 example.com
```
