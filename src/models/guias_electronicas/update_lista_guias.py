from datetime import datetime, timedelta
import requests
import uuid

from models.guias_electronicas.consulta_guias import ConsultasGuiasElectronicas
from sentencias_sql_api import sentenciasConsultasApi

class UpdateGuiasElectronicasDeSunat():
	def __init__(self):
		self.consultas = sentenciasConsultasApi()
		self.consulta_guia = ConsultasGuiasElectronicas()

	def insertar_guias_fecha(self):
		lista_empresas = ['20512524380', '20563256380', '20606636556', '20604773459']
		empresa_dict = {'20512524380': 1, '20563256380': 2, '20606636556': 3, '20604773459': 4}

		hoy = datetime.now()
		fecha = datetime.strftime(hoy, '%Y-%m-%d') 
		fecha = '2025-01-30'
		fecha_fin = '2025-01-31'

		try:
			for q in lista_empresas:
				array_bd = set(self.guias_by_empresa((empresa_dict.get(q), fecha, fecha_fin)))
				data_sunat = self.consulta_guia.get_lista_guias(q, '31', fecha, fecha_fin)

				secuencia_actual = int(self.secuencia_guias_transportistas())

				if data_sunat[1] == 200:
					data = data_sunat[0]

					if data:
						array_sunat = set([item[1] for item in data])
						array_unico = array_sunat - array_bd
						
						lista_guias = []
						lista_detalles = []	
						lista_guias_remit = []
						cliente_destino = []
						cliente_remit = []
					
						for x in array_unico:
							asiento = f"GETR-{str(secuencia_actual).zfill(8)}"

							n_guia = f"{q}-31-{x}"
							response_guia = self.consulta_guia.consultar_guia_comprobante(n_guia)
							if response_guia[1] == 200:
								data_guia = response_guia[0]
								# placas ...................
								if len(data_guia[4]) > 1:
									n_placa = data_guia[4][0]
									n_placa_2 = data_guia[4][1]
									tracto = f"{n_placa[:3]}-{n_placa[-3:]}"
									acoplado = f"{n_placa_2[:3]}-{n_placa_2[-3:]}"
									placas = f"{tracto} / {acoplado}"
								else:  
									tracto = f"{data_guia[4][0][:3]}-{data_guia[4][0][-3:]}"
									acoplado = ''
									placas = tracto

								# -- guias principales
								status_sunat = 'OK' if data_guia[7]  == '01' else 'NO'
								status_mf = 'NO' if status_sunat  == 'OK' else 'ANU'

								lista_guias.append((
									str(asiento), x, data_guia[6], data_guia[0], data_guia[2], tracto, placas, status_mf, 
									status_sunat, empresa_dict.get(q)
								))

								# -- Detalle de guias como placa, conductor, rutas etc
								lista_detalles.append((
									str(asiento), data_guia[7], data_guia[8], data_guia[9], tracto, acoplado, data_guia[10]
								))

								# -- Guias remitentes asociados
								for i in data_guia[11]:
									lista_guias_remit.append((asiento, i[0], i[1])) 
				
								# -- Agregar Clientes que no figuran en base de datos 
								cliente_remit.append((data_guia[0], data_guia[1]))
								cliente_destino.append((data_guia[2], data_guia[3]))
								cliente_remit.extend(cliente_destino)
								
							secuencia_actual += 1

						if array_unico:
							self.guardar_lista_guias(lista_guias, lista_detalles, lista_guias_remit)
							self.reactualizar_cliente_if_notexist(cliente_remit)
							self.actualiza_secuencia(secuencia_actual)
					self.update_fecha_extraccion('Token Activo')
					print("si paso")
		except:
			self.update_fecha_extraccion('401 - Token Inactivo')
			self.consultas.fin_conexion()
			return
			
		self.consultas.fin_conexion()

	def secuencia_guias_transportistas(self):
		rst = self.consultas.get_secuencia_actual(('guia_transp_sunat', ))
		return rst[1]

	def actualiza_secuencia(self, secuencia_actual):
		secuencia_up = secuencia_actual + 1
		if not self.consultas.set_update_secuencia([ (secuencia_up, 'guia_transp_sunat') ]):
			return True

	def guias_by_empresa(self, param):
		rst = self.consultas.last_guia(param)
		if not rst:
			return []
		array_modificado = [item[0] for item in rst]
		return  array_modificado

	def guias_baja_by_empresa(self, param):
		rst = self.consultas.get_guias_baja(param)
		if not rst:
			return []
		array_modificado = [item[0] for item in rst]
		return  array_modificado

	# ........................................
	def guardar_lista_guias(self, rst, rst_detalles, rst_guias_remit):
		if not self.consultas.update_guias_electronicas_transportistas(rst):
			return
		if not self.consultas.update_detalle_guias_electronicas(rst_detalles):
			return
		if not self.consultas.insert_guias_relacionadas(rst_guias_remit):
			return

	def reactualizar_cliente_if_notexist(self, datos):
		if not self.consultas.update_clientes(datos):
			return

	def update_fecha_extraccion(self, valor_token):
		param = [( datetime.now(), valor_token, 'GUIAS_ELECTRONICAS' )]
		if not self.consultas.update_fecha_guias_elec(param):
			return

		
	# -- Guias que fueron anuladas por sunat y hacer una reactualizacion de estatus
	# .............................................................................
	def reactualizar_guias_anuladas(self):
		lista_empresas = ['20512524380', '20563256380', '20606636556', '20604773459']
		empresa_dict = {'20512524380': 1, '20563256380': 2, '20606636556': 3, '20604773459': 4}

		# hoy = datetime.now()
		hoy = datetime.strptime('2024-10-31', '%Y-%m-%d')
		fecha_hoy = hoy.strftime('%Y-%m-%d')  
		fecha_anterior = hoy - timedelta(days=28)
		fecha_anterior_fmt = fecha_anterior.strftime('%Y-%m-%d')
		
		try:
			lista_anuladas = []
			for q in lista_empresas:
				array_bd = set(self.guias_baja_by_empresa((empresa_dict.get(q), fecha_anterior, hoy)))
				data_sunat = self.consulta_guia.get_lista_guias(q, '31', fecha_anterior_fmt, fecha_hoy, cod_estado='02')
				data = data_sunat[0]

				if data:
					array_sunat = set([item[1] for item in data])
					array_unico = array_sunat - array_bd
		
					for x in array_unico:
						lista_anuladas.append((
							'ANU',
							x,
							empresa_dict.get(q)
						))
			self.actualizar_estatus_sunat(lista_anuladas)
		except:
			pass
		
		self.consultas.fin_conexion()

	def reactualizar_guias_anuladas_anterior(self):
		lista_empresas = ['20512524380', '20563256380', '20606636556', '20604773459']
		empresa_dict = {'20512524380': 1, '20563256380': 2, '20606636556': 3, '20604773459': 4}

		lista_dias = [
			'2024-07-30',
			'2024-08-30', 
			'2024-09-30', 
			'2024-10-30', 
			'2024-11-30', 
			'2024-12-30', 
		]

		for x in lista_dias:
			hoy = datetime.strptime(x, '%Y-%m-%d')
			fecha_hoy = hoy.strftime('%Y-%m-%d')  
			# valor_days = 29 if fecha_hoy[-2:] == '30' else 30
			
			fecha_anterior = hoy - timedelta(days=29)
			fecha_anterior_fmt = fecha_anterior.strftime('%Y-%m-%d')
			
			# try:
			lista_anuladas = []
			for q in lista_empresas:
				array_bd = set(self.guias_baja_by_empresa((empresa_dict.get(q), fecha_anterior, hoy)))
				data_sunat = self.consulta_guia.get_lista_guias(q, '31', fecha_anterior_fmt, fecha_hoy, cod_estado='02')
				data = data_sunat[0]

				if data:
					array_sunat = set([item[1] for item in data])
					array_unico = array_sunat - array_bd
				
					for j in array_unico:
						lista_anuladas.append((
							'ANU',
							j,
							empresa_dict.get(q)
						))

			self.actualizar_estatus_sunat(lista_anuladas)
			# print(array_unico)
			# print(lista_anuladas)
			# except:
			# 	pass
			
		self.consultas.fin_conexion()

	def actualizar_estatus_sunat(self, rst):
		if not self.consultas.update_status_sunat(rst):
			return
		






































# byte_id = bytes.fromhex(data_guia[5]) 