#!/bin/bash
echo "====================================="
echo "VTR PRIME VIDEO CHECKER - Setup"
echo "====================================="
echo ""

echo "Verificando Python3..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no esta instalado"
    echo "En Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "En Mac: brew install python3"
    exit 1
fi

python3 --version
echo ""
echo "Instalando dependencias..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Fallo al instalar dependencias"
    exit 1
fi

echo ""
echo "====================================="
echo "Instalacion completada!"
echo "====================================="
echo ""
echo "Para ejecutar el checker:"
echo "  - Opcion 1: python3 main.py"
echo "  - Opcion 2: ./run.sh"
echo ""
