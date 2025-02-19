import base64
import requests
import json
from datetime import datetime

from sentencias_sql_api import sentenciasConsultasApi


class GetTokenKeyFacil():
	def __init__(self):
		self._url= "https://api.vitekey.com/keyid/accounts/authentication/signin"

	def get_token(self):
		payload = {
			"email": "facturacion@transcargopaucar.com",
			"password": "TRANSCARGO2024"
		}

		try:
			response = requests.post(self._url, json=payload)
		
			if response.status_code == 200:
				response_data = response.json()
				# print(response_data)
				self.guardar_token('20512524380', response_data)

			else:
				print(f"Error: Código de estado {response_.status_code}")
				
		except requests.exceptions.RequestException as e:
			print("Ocurrió un error en la solicitud:", e)

	def guardar_token(self, ruc, token):
		valor_token = token.get('access_token')
		valor_clave = token.get('sin_clave_acceso')
		
		token_bytes = valor_token.encode("utf-8")
		clave_bytes = valor_token.encode("utf-8")
		values = [(f'api_token_keyfacil_{ruc}', token, clave)]
		
		if not conexion.insertar_idcache_detracciones(values):
			return
		
		consultas.fin_conexion()

	def extraer_token_key_facil(self):
		pass
		# rst = 
		# token_recuperado = token_bytes.decode("utf-8")
		# print(token_recuperado)
		# print(self.extraemos_fecha_vcto(token_recuperado))

	def extraemos_fecha_vcto(self, token):
		payload_b64 = token.split(".")[1] 
		payload_json = base64.urlsafe_b64decode(payload_b64 + "==").decode("utf-8")
		payload = json.loads(payload_json)

		exp_timestamp = payload.get("exp")
		exp_date = datetime.utcfromtimestamp(exp_timestamp)
		date_formato = datetime.strftime(exp_date, '%d-%m-%Y')
		return f"Fecha de expiración:, {date_formato}"



gg = GetTokenKeyFacil()
gg.get_token()