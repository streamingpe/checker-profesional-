# DOCUMENTACIÓN TÉCNICA - VTR PRIME VIDEO CHECKER

## 🏗️ ARQUITECTURA DEL PROYECTO

```
┌─────────────────────────────────────────┐
│         INTERFAZ GRÁFICA (PyQt5)        │
│  main.py - VTRCheckerApp                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     LÓGICA DE VERIFICACIÓN              │
│  checker_logic.py - CheckerWorker       │
│  - Validación RUT                       │
│  - Encriptación RSA                     │
│  - Resolución CAPTCHA                   │
│  - Consulta API VTR                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     APIS EXTERNAS                       │
│  - VTR Authentication                   │
│  - Prime Video API                      │
│  - CAPTCHA Solver                       │
└─────────────────────────────────────────┘
```

---

## 📋 ARCHIVOS Y SUS FUNCIONES

### main.py (1,232 líneas)
**Responsabilidad**: Interfaz gráfica y gestión de UI

**Clases principales**:
- `VTRCheckerApp` - Ventana principal
  - `setup_ui()` - Construye interfaz
  - `load_combos()` - Carga archivo de combos
  - `load_proxies()` - Carga archivo de proxies
  - `start_checker()` - Inicia verificación
  - `run_checker()` - Loop de verificación (thread)
  - `add_result()` - Añade resultado a tabla
  - `update_stats()` - Actualiza estadísticas

**Dependencias**:
- PyQt5 (interfaz)
- checker_logic (lógica)
- threading (procesamiento paralelo)

### checker_logic.py (381 líneas)
**Responsabilidad**: Lógica de verificación de cuentas

**Clases principales**:
- `CheckerWorker(QObject)` - Worker del checker
  - `validate_rut()` - Valida RUT chileno
  - `encrypt_password()` - Encripta con RSA
  - `solve_captcha()` - Resuelve CAPTCHA v2
  - `check_vtr()` - Verificación principal

**Flujo de check_vtr()**:
1. Parsea combo (RUT:PASSWORD)
2. Valida formato RUT
3. Conecta a sesión inicial VTR
4. Obtiene CAPTCHA sitekey
5. Resuelve CAPTCHA
6. Encripta contraseña
7. Envía datos de login
8. Verifica respuesta de autenticación
9. Consulta API de Prime Video
10. Procesa respuesta y retorna resultado

---

## 🔐 ALGORITMO DE VALIDACIÓN RUT

```python
# Entrada: "25.305.194-9"
# Salida: True, "25305194-9"

def validate_rut(rut_input):
    1. Limpiar formato (puntos, guiones)
    2. Separar dígito verificador (último carácter)
    3. Validar que sea número (excepto DV que puede ser K)
    4. Calcular DV esperado:
        a. Multiplicar cada dígito por [2,3,4,5,6,7,2,3,...]
        b. Sumar todos los productos
        c. Dividir suma entre 11
        d. Restar 11 - resto
        e. Si resultado es 11 → DV = 0
        f. Si resultado es 10 → DV = K
        g. Si resultado es otro → DV = ese número
    5. Comparar DV calculado con DV ingresado
    6. Retornar True si coinciden, False si no
```

---

## 🔒 ENCRIPTACIÓN RSA

**Clave pública VTR (Base64)**:
```
MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBANgDJ1D8IOc8ZQpzJCnLujRc9Dt06ckr
r1F8zTivMgAmFXlUv6Skbey+DZ4nZ/SAQgTFLpMm9i1/2BNabqFa5vsCAwEAAQ==
```

**Proceso**:
1. Decodificar clave de Base64
2. Cargar clave pública DER
3. Encriptar contraseña con padding PKCS1v15
4. Codificar resultado a Base64
5. Enviar en parámetro "password"

---

## 🤖 RESOLUCIÓN DE CAPTCHA

**Integración con servidor local**:
```
http://localhost:407/token
```

**Request**:
```json
{
  "url": "https://accounts.vtr.com",
  "sitekey": "6Ldz5XEaAAAAAHyzCrh1TK53A22e-FSx0ukqyhmS"
}
```

**Response**:
```json
{
  "token": "03AOLTBLR5Uj3...",
  "status": "success"
}
```

**Timeout**: 150 segundos

---

## 📡 FLUJO DE AUTENTICACIÓN VTR

### 1️⃣ GET inicial
```
GET /v2/auth/vtr/login.html?idp=vtr2&return=...
Headers: User-Agent
Response: Página de login + Formulario
```

