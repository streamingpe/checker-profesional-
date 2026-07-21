@echo off
echo =====================================
echo VTR PRIME VIDEO CHECKER
echo =====================================
echo.
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar el checker
    echo Asegurate de tener Python instalado
    echo Ejecuta primero: install.bat
    pause
)
