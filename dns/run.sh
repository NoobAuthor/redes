#!/bin/bash
# Script para ejecutar el resolver DNS

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Iniciando Resolver DNS${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado"
    echo "Ejecuta primero: ./setup.sh"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar si dnslib está instalado
python3 -c "import dnslib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ dnslib no está instalado"
    echo "Ejecuta primero: ./setup.sh"
    exit 1
fi

echo -e "${GREEN}✅ Entorno configurado correctamente${NC}"
echo ""
echo "El resolver escuchará en el puerto 8000"
echo ""
echo "Para hacer consultas desde otra terminal:"
echo "  dig -p8000 @127.0.0.1 example.com"
echo "  dig -p8000 @127.0.0.1 www.uchile.cl"
echo ""
echo "Presiona Ctrl+C para detener el resolver"
echo ""
echo -e "${BLUE}========================================${NC}"
echo ""

# Ejecutar resolver
python3 resolver.py
