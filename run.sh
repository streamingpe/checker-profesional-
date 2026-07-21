#!/bin/bash
echo "====================================="
echo "VTR PRIME VIDEO CHECKER"
echo "====================================="
echo ""
python3 main.py
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: No se pudo ejecutar el checker"
    echo "Asegurate de tener Python 3 instalado"
    echo "Ejecuta primero: chmod +x install.sh && ./install.sh"
fi
