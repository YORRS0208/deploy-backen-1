import requests
from bs4 import BeautifulSoup
import time

import json
from typing import List, Optional
import logging
import requests
import zipfile
from flask import  jsonify
from io import BytesIO

from sentencias_sql_api import sentenciasConsultasApi
from ..parametros import _RUTA_PATH_TOKEN_GUIA

class ApisNetPe:
    BASE_URL = "https://api.apis.net.pe"

    def __init__(self, token: str = None) -> None:
        self.token = token

    def _get(self, path: str, params: dict):
        url = f"{self.BASE_URL}{path}"

        headers = {
            "Authorization": self.token, 
            "Referer": "https://apis.net.pe/api-tipo-cambio.html"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            logging.warning(f"{response.url} - invalida parameter")
            logging.warning(response.text)
        elif response.status_code == 403:
            logging.warning(f"{response.url} - IP blocked")
        elif response.status_code == 429:
            logging.warning(f"{response.url} - Many requests add delay")
        elif response.status_code == 401:
            logging.warning(f"{response.url} - Invalid token or limited")
        else:
            logging.warning(f"{response.url} - Server Error status_code={response.status_code}")
        return None

    def get_person(self, dni: str) -> Optional[dict]:
        return self._get("/v2/reniec/dni", {"numero": dni})

    def get_company(self, ruc: str) -> Optional[dict]:
        return self._get("/v2/sunat/ruc", {"numero": ruc})

    def get_exchange_rate(self, date: str) -> dict:
        return self._get("/v2/sunat/tipo-cambio", {"fecha": date})

    def get_exchange_rate_today(self) -> dict:
        return self._get("/v2/sunat/tipo-cambio", {})

    def get_exchange_rate_for_month(self, month: int, year: int) -> List[dict]:
        return self._get("/v2/sunat/tipo-cambio", {"month": month, "year": year})   


class ApiSunatRucDni:
    def __init__(self):
        self.token = self.leer_token_vigente()
        self.path_url = f"https://api-cpe.sunat.gob.pe/v1/contribuyente/parametros/"

    def leer_token_vigente(self):
        with open(_RUTA_PATH_TOKEN_GUIA, 'r') as file: 
            valor_token = file.read()
        return valor_token

    def _get(self, path, valor):
        _HEADERS = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        url = f"{self.path_url}{path}/{valor}"

        response = requests.get(url, headers=_HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data
        return None


    def get_company(self, ruc:str):
        datos = self._get('contribuyentes', ruc)
        data = datos.get('datosContribuyente')

        data_direccion = data.get('ubigeo')
        departamento = data_direccion.get('desDepartamento')
        provincia = data_direccion.get('desProvincia')
        distrito = data_direccion.get('desDistrito')
        
        direccion = data.get('desDireccion')
        texto_sin_espacios= " ".join(direccion.split())
        direccion_final = f"{texto_sin_espacios} - {departamento} - {provincia} - {distrito}"
        
        razonsocial = data.get('desNomApe')
        
        values = {
            'razonsocial': razonsocial,
            'direccion': direccion_final,

        }            
        return values
    
    def get_persona(self, ruc:str):
        datos = self._get('personas', ruc)
        
        print(datos)
        # data_direccion = data.get('ubigeo')
        # departamento = data_direccion.get('desDepartamento')
        # provincia = data_direccion.get('desProvincia')
        # distrito = data_direccion.get('desDistrito')
        
        # direccion = data.get('desDireccion')
        # texto_sin_espacios= " ".join(direccion.split())
        # direccion_final = f"{texto_sin_espacios} - {departamento} - {provincia} - {distrito}"
        
        # razonsocial = data.get('desNomApe')
        
        # values = {
        #     'razonsocial': razonsocial,
        #     'direccion': direccion_final,

        # }            
        return datos
    

    # https://api-cpe.sunat.gob.pe/v1/contribuyente/parametros/personas/43665349