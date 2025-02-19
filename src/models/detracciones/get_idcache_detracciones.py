import base64
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re


class ObtenerIdCacheDetracciones():
    def __init__(self, ruc, usuario, clave):
        self.ruc = str(int(ruc))
        self.usuario = str(usuario)
        self.clave = str(clave)

    def get_id_cache(self):        
        url = "https://api-seguridad.sunat.gob.pe/v1/clientessol/59d39217-c025-4de5-b342-393b0f4630ab/oauth2/j_security_check"
        
        payload = {
            'tipo': '2',
            'dni': '', 
            'custom_ruc': self.ruc,
            'j_username': self.usuario,
            'j_password': self.clave,
            'captcha': '', 
            'originalUrl': 'https://e-menu.sunat.gob.pe/cl-ti-itmenu2/AutenticaMenuInternetPlataforma.htm',
            'state': 'rO0ABXQA701GcmNEbDZPZ28xODJOWWQ4aTNPT2krWUcrM0pTODAzTEJHTmtLRE1IT2pBQ2l2eW84em5lWjByM3RGY1BLT0tyQjEvdTBRaHNNUW8KWDJRQ0h3WmZJQWZyV0JBaGtTT0hWajVMZEg0Mm5ZdHlrQlFVaDFwMzF1eVl1V2tLS3ozUnVoZ1ovZisrQkZndGdSVzg1TXdRTmRhbAp1ek5OaXdFbG80TkNSK0E2NjZHeG0zNkNaM0NZL0RXa1FZOGNJOWZsYjB5ZXc3MVNaTUpxWURmNGF3dVlDK3pMUHdveHI2cnNIaWc1CkI3SkxDSnc9'
        }    

    
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "content-type": "application/x-www-form-urlencoded",
            # 'Content-Type': 'application/json;chartset=utf-8',
            # "cookie": "RECUERDAME=RUC; RUC=20563256380; USR=LOTRANSA",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }


        session = requests.Session()
        response = session.post(url, data=payload, headers=headers)
       
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        if response.status_code == 200:
            try:
                for script in scripts[5]:
                    if 'idCache' in script:
                        # Usar regex para extraer el valor de idCache
                        match = re.search(r'idCache=([\'\"]?)([\w\d-]+\.[\w\d-]+\.[\w\d-]+)\1', script)
                        if match:
                            id_cache_value = match.group(2)
                            return id_cache_value
            except:
                # datos de acceso incorrectos
                return False
        else:
            return False 