import PyInstaller.__main__
import sys
import os

# Configuración de PyInstaller
PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=VTR_Checker',
    '--distpath=./dist',
    '--buildpath=./build',
    '--specpath=./build',
    '--icon=NONE',
    '--add-data=config.json:.',
    '--hidden-import=PyQt5',
    '--hidden-import=requests',
    '--hidden-import=cryptography',
])

print("\n" + "="*50)
print("✓ Compilación completada!")
print("Ejecutable: dist/VTR_Checker.exe")
print("="*50)