### 2️⃣ POST de autenticación
```
POST /commonauth
Data:
  - name: RUT (sin DV)
  - username: RUT completo
  - password: Contraseña encriptada
  - g-recaptcha-response: Token CAPTCHA
  - sessionDataKey: ID de sesión
```

### 3️⃣ Validación de respuesta
```
if "login.fail.message" in response:
    return BAD (credenciales inválidas)
else:
    Continuar a verificación de Prime
```

### 4️⃣ Consulta API Prime Video
```
GET /v1/partnergw/affiliates/subscriptions?...
Headers:
  - Accept: application/json
  - Authorization: vtr-a11c019950-f84338973c
  
Response: JSON con estado de beneficios
```

---

## 📊 ESTRUCTURA DE RESULTADOS

```python
{
    'status': 'HITS' | 'CUSTOM' | 'BAD',
    'rut': '25305194-9',
    'captura': 'Descripción del resultado',
    'link': 'URL de activación' | None
}
```

### Estados posibles:
- **HITS**: `status: BINDING_PENDING` - Prime disponible sin activar
- **CUSTOM**: `status: BOUND` - Prime ya activado
- **CUSTOM**: Sin beneficios encontrados
- **BAD**: RUT inválido, credenciales incorrectas, error de conexión

---

## 🧵 THREADING Y CONCURRENCIA

**Modelo**: Productor-Consumidor

```
Thread Principal (UI)
    │
    ├─ Carga combos/proxies (UI thread)
    │
    └─ Inicia run_checker() en thread separado
        │
        └─ Para cada combo:
            ├─ Selecciona proxy (rotativo)
            ├─ Ejecuta check_vtr() (bloqueante)
            ├─ Emite señales de resultado (thread-safe)
            ├─ Actualiza progress bar
            └─ Delay de 0.5 segundos
```

**Señales PyQt5**:
- `log_signal` - Emite log en tiempo real
- `result_signal` - Emite resultado de verificación

---

## ⚙️ CONFIGURACIÓN (config.json)

```json
{
  "timeout_conexion": 15,        // segundos
  "timeout_captcha": 150,         // segundos
  "reintentos": 3,                // intentos
  "delay_entre_verificaciones": 0.5, // segundos
  "max_threads": 5                // threads paralelos
}
```

---

## 🎨 ESTILOS Y TEMAS

**Dark Mode Personalizado**:
- Fondo: `#0D1B2A` (azul muy oscuro)
- Paneles: `#1A2F4B` (azul oscuro)
- Borders: `#2E5C8F` (azul medio)
- Hover: `#4A90E2` (azul claro)

**Colores de estado**:
- HITS: `#00FF41` (verde)
- CUSTOM: `#FFA500` (naranja)
- BAD: `#FF6B6B` (rojo)
- TOTAL: `#00D4FF` (cyan)

---

## 📦 DEPENDENCIAS EXTERNAS

```
PyQt5==5.15.9           # GUI
requests==2.31.0        # HTTP
cryptography==41.0.7    # RSA
pyinstaller==6.1.0      # Compilación
```

---

## 🔧 VARIABLES DE ENTORNO (Opcional)

```bash
# Proxy CAPTCHA alternativo
export CAPTCHA_SOLVER_URL=http://localhost:407

# Timeout personalizado
export CHECKER_TIMEOUT=30

# Debug mode
export DEBUG=1
```

---

## 📈 OPTIMIZACIONES FUTURAS

1. **Pool de threads** - Procesar múltiples combos en paralelo
2. **Cache de sesiones** - Reutilizar sesiones VTR
3. **Rotación de proxies** - Cambiar proxy cada N intentos
4. **Retry automático** - Reintentar combos fallidos
5. **Exportar resultados** - CSV, JSON, Excel
6. **Estadísticas avanzadas** - Gráficos, tasas de éxito
7. **API REST** - Servir resultados vía HTTP
8. **Base de datos** - Almacenar histórico

---

## 🐛 DEBUGGING

### Ver logs en consola
```bash
python main.py
```

### Debug mode
```python
# En main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspeccionar requests
```python
import requests
requests.packages.urllib3.disable_warnings()
# Ver requests en Fiddler o Burp
```

---

## 📞 VERSIONES

| Versión | Cambios |
|---------|---------|
| 1.0.0   | Release inicial |
| 1.0.1   | Bug fixes (próximo) |
| 1.1.0   | Threading pool (próximo) |
| 2.0.0   | API REST (futuro) |

---

**Última actualización**: 2024
**Autor**: streamingpe
**Licencia**: MIT
