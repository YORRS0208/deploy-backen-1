from datetime import datetime
from unidecode import unidecode
import base64
import requests

from sentencias_sql_api import sentenciasConsultasApi
from utils.token_claves.cifrado_de_claves import CifradoTokenClaveMaestra


class InformacionDetracciones():
	def __init__(self):
		self.consultas = sentenciasConsultasApi()
		self.tk_cifrado = CifradoTokenClaveMaestra()

	def params_fechas(self, ruc):
		rst = self.consultas.search_ultima_fecha_detraccion((ruc,))
		hoy = datetime.now()

		if not rst:
			fecha = datetime.strftime(hoy, '%d/%m/%Y') 
		else:
			fecha = rst[0][0].strftime('%d/%m/%Y')		

		fecha_actual = datetime.strftime(hoy, '%d/%m/%Y')

		return fecha, fecha_actual

	def obtener_token_desde_bd(self, name_api):
		rst = self.consultas.search_token_por_api((name_api,))

		if not rst:
			return False

		token = base64.b64decode(rst[0])
		clave = base64.b64decode(rst[1])

		token_descifrado = self.tk_cifrado.descifrar_dato(token, clave)
		return token_descifrado


	def get_lista_detracciones(self, *args):
		url = "https://e-plataformaunica.sunat.gob.pe/v1/recaudacion/tributaria/declapago/detracciones/t/consultar"
		ruc, = args
		fecha, fecha_actual = self.params_fechas(ruc)

		# INFORMACION IDCACHE APIS - BASE DE DATOS
		key_api = f'api_idcache_detraccion_{ruc}' 
		try:
			token_descifrado = self.obtener_token_desde_bd(key_api) # DESCIFRAR TOKEN DE BASE 64
			
			params = {
				"fechaInicio": str(fecha),
				"fechaFin": str(fecha_actual),
				"tipoCuenta": "1",
				"tipoConsulta": "pagosIndividuales",
				"periodo": "",
				"_": "1726582574079"
			}
		
			headers = {
				"Idcache": token_descifrado,
				"Idformulario": "*MENU*"
			}

			response = requests.get(url, params=params, headers=headers)	
			if response.status_code == 200:
				data = response.json() 
				respuesta = data.get("resultado")
				lista = []
				for x in respuesta:
					proveedor = unidecode(str(x['des_prov']))
					adquiriente = unidecode(str(x['des_adq']))

					lista.append((
						x['cod_usuario_sol'],
						x['num_cuenta'],
						x['num_constancia'],
						x['per_tributario'],
						x['num_ruc_proveedor'],
						proveedor,
						x['tip_doc_adq'].lstrip('0'), 			# tipo de documento
						x['num_doc_adq'],
						adquiriente,
						x['fec_pago_desc'],
						x['mto_deposito_desc'],
						x['tip_bien'].lstrip('0'), 				# tipo de servicio
						x['tip_operacion'].lstrip('0'), 		# tipo de operacion
						x['cod_tipcomprobante'].lstrip('0'),	# Tipo de Comprobante
						x['num_serie'],
						x['num_comprobante'].lstrip('0'),
						x['num_pres']

					))
				return lista, 200

			else:
				return [], response.status_code
		except:
			return [],500


