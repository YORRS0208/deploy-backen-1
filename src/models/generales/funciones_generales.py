from sentencias_sql_api import sentenciasConsultasApi

class FuncionesGenerales():
	def __init__(self, parent=None):
		self.consultas = sentenciasConsultasApi()

	def get_secuencia(self, tipo):
		param = (tipo,)
		rst = self.consultas.search_secuencia(param)

		print(rst)
		if not rst:
			return
