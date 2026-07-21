# VTR PRIME VIDEO CHECKER

## 📋 Descripción

Checker profesional para validar cuentas VTR y verificar acceso a Prime Video. Interfaz gráfica moderna con soporte para proxies y procesamiento en tiempo real.

## ✨ Características

✅ Interfaz gráfica intuitiva (PyQt5)
✅ Validación de RUT chileno
✅ Encriptación RSA de contraseñas
✅ Resolución automática de CAPTCHA
✅ Soporte para proxies
✅ Estadísticas en tiempo real
✅ Logs detallados
✅ Exportación de resultados
✅ Compilable a EXE
✅ Multithread

## 🚀 Inicio Rápido

### Windows
```bash
# 1. Instalar
install.bat

# 2. Ejecutar
run.bat
```

### Linux/Mac
```bash
# 1. Instalar
chmod +x install.sh
./install.sh

# 2. Ejecutar
./run.sh
```

## 📦 Compilar a EXE

```bash
# Instalar dependencias
pip install -r requirements.txt

# Compilar
python build_exe.py

# Resultado: dist/VTR_Checker.exe
```

## 📖 Documentación

- **GUIA_RAPIDA.md** - Guía de usuario paso a paso
- **COMPILAR_A_EXE.md** - Instrucciones de compilación
- **DOCUMENTACION_TECNICA.md** - Detalles técnicos y arquitectura

## 🎯 Uso

1. Carga archivo de combos (RUT:PASSWORD)
2. Opcionalmente carga proxies
3. Haz clic en "▶ INICIAR"
4. Observa resultados en tiempo real

## 📊 Resultados

- **✓ HITS** - Prime Video disponible
- **⚠ CUSTOM** - Estado especial
- **✗ BAD** - Credenciales inválidas

## 🔧 Requisitos

- Python 3.8+
- PyQt5
- requests
- cryptography

## 📝 Archivos de Ejemplo

- `combos_ejemplo.txt` - Formato de combos
- `proxies_ejemplo.txt` - Formato de proxies

## ⚙️ Configuración

Edita `config.json` para personalizar:
- Timeout de conexión
- Timeout de CAPTCHA
- Reintentos
- Delays

## 🐛 Troubleshooting

### "Python no encontrado"
- Instala Python 3.8+ desde https://www.python.org
- Marca "Add Python to PATH"

### "CAPTCHA timeout"
- El servidor local (localhost:407) no está activo
- Inicia tu solucionador de CAPTCHA

### "No se puede cargar combos"
- Verifica formato: RUT:PASSWORD
- Usa archivo .txt

## 📄 Licencia

MIT

## 👤 Autor

streamingpe

## 📞 Soporte

Reporta bugs en GitHub Issues

---

**Versión**: 1.0.0
**Última actualización**: 2024
