"""
Sistema de cifrado AES para datos sensibles.
Implementa funcionalidades similares a Bitwarden para proteger información confidencial.
"""

import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from django.conf import settings
from django.core.exceptions import ValidationError
import json
import secrets
import logging

logger = logging.getLogger(__name__)


class AESCrypto:
    """
    Clase para manejo de cifrado/descifrado AES-256-CBC.
    Implementa best practices de seguridad para protección de datos.
    """
    
    def __init__(self, master_key=None):
        """
        Inicializa el sistema de cifrado.
        
        Args:
            master_key (bytes, optional): Clave maestra para cifrado. 
                                        Si no se proporciona, usa la de settings.
        """
        self.master_key = master_key or self._get_master_key()
        self.algorithm = algorithms.AES(self.master_key)
        self.backend = default_backend()
    
    def _get_master_key(self):
        """Obtiene la clave maestra desde settings o genera una nueva."""
        key_from_settings = getattr(settings, 'ENCRYPTION_KEY', None)
        
        if key_from_settings:
            # Si la clave está en base64, decodificarla
            try:
                if len(key_from_settings) == 44:  # Base64 de 32 bytes
                    return base64.b64decode(key_from_settings.encode())
                elif len(key_from_settings) == 32:  # Ya son 32 bytes
                    return key_from_settings.encode()
                else:
                    raise ValueError("Invalid key length")
            except Exception:
                logger.warning("Invalid encryption key in settings, generating new one")
        
        # Generar nueva clave si no hay una válida
        new_key = os.urandom(32)  # 256 bits
        logger.warning(
            f"Generated new encryption key: {base64.b64encode(new_key).decode()}"
        )
        return new_key
    
    def generate_key_from_password(self, password: str, salt: bytes = None) -> tuple:
        """
        Genera una clave de cifrado derivada de una contraseña usando PBKDF2.
        
        Args:
            password (str): Contraseña del usuario
            salt (bytes, optional): Salt para la derivación. Si no se proporciona, se genera uno nuevo.
        
        Returns:
            tuple: (key, salt) - Clave derivada y salt usado
        """
        if salt is None:
            salt = os.urandom(16)  # 128 bits
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
            backend=self.backend
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def encrypt(self, plaintext: str, user_password: str = None) -> dict:
        """
        Cifra un texto usando AES-256-CBC.
        
        Args:
            plaintext (str): Texto a cifrar
            user_password (str, optional): Contraseña del usuario para cifrado adicional
        
        Returns:
            dict: Diccionario con datos cifrados y metadatos
        """
        try:
            # Convertir a bytes si es string
            if isinstance(plaintext, str):
                plaintext_bytes = plaintext.encode('utf-8')
            else:
                plaintext_bytes = plaintext
            
            # Generar IV aleatorio
            iv = os.urandom(16)  # 128 bits para AES
            
            # Si se proporciona contraseña de usuario, usar cifrado en capas
            if user_password:
                # Primera capa: cifrado con clave derivada de contraseña
                user_key, salt = self.generate_key_from_password(user_password)
                cipher_user = Cipher(algorithms.AES(user_key), modes.CBC(iv), backend=self.backend)
                encryptor_user = cipher_user.encryptor()
                
                # Padding para AES
                padder = PKCS7(128).padder()
                padded_data = padder.update(plaintext_bytes) + padder.finalize()
                
                # Cifrar con clave de usuario
                first_layer = encryptor_user.update(padded_data) + encryptor_user.finalize()
                
                # Segunda capa: cifrado con clave maestra
                iv2 = os.urandom(16)
                cipher_master = Cipher(self.algorithm, modes.CBC(iv2), backend=self.backend)
                encryptor_master = cipher_master.encryptor()
                
                # Padding para segunda capa
                padder2 = PKCS7(128).padder()
                padded_first_layer = padder2.update(first_layer) + padder2.finalize()
                
                # Cifrado final
                ciphertext = encryptor_master.update(padded_first_layer) + encryptor_master.finalize()
                
                return {
                    'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                    'iv': base64.b64encode(iv).decode('utf-8'),
                    'iv2': base64.b64encode(iv2).decode('utf-8'),
                    'salt': base64.b64encode(salt).decode('utf-8'),
                    'algorithm': 'AES-256-CBC-DOUBLE',
                    'iterations': 100000,
                    'version': '1.0'
                }
            else:
                # Cifrado simple con clave maestra
                cipher = Cipher(self.algorithm, modes.CBC(iv), backend=self.backend)
                encryptor = cipher.encryptor()
                
                # Padding
                padder = PKCS7(128).padder()
                padded_data = padder.update(plaintext_bytes) + padder.finalize()
                
                # Cifrar
                ciphertext = encryptor.update(padded_data) + encryptor.finalize()
                
                return {
                    'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                    'iv': base64.b64encode(iv).decode('utf-8'),
                    'algorithm': 'AES-256-CBC',
                    'version': '1.0'
                }
                
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise ValidationError(f"Error durante el cifrado: {str(e)}")
    
    def decrypt(self, encrypted_data: dict, user_password: str = None) -> str:
        """
        Descifra datos cifrados.
        
        Args:
            encrypted_data (dict): Datos cifrados del método encrypt()
            user_password (str, optional): Contraseña del usuario si se usó cifrado en capas
        
        Returns:
            str: Texto descifrado
        """
        try:
            # Extraer datos
            ciphertext = base64.b64decode(encrypted_data['ciphertext'].encode('utf-8'))
            iv = base64.b64decode(encrypted_data['iv'].encode('utf-8'))
            algorithm = encrypted_data.get('algorithm', 'AES-256-CBC')
            
            if algorithm == 'AES-256-CBC-DOUBLE':
                if not user_password:
                    raise ValueError("User password required for double-layer decryption")
                
                # Descifrado en capas
                iv2 = base64.b64decode(encrypted_data['iv2'].encode('utf-8'))
                salt = base64.b64decode(encrypted_data['salt'].encode('utf-8'))
                
                # Primera capa: descifrar con clave maestra
                cipher_master = Cipher(self.algorithm, modes.CBC(iv2), backend=self.backend)
                decryptor_master = cipher_master.decryptor()
                first_layer_padded = decryptor_master.update(ciphertext) + decryptor_master.finalize()
                
                # Quitar padding
                unpadder = PKCS7(128).unpadder()
                first_layer = unpadder.update(first_layer_padded) + unpadder.finalize()
                
                # Segunda capa: descifrar con clave de usuario
                user_key, _ = self.generate_key_from_password(user_password, salt)
                cipher_user = Cipher(algorithms.AES(user_key), modes.CBC(iv), backend=self.backend)
                decryptor_user = cipher_user.decryptor()
                plaintext_padded = decryptor_user.update(first_layer) + decryptor_user.finalize()
                
                # Quitar padding final
                unpadder2 = PKCS7(128).unpadder()
                plaintext_bytes = unpadder2.update(plaintext_padded) + unpadder2.finalize()
                
            else:
                # Descifrado simple
                cipher = Cipher(self.algorithm, modes.CBC(iv), backend=self.backend)
                decryptor = cipher.decryptor()
                plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()
                
                # Quitar padding
                unpadder = PKCS7(128).unpadder()
                plaintext_bytes = unpadder.update(plaintext_padded) + unpadder.finalize()
            
            return plaintext_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise ValidationError(f"Error durante el descifrado: {str(e)}")
    
    def encrypt_json(self, data: dict, user_password: str = None) -> dict:
        """
        Cifra un diccionario completo serializándolo a JSON.
        
        Args:
            data (dict): Diccionario a cifrar
            user_password (str, optional): Contraseña del usuario
        
        Returns:
            dict: Datos cifrados
        """
        json_string = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        return self.encrypt(json_string, user_password)
    
    def decrypt_json(self, encrypted_data: dict, user_password: str = None) -> dict:
        """
        Descifra y deserializa datos JSON cifrados.
        
        Args:
            encrypted_data (dict): Datos cifrados
            user_password (str, optional): Contraseña del usuario
        
        Returns:
            dict: Diccionario descifrado
        """
        json_string = self.decrypt(encrypted_data, user_password)
        return json.loads(json_string)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Genera un token seguro para verificaciones.
        
        Args:
            length (int): Longitud del token en bytes
        
        Returns:
            str: Token en base64
        """
        token_bytes = secrets.token_bytes(length)
        return base64.urlsafe_b64encode(token_bytes).decode('utf-8')


class VaultEntry:
    """
    Representa una entrada en el baúl de contraseñas cifrado.
    Similar a las entradas de Bitwarden.
    """
    
    def __init__(self, crypto_instance: AESCrypto = None):
        self.crypto = crypto_instance or AESCrypto()
    
    def create_entry(self, user_password: str, entry_data: dict) -> dict:
        """
        Crea una nueva entrada cifrada en el baúl.
        
        Args:
            user_password (str): Contraseña maestra del usuario
            entry_data (dict): Datos de la entrada (nombre, username, password, url, notas, etc.)
        
        Returns:
            dict: Entrada cifrada lista para almacenar
        """
        # Validar datos requeridos
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in entry_data:
                raise ValidationError(f"Campo requerido: {field}")
        
        # Estructura estándar de entrada
        vault_entry = {
            'id': self.crypto.generate_secure_token(16),
            'type': entry_data['type'],  # 'login', 'note', 'card', 'identity'
            'name': entry_data['name'],
            'favorite': entry_data.get('favorite', False),
            'created_at': entry_data.get('created_at'),
            'updated_at': entry_data.get('updated_at'),
            'data': {}
        }
        
        # Datos específicos por tipo
        if entry_data['type'] == 'login':
            vault_entry['data'] = {
                'username': entry_data.get('username', ''),
                'password': entry_data.get('password', ''),
                'url': entry_data.get('url', ''),
                'totp': entry_data.get('totp', ''),
                'notes': entry_data.get('notes', '')
            }
        elif entry_data['type'] == 'note':
            vault_entry['data'] = {
                'content': entry_data.get('content', ''),
                'notes': entry_data.get('notes', '')
            }
        elif entry_data['type'] == 'card':
            vault_entry['data'] = {
                'card_holder': entry_data.get('card_holder', ''),
                'card_number': entry_data.get('card_number', ''),
                'expiry_month': entry_data.get('expiry_month', ''),
                'expiry_year': entry_data.get('expiry_year', ''),
                'cvv': entry_data.get('cvv', ''),
                'notes': entry_data.get('notes', '')
            }
        elif entry_data['type'] == 'identity':
            vault_entry['data'] = {
                'first_name': entry_data.get('first_name', ''),
                'last_name': entry_data.get('last_name', ''),
                'email': entry_data.get('email', ''),
                'phone': entry_data.get('phone', ''),
                'address': entry_data.get('address', ''),
                'notes': entry_data.get('notes', '')
            }
        
        # Cifrar la entrada completa
        return self.crypto.encrypt_json(vault_entry, user_password)
    
    def decrypt_entry(self, encrypted_entry: dict, user_password: str) -> dict:
        """
        Descifra una entrada del baúl.
        
        Args:
            encrypted_entry (dict): Entrada cifrada
            user_password (str): Contraseña maestra del usuario
        
        Returns:
            dict: Entrada descifrada
        """
        return self.crypto.decrypt_json(encrypted_entry, user_password)
    
    def update_entry(self, encrypted_entry: dict, user_password: str, updates: dict) -> dict:
        """
        Actualiza una entrada existente.
        
        Args:
            encrypted_entry (dict): Entrada cifrada existente
            user_password (str): Contraseña maestra del usuario
            updates (dict): Datos a actualizar
        
        Returns:
            dict: Entrada actualizada y cifrada
        """
        # Descifrar entrada existente
        current_entry = self.decrypt_entry(encrypted_entry, user_password)
        
        # Aplicar actualizaciones
        for key, value in updates.items():
            if key == 'data':
                # Actualizar datos específicos
                current_entry['data'].update(value)
            else:
                current_entry[key] = value
        
        # Actualizar timestamp
        from django.utils import timezone
        current_entry['updated_at'] = timezone.now().isoformat()
        
        # Cifrar y retornar
        return self.crypto.encrypt_json(current_entry, user_password)


def generate_encryption_key() -> str:
    """
    Genera una nueva clave de cifrado segura para usar en settings.
    
    Returns:
        str: Clave de cifrado en base64
    """
    key = os.urandom(32)  # 256 bits
    return base64.b64encode(key).decode('utf-8')


def test_encryption():
    """
    Función de prueba para verificar el funcionamiento del cifrado.
    """
    crypto = AESCrypto()
    
    # Datos de prueba
    test_data = {
        'type': 'login',
        'name': 'Gmail',
        'username': 'usuario@gmail.com',
        'password': 'MiContraseñaSegura123!',
        'url': 'https://gmail.com',
        'notes': 'Cuenta principal de email'
    }
    
    user_password = 'ContraseñaMaestra123!'
    
    try:
        # Crear entrada
        vault = VaultEntry(crypto)
        encrypted_entry = vault.create_entry(user_password, test_data)
        print("✅ Cifrado exitoso")
        
        # Descifrar entrada
        decrypted_entry = vault.decrypt_entry(encrypted_entry, user_password)
        print("✅ Descifrado exitoso")
        
        # Verificar integridad
        assert decrypted_entry['data']['username'] == test_data['username']
        assert decrypted_entry['data']['password'] == test_data['password']
        print("✅ Integridad verificada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de cifrado: {e}")
        return False


if __name__ == '__main__':
    # Generar nueva clave si se ejecuta directamente
    print("Nueva clave de cifrado:")
    print(generate_encryption_key())
    print("\nPrueba de cifrado:")
    test_encryption()
