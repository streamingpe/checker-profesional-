# GUÍA RÁPIDA - VTR PRIME VIDEO CHECKER

## 🚀 Inicio Rápido (5 minutos)

### Opción A: Ejecutable (MÁS FÁCIL)
```
1. Descarga: VTR_Checker.exe desde /dist/
2. Ejecuta el archivo
3. Listo! No necesitas instalar nada
```

### Opción B: Desde Python
```bash
# Windows
install.bat
run.bat

# Linux/Mac
chmod +x install.sh run.sh
./install.sh
./run.sh
```

---

## 📝 PREPARAR TUS ARCHIVOS

### Archivo de Combos (RUT:PASSWORD)
Crea un archivo `combos.txt`:
```
25305194-9:micontraseña123
6645654-4:otrapwd456
5583542-K:pass789
```

**Formatos válidos de RUT:**
- Con puntos y guion: `25.305.194-9`
- Sin puntos: `253051949`
- Solo números: `25305194-9`

### Archivo de Proxies (Opcional)
Crea un archivo `proxies.txt`:
```
proxy1.com:8080
192.168.1.1:3128
proxy.vpn.net:9090
```

---

## 🎮 USAR EL CHECKER

1. **Abre VTR_Checker.exe**

2. **Haz clic en "📁 Cargar Combos"**
   - Selecciona tu archivo combos.txt
   - Verás: "✓ Combos cargados: 100 líneas"

3. **(Opcional) Haz clic en "🔗 Cargar Proxies"**
   - Selecciona tu archivo proxies.txt

4. **Haz clic en "▶ INICIAR"**
   - El checker comenzará a verificar cuentas
   - Verás resultados en tiempo real en la tabla

5. **Observa los resultados**
   - **✓ HITS**: Prime Video disponible
   - **⚠ CUSTOM**: Estado especial (Activado, Sin beneficios)
   - **✗ BAD**: Credenciales incorrectas

---

## 📊 ENTENDER LOS RESULTADOS

### Panel de Estadísticas (Arriba)
- **✓ HITS**: Cuentas con Prime disponible
- **⚠ CUSTOM**: Cuentas en estado especial
- **✗ BAD**: Cuentas inválidas
- **🏁 TOTAL**: Cuentas procesadas

### Tabla de Resultados (Izquierda)
- Muestra RUT, Estado y Detalles
- Botón 📋 para copiar resultado al portapapeles

### Logs en Vivo (Derecha)
- Muestra cada acción en tiempo real
- Timestamps de cada evento
- Información de conexión y errores

---

## ⚙️ COMPILAR TU PROPIO EXE

Si quieres crear tu propio ejecutable:

```bash
# 1. Asegurate de tener PyInstaller
pip install pyinstaller

# 2. Ejecuta el builder
python build_exe.py

# 3. El EXE se crea en: dist/VTR_Checker.exe
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### "No se puede ejecutar el programa"
- Instala Python 3.8+
- Ejecuta: `install.bat` (Windows) o `install.sh` (Linux/Mac)

### "Error: Combos no cargados"
- Verifica que el archivo sea .txt
- Revisa el formato: RUT:PASSWORD

### "Conexión rechazada"
- Verifica tu conexión a internet
- Intenta sin proxies primero
- La API puede estar bloqueada en tu país

### "CAPTCHA timeout"
- El servidor local (localhost:407) no está activo
- O necesitas una solución alternativa de CAPTCHA

### "Tabla vacía después de iniciar"
- Espera unos segundos a que cargue
- Verifica los logs (panel derecho)
- Comprueba la conexión

---

## 💡 TIPS PROFESIONALES

✅ **Siempre** valida tu archivo de combos primero
✅ **Usa proxies** de diferentes proveedores
✅ **Monitorea los logs** para detectar problemas
✅ **Guarda resultados HITS** en archivo aparte
✅ **No** uses el checker con mucha velocidad (spam banea)

---

## 📧 SOPORTE

- Reporta bugs en GitHub Issues
- Verifica la documentación en README.md
- Revisa config.json para parámetros avanzados

---

**¡Éxito con tu checker! 🚀**
