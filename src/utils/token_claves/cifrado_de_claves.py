import base64
from cryptography.fernet import Fernet
import os

class CifradoTokenClaveMaestra():
    def __init__(self):
        pass
    
    def obtener_clave_cifrada(self):
        clave = os.getenv('CLAVE_CIFRADO')
        if clave is None:
            raise ValueError("No se ha encontrado la clave de cifrado en las variables de entorno")
        return clave.encode()  # Asegúrate de que la clave esté en bytes

    def generar_clave_maestra(self, clave_formulario):
        clave_form =  clave_formulario.encode()
        clave_form = Fernet.generate_key()
        return clave_form

    def cifrar_dato(self, token, clave_maestra):
        fernet = Fernet(clave_maestra)
        clave_cifrada = fernet.encrypt(token.encode())
        return clave_cifrada

    def descifrar_dato(self, dato_cifrado, clave_maestra):
        fernet = Fernet(clave_maestra)
        return fernet.decrypt(dato_cifrado).decode()