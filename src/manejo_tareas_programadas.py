from datetime import datetime
import base64
import threading
import time
import random
import schedule

from sentencias_sql_api import sentenciasConsultasApi
from utils.token_claves.cifrado_de_claves import CifradoTokenClaveMaestra

#from models.detracciones.get_idcache_detracciones import ObtenerIdCacheDetracciones
#from models.detracciones.set_detracciones_bd import UpdateDetraccionesBD
#from models.guias_electronicas.get_token_guia import GetTokenGuiasElectronicas
#from models.guias_electronicas.update_lista_guias import UpdateGuiasElectronicasDeSunat
#from models.consultas_ruc.consulta_ruc import ApisNetPe


class ManejoTareasProgramadas():
	@staticmethod
	def start_scheduler_tareas():
		scheduler_thread = threading.Thread(target=ManejoTareasProgramadas.schedule_task)
		scheduler_thread.daemon = True 
		scheduler_thread.start()


	@staticmethod
	def schedule_task():
		# GUIAS ELECTRONICAS ........................
		# schedule. every(54).minutes.do(ManejoTareasProgramadas.get_token_guias)
		# schedule.every(35).minutes.do(ManejoTareasProgramadas.update_lista_guias_transportistas)
		# schedule.every(37).minutes.do(ManejoTareasProgramadas.update_status_guias_debaja)
		
		# schedule.every(10).seconds.do(ManejoTareasProgramadas.update_lista_guias_transportistas)
		#schedule.every(35).minutes.do(ManejoTareasProgramadas.update_status_guias_debaja_2)
		# schedule.every(10).seconds.do(ManejoTareasProgramadas.update_status_guias_debaja_2)

	
		# DETRACCIONES ...............................
		# schedule.every(2.8).hours.do(ManejoTareasProgramadas.get_idcache_detraccion)
		# schedule.every(1).hours.do(ManejoTareasProgramadas.update_detracciones)

		# ACTUALIZACION TIPO DE CAMBIO ...............
		# schedule.every().day.at("07:30:05").do(ManejoTareasProgramadas.update_tipo_cambio)
		
		while True:
			current_time = datetime.now().time()
			start_time = datetime.strptime("06:00", "%H:%M").time()
			end_time = datetime.strptime("23:58", "%H:%M").time()

			if start_time <= current_time <= end_time:
				schedule.run_pending()
				delay = random.randint(60, 180)
				time.sleep(delay)
			else:
				pass
			time.sleep(50)


	# ............................................................
	# DETRACCIONES ..............................................
	@staticmethod
	def get_idcache_detraccion(*args):
		try:
			consultas = sentenciasConsultasApi()
			rst = consultas.search_claves_sunat_para_detracciones()
		
			if not rst:
				return

			lista_status = []
			for accesos in rst:
				ruc, clave, usuario = accesos
				detra = ObtenerIdCacheDetracciones(str(int(ruc)), clave, usuario)
				id_cache = detra.get_id_cache()

				if id_cache:
					ManejoTareasProgramadas.guardar_id_cache(str(int(ruc)), id_cache, consultas)
					lista_status.append(('OK', ruc))
				else:
					lista_status.append(('NOT FOUND - SUNAT : TOKEN INVALIDO', ruc))
	
			if not consultas.update_status_id_cache(lista_status):
				return
			consultas.fin_conexion()

		except Exception as e:
			print(f"Error en tarea_update_detracciones: {e}")


	@staticmethod
	def guardar_id_cache(ruc, id_cache, conexion):
		instancia = CifradoTokenClaveMaestra()
		clave_maestra = instancia.generar_clave_maestra('idcache_detracciones')
		token_cifrado = instancia.cifrar_dato(id_cache, clave_maestra)
		token = base64.b64encode(token_cifrado).decode('utf-8')
		clave = base64.b64encode(clave_maestra).decode('utf-8')
	
		values = [(f'api_idcache_detraccion_{ruc}', token, clave)]
		hoy = datetime.now()
		update_cache = [(hoy, ruc)]
		
		if not conexion.insertar_idcache_detracciones(values):
			return
		if not conexion.update_accesos_sunat_cache(update_cache):
			return


	@staticmethod
	def update_detracciones():
		try:
			UpdateDetraccionesBD().save_detracciones_sunat_bd()
		except Exception as e:
			print(f"Error en actualizacion detracciones {e}")


	# -- GUIAS .................................................
	# ..........................................................
	@staticmethod
	def get_token_guias(*args):
		try:
			consultas = sentenciasConsultasApi()
			rst = consultas.search_claves_sunat()
		
			if rst:
				ruc, usuario, clave = rst[0]
				app = GetTokenGuiasElectronicas(ruc, usuario, clave)
				token_result = app.abrir_sunat() 
		
				if token_result:
					if not consultas.update_fecha_claves_sunat([(ruc,)]):
						return
					consultas.fin_conexion()
			else:
				return {'status': 'error', 'message': 'No se encontraron claves'} , 404
			consultas.cerrar_conexion()
		except Exception as e:
			print(f"Error en tarea_get_token_guias: {e}")


	@staticmethod
	def update_lista_guias_transportistas():
		try:
			UpdateGuiasElectronicasDeSunat().insertar_guias_fecha()
		except:
			print("Error al Obtener Guias desde Sunat")

	@staticmethod
	def update_status_guias_debaja():
		try:
			UpdateGuiasElectronicasDeSunat().reactualizar_guias_anuladas()
		except:
			print("Error al Obtener Guias desde Sunat")

	@staticmethod
	def update_status_guias_debaja_2():
		try:
			UpdateGuiasElectronicasDeSunat().reactualizar_guias_anuladas_anterior()
		except:
			print("Error al Obtener Guias desde Sunat")


	# -- TIPO DE CAMBIO ........................................
	# ..........................................................
	@staticmethod
	def update_tipo_cambio():
		# actualizamos el tipo de cambio del dia.
		lista_meses = {
            '1':'enero',
            '2':'febrero',
            '3':'marzo',
            '4':'abril',
            '5':'mayo',
            '6':'junio',
            '7':'julio',
            '8':'agosto',
            '9':'setiembre',
            '10':'octubre',
            '11':'noviembre',
            '12':'diciembre',
        }

		fecha = datetime.now()
		mes = lista_meses.get(str(fecha.month))
		
		try:
			clase = ApisNetPe('apis-token-10698.2BzCuElu4kghYNe9bZwok2zYbTj9XTvh')
			tipo_de_cambio = clase.get_exchange_rate(fecha).get('precioVenta')

			param = [( tipo_de_cambio, str(fecha.day), fecha.year)]
			# actualizamos base de datos
			consultas = sentenciasConsultasApi()

			if not consultas.update_tipo_cambio_bd(param, mes):
				return
			consultas.fin_conexion()
		except:
			consultas.cerrar_conexion()


	


 












