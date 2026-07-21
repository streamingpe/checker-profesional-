@echo off
echo =====================================
echo VTR PRIME VIDEO CHECKER - Setup
echo =====================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH"
    pause
    exit /b 1
)

echo Python encontrado!
echo.
echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias
    pause
    exit /b 1
)

echo.
echo =====================================
echo Instalacion completada!
echo =====================================
echo.
echo Para ejecutar el checker:
echo   - Opcion 1: Ejecuta "python main.py"
echo   - Opcion 2: Ejecuta "python build_exe.py" para crear un EXE
echo.
pause
