"""
Script para construir un ejecutable .exe con PyInstaller
Ejecutar: python build_exe.py
"""

import os
import subprocess
import sys

def build_exe():
    print("=" * 60)
    print("VTR PRIME VIDEO CHECKER - Builder EXE")
    print("=" * 60)
    
    # Verificar que PyInstaller esté instalado
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller no está instalado")
        print("Ejecuta: pip install pyinstaller")
        return False
    
    print("\n📦 Compilando aplicación...")
    
    comando = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',
        '--name=VTR_Checker',
        '--add-data=requirements.txt:.',
        'main.py'
    ]
    
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅ ¡Compilación exitosa!")
            print("\n📁 El ejecutable se encuentra en: ./dist/VTR_Checker.exe")
            print("\n💡 Instrucciones:")
            print("   1. Abre dist/VTR_Checker.exe")
            print("   2. Carga tu archivo de combos (RUT:PASSWORD)")
            print("   3. Opcionalmente carga proxies")
            print("   4. Haz clic en 'INICIAR'")
            return True
        else:
            print("❌ Error en compilación:")
            print(resultado.stderr)
            return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
