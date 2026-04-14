#!/bin/bash
# Script de instalación para el resolver DNS

echo "Configurando entorno virtual..."
python3 -m venv venv

echo "Activando entorno virtual..."
source venv/bin/activate

echo "Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "¡Instalación completada!"
echo ""
echo "Para ejecutar el resolver:"
echo "  source venv/bin/activate"
echo "  python3 resolver.py"
