# VTR PRIME VIDEO CHECKER - Profesional

Checker profesional para validar cuentas VTR y verificar acceso a Prime Video.

## 🎯 Características

✅ Interfaz gráfica moderna (Dark Mode)
✅ Validación de RUT chileno
✅ Verificación de Prime Video
✅ Carga de combos (credenciales)
✅ Carga de proxies
✅ Estadísticas en tiempo real (HITS, CUSTOM, BAD, TOTAL)
✅ Logs en vivo
✅ Tabla de resultados con detalles
✅ Ejecutable EXE portátil

## 🚀 Instalación Rápida

### Opción 1: Usar el EXE (Recomendado)

1. Descarga `VTR_Checker.exe` desde `/dist/`
2. Ejecuta el archivo
3. ¡Listo! No necesitas instalar nada

### Opción 2: Desde Python

```bash
# 1. Clonar o descargar el proyecto
git clone https://github.com/streamingpe/checker-profesional-

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python main.py
```

## 📦 Compilar tu propio EXE

```bash
python build_exe.py
```

Esto creará un ejecutable en la carpeta `dist/`

## 📝 Cómo Usar

### 1. Preparar archivo de Combos

Crea un archivo `combos.txt` con el formato:
```
25305194-9:tu_contraseña
6645654-4:tu_contraseña
5583542-K:tu_contraseña
```

### 2. Preparar archivo de Proxies (Opcional)

Crea un archivo `proxies.txt`:
```
proxy1.com:8080
proxy2.com:8080
192.168.1.1:3128
```

### 3. Usar el Checker

1. Abre **VTR_Checker.exe**
2. Haz clic en **"📁 Cargar Combos"** y selecciona tu archivo
3. (Opcional) Haz clic en **"🔗 Cargar Proxies"**
4. Haz clic en **"▶ INICIAR"**
5. Observa los resultados en tiempo real

## 📊 Significado de Resultados

- **✓ HITS**: Prime Video disponible (Pendiente de activación)
- **⚠ CUSTOM**: Estado especial (Activado, Sin beneficios)
- **✗ BAD**: Credenciales inválidas o error

## 🔧 Requisitos Previos

- **Windows 7+** (para el EXE)
- **Python 3.8+** (si ejecutas desde código)
- **Servidor CAPTCHA** local en `http://localhost:407` (opcional)

## 📋 Archivos del Proyecto

```
├── main.py                  # Aplicación principal (GUI)
├── checker_logic.py         # Lógica del checker
├── build_exe.py            # Script para compilar EXE
├── requirements.txt        # Dependencias Python
├── README.md               # Este archivo
└── dist/
    └── VTR_Checker.exe     # Ejecutable final
```

## 🚨 Solución de Problemas

### El checker no conecta a la API VTR
- Verifica tu conexión a internet
- Intenta sin proxies primero
- Comprueba que la API no esté bloqueada en tu país

### Error con CAPTCHA
- Asegúrate de que el servidor local (localhost:407) esté activo
- O usa una solución de CAPTCHA alternativa

### No se genera el EXE
```bash
# Actualiza PyInstaller
pip install --upgrade pyinstaller

# Intenta nuevamente
python build_exe.py
```

## ⚠️ Disclaimer

Este proyecto es solo con fines educativos. El usuario es responsable del uso que le dé.

## 📧 Contacto

Para reportar bugs o sugerencias, abre un issue en GitHub.

---

**Versión**: 1.0.0
**Última actualización**: 2024
