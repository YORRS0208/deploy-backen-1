from datetime import datetime
from .get_detracciones import InformacionDetracciones
from sentencias_sql_api import sentenciasConsultasApi


class UpdateDetraccionesBD():
	def __init__(self):
		self.consultas = sentenciasConsultasApi()
		self.detraccion = InformacionDetracciones()

	def save_detracciones_sunat_bd(self):
		hoy = datetime.now()
		lista_empresas = ['20512524380', '20563256380', '20606636556', '20604773459']

		lista = []
		lista_upd = []
		lista_status = []
		for x in lista_empresas:
			data = self.detraccion.get_lista_detracciones(x)
	
			if data[1] == 200:
				lista.extend(data[0])
				lista_upd.append((hoy, x))
				lista_status.append(('OK', x))
			else:
				lista_status.append(('401 : TOKEN INVALIDO', x))

		if not self.consultas.update_status_id_cache(lista_status):
			return

		if lista_upd:
			if not self.consultas.insert_detracciones_bd(lista):
				return
			if not self.consultas.update_tb_accesos_sunat(lista_upd):
				return

			# Genera listas de facturas de ventas y compras
			lista_ventas, lista_compras = self._procesar_facturas(lista)
			if not self.consultas.update_status_detra_ventas(lista_ventas):
				return
			if not self.consultas.update_status_detra_compras(lista_compras):
				return
		self.consultas.fin_conexion()
		

	def _procesar_facturas(self, lista):
		lista_compras = []
		lista_ventas = []	
		empresa_dict = {'20512524380': 1, '20563256380': 2, '20606636556': 3, '20604773459': 4}

		for item in lista:
			factura = f"{item[14]}-{item[15]}"
			empresa_origen = str(item[4])
			empresa_destino = str(item[7])

			# Procesa ventas
			if empresa_origen in empresa_dict:
				lista_ventas.append((
					'OK', factura, empresa_destino, empresa_dict[empresa_origen]
				))

			# Procesa compras
			if empresa_destino in empresa_dict:
				lista_compras.append((
					'OK', factura, empresa_origen, empresa_dict[empresa_destino]
				))

		return lista_ventas, lista_compras
		
		