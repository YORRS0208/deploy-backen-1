import requests
import mysql.connector as conx
from mysql.connector import Error

from .conexionBD import conexionData


class DatabaseManager:
	def __init__(self):
		self._conexion = None

	def open_connection(self):
		if self._conexion is None or not self._conexion.is_connected():
			self._conexion = conexionData().crear_conexion()

	def close_connection(self):
		if self._conexion and self._conexion.is_connected():
			self._conexion.close()
			self._conexion = None 
			# print("cerrado")

	def get_connection(self):
		return self._conexion


class DatabaseFacade():
	def __init__(self, db_manager):
		super().__init__()
		self.db_manager = db_manager
		self.facade = self.db_manager.get_connection()

	def update_conex(self):
		if self.facade and self.facade.is_connected():
			self.facade.commit()
			self.close_connection()
			print("ACTUALIZADO ")
			# self.facade.close()

	def open_db_connection(self):
		if not self.facade or not self.facade.is_connected():
			self.db_manager.open_connection()
			self.facade = self.db_manager.get_connection()
			# print("abierto")

	def close_connection(self):
		self.db_manager.close_connection()

	def apply_rollback(self):
		if self.facade:
			self.facade.rollback()

	# conexion abiertas para transacciones ...........................
	# ................................................................
	def execute_query(self, query, param=None, fetch_one=False):
		self.open_db_connection()
		cursor = None
		try:
			cursor = self.facade.cursor()
			cursor.execute(query, param)
			return cursor.fetchone() if fetch_one else cursor.fetchall()
		except conx.errors.ProgrammingError as err:
			# QMessageBox.warning(self, "Informe", f"{err.msg}")
			return False
		except Exception as e:
			# QMessageBox.warning(self, 'Error', f'Error inesperado:\n{str(e)}')
			return  False
		finally:
			if cursor:
				cursor.close()

	def execute_sql_transaccion(self, query, param=None):
		return self.execute_query(query, param, fetch_one=False)

	def execute_sqlone_transaccion(self, query, param=None):
		return self.execute_query(query, param, fetch_one=True)

	
	# conexion select y update para transacciones ....................
	# ................................................................
	def insert_transaccion(self, param=None, tabla=None):
		query, valores= self.parameters_insert(param, tabla)
		return self.execute_commit_transaccion(query, valores)

	def update_transaccion(self, param=None, tabla=None):
		query, valores= self.parameters_updates(param, tabla)
		return self.execute_commit_transaccion(query, valores)

	def insert_transaccion_varios(self, param=None, tabla=None):
		query, valores= self.parameters_insert_varios(param, tabla)
		return self.execute_commit_transaccion(query, valores)

	def execute_commit_transaccion(self, query, param=None):
		self.open_db_connection()
		try:
			cursor = self.facade.cursor()
			cursor.executemany(query, param)
			return True
		except conx.errors.IntegrityError as err:
			# QMessageBox.warning(self,'Informe', f'Autenticación de dato :\n{err.msg}')
			print(err.msg)
			self.facade.rollback()  
			return False
		except conx.errors.ProgrammingError as err:
			# QMessageBox.warning(self, "Informe ", f"{err.msg}")
			print(err.msg)
			self.facade.rollback() 
			return False
		except Exception as err:
			# QMessageBox.warning(self, 'Error', f'Error inesperado:\n{str(e)}')
			print(err.msg)
			self.facade.rollback() 
			return False
		finally:
			if cursor:
				cursor.close()	

	# funciones especiales .....................
	# ..........................................
	def parameters_insert(self, datos, tabla):
		placeholders = ', '.join(['%s'] * len(datos))
		columnas = ', '.join(datos.keys())
		valores = [tuple(datos.values())]
		query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
		return query, valores

	def parameters_insert_varios(self, datos, tabla):
		placeholders = ', '.join(['%s'] * len(datos[0]))
		columnas = ', '.join(datos[0].keys())
		valores = [tuple(x.values()) for x in datos]
		query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
		return query, valores

	def parameters_updates(self, datos, tabla):
		primera_fila = datos[0][0]	
		set_clause = ', '.join([f"{key} = %s" for key in datos[0][0].keys()])
		where_clause = ' AND '.join([f"{key} = %s" for key in datos[0][1].keys()])
		
		values = []
		for x in datos:
			values.append((tuple(x[0].values()) + tuple(x[1].values())))
		query = f" UPDATE {tabla} set {set_clause} where {where_clause}"
		return query, values

	def generate_parameters_select(self, param):
		conditions = []
		# ....................................
		primera_clave = list(param.keys())[0]
		clave_encontrada = next((clave for clave in param.keys() if primera_clave in clave), None)
		# ....................................

		if clave_encontrada.find('between') > -1:
			valor_clave = list(param.values())[0]
			eliminado = param.pop(clave_encontrada)
			for key, value in param.items():
				conditions.append("{} like '{}'".format(key, "%" + value + "%"))
				
			rango_fecha = 	"'" + valor_clave[0] + "'" + " and " + "'" + valor_clave[1] + "'"
			query = primera_clave + ' ' +  rango_fecha + ' and ' +  " and ".join(conditions)

		else:	
			for key, value in param.items():
				conditions.append("{} like '{}'".format(key, "%" + value + "%"))
			query =  " and ".join(conditions)
			
		return query
  
	def correlativo_sinquiebre_transaccion(self, param, idr):
		query = "select *from secuencia where ntabla =%s LIMIT 1"
		rst = self.execute_sqlone_transaccion(query, param)

		if rst:
			corrl = rst[1]
			clmaster = idr + str(corrl).zfill(7)	
			nuevo_corrl = int(corrl) + 1
		
			query_up = "UPDATE secuencia SET correlativo = %s WHERE ntabla = %s"
			param_up = [(str(nuevo_corrl),) + param ]
			if self.execute_commit_transaccion(query_up, param_up):
				return clmaster
			return []
		else:
			return None
