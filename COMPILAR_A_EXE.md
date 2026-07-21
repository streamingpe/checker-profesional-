# COMPILAR A EXE - Guía Completa

## 📦 ¿Qué necesitas?

✅ Python 3.8 o superior instalado
✅ Todos los archivos del proyecto
✅ PyInstaller (se instala automáticamente)

---

## 🚀 OPCIÓN 1: Compilación Automática (RECOMENDADO)

### Paso 1: Preparar el proyecto
```bash
# Clonar o descargar el proyecto
cd checker-profesional-

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Compilar a EXE
```bash
# Windows
python build_exe.py

# Linux/Mac
python3 build_exe.py
```

### ✅ Resultado
El ejecutable se crea en: `dist/VTR_Checker.exe`

---

## 🔧 OPCIÓN 2: Compilación Manual (AVANZADO)

### Instalar PyInstaller
```bash
pip install pyinstaller
```

### Compilar
```bash
pyinstaller --onefile --windowed --name=VTR_Checker main.py
```

### Opciones:
- `--onefile` = Crea un archivo único (no carpeta)
- `--windowed` = Sin consola (interfaz limpia)
- `--icon=icon.ico` = Agrega icono personalizado
- `--add-data` = Incluye archivos adicionales

---

## 📋 ESTRUCTURA DEL PROYECTO

```
checker-profesional-/
├── main.py                 # Aplicación principal
├── checker_logic.py        # Lógica del checker
├── build_exe.py            # Script de compilación
├── requirements.txt        # Dependencias Python
├── config.json            # Configuración
├── install.bat            # Instalador (Windows)
├── install.sh             # Instalador (Linux/Mac)
├── run.bat                # Ejecutar (Windows)
├── run.sh                 # Ejecutar (Linux/Mac)
├── combos_ejemplo.txt     # Ejemplo de combos
├── proxies_ejemplo.txt    # Ejemplo de proxies
├── dist/
│   └── VTR_Checker.exe    # EJECUTABLE FINAL ⭐
└── build/                 # Archivos temporales (se elimina)
```

---

## ✨ DISTRIBUCIÓN DEL EXE

Una vez compilado, puedes distribuir el EXE:

### Opción A: Archivo Individual
- Comparte solo `dist/VTR_Checker.exe`
- Es portátil (funciona en cualquier PC)
- No requiere Python instalado

### Opción B: Carpeta Completa
- Incluye todo el proyecto en un ZIP
- Los usuarios pueden compilar su propio EXE
- Más seguro para algunos usuarios

### Opción C: Empaquetador
Usa herramientas como:
- **Inno Setup** - Crea instalador profesional
- **WinRAR SFX** - Auto-extrae y ejecuta
- **NSIS** - Instalador avanzado

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "pyinstaller command not found"
```bash
pip install --upgrade pyinstaller
```

### Error: "Module not found"
```bash
# Asegúrate de instalar todas las dependencias
pip install -r requirements.txt
```

### El EXE no ejecuta
```bash
# Compila con más verbosidad
pyinstaller --onefile --windowed --debug=all main.py
```

### EXE muy pesado (>500MB)
```bash
# PyInstaller incluye muchas librerías, es normal
# Usa UPX para comprimir (opcional)
pip install upx
pyinstaller --onefile --upx-dir=./upx main.py
```

---

## 📊 VERIFICAR LA COMPILACIÓN

Después de compilar, verifica:

```bash
# Navega a dist/
cd dist

# Verifica que el EXE existe
dir VTR_Checker.exe

# Ejecuta el EXE
VTR_Checker.exe
```

---

## 🎯 FINAL: RESUMEN RÁPIDO

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Compilar
python build_exe.py

# 3. Ejecutar (desde dist/)
dist/VTR_Checker.exe
```

**¡Listo! Tu ejecutable está lista para usar! 🚀**

---

## 📞 SOPORTE

Si encuentras problemas:
1. Verifica que Python esté en PATH
2. Actualiza PyInstaller: `pip install --upgrade pyinstaller`
3. Revisa que todos los archivos .py estén en la carpeta correcta
4. Intenta desde una carpeta sin caracteres especiales

---

**Versión**: 1.0.0
**Última actualización**: 2024
