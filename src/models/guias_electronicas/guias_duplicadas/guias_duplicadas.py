from datetime import datetime
from sentencias_sql_api import sentenciasConsultasApi


# -- Obtenemos las guias remitentes que aparecen en varias Guias transportistas
class GuiasDuplicadasTransp():
	def __init__(self, parent=None):
		self.parent = None
		self.consultas = sentenciasConsultasApi()

	def get_guias_duplicadas(self):
		rst = self.consultas.extraer_guias_duplicadas_remit()
		rst_update = self.consultas.extraer_fecha_update(('GUIAS_ELECTRONICAS',))

		# -- Formateamos fecha .....
		fecha_dt = datetime.strptime(str(rst_update[0]), "%Y-%m-%d %H:%M:%S")
		fecha_formateada = fecha_dt.strftime("%d-%m-%Y,          a las :       %I:%M %p")

		
		if rst:
		    return [rst, fecha_formateada, self.total_registros_unicos(rst)], 200
		else:
		    return {'Message': 'Guias Duplicadas No encontradas'}, 400


	def total_registros_unicos(self, lista):
		# Usar un conjunto para almacenar combinaciones únicas de guías y fechas
		registros_unicos = set()
		for guias in lista:
			registros_unicos.add((guias[2],))

		return str(len(registros_unicos))