
import os
from mysql.connector import connect, Error
from .xml_inicializacion import lecturaFileXml
import mysql.connector as conx

from config import config

class conexionData():
	def __init__(self):
		super().__init__()

	def crear_conexion(self):
		# servidor = os.getenv('MYSQL_HOST')
		# usuario = os.getenv('MYSQL_USER')
		# password = os.getenv('MYSQL_PAsSWORD')
		# database = os.getenv('MYSQL_DATABASE')
		servidor = lecturaFileXml.fnObtenDato("servidor")
		usuario  = lecturaFileXml.fnObtenDato("usuario")
		password = lecturaFileXml.fnObtenDato("password")
		database = lecturaFileXml.fnObtenDato("database")
		
		conMysql = None

		try:
			conMysql = connect(host    = servidor, 
								user     = usuario, 
								passwd   = password,
								database = database,
								sql_mode = "ALLOW_INVALID_DATES",
								auth_plugin = 'mysql_native_password'
										)
			if conMysql.is_connected():
				# print("conexion exitosa")
				return conMysql
		except Error as err:
			error_message = str(err)
			if err.errno ==  -1:
				return " El usuario ingresado no tiene acceso al Servidor"
			if err.errno == 1045 or "Access denied" in error_message:
				return " El usuario ingresado no tiene acceso al Servidor"
				# conMysql = False
			elif err.errno == 2003:
				return '* verifique que el servidor se encuentra encendido'
				# conMysql = False 	
			elif err.errno == 2005:
				return '* Servidor no se encuentra activo, Consulte con su area de soporte.\n'
				' o verifique que el servidor se encuentre encendido'
				# conMysql = False
			elif err.errno == 2013:
				return 'Servidor Desconectado\n** Intente en unos Minutos.'
				# conMysql = False
		return conMysql


	