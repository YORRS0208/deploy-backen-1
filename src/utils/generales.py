import bcrypt
from argon2 import PasswordHasher


def get_secuencia_actual(param):
	db_manager = DatabaseManager()
	self.consultas_exe = DatabaseFacade(db_manager)


	query = "select *from secuencia where ntabla =%s LIMIT 1"
	rst =conexion.execute_sqlone(query, param)

	if rst:
		corrl = rst[1]
		clmaster = str(corrl)
		return clmaster
	else:
		return None	

def set_update_secuencia(param):
	correlativo, ncampo = param
	query_up = "UPDATE secuencia SET correlativo = %s WHERE ntabla = %s"
	param_up = [(str(correlativo),) + ncampo ]

	if not conexion.execute_commit(query_up, param_up):
		return []
	conexion.update_conex()



# -- Funciones para cifrar uy descifrar contraseñas Base de Datos ..........
# def cifrar_contraseña(contraseña_plana):
#     contraseña_bytes = contraseña_plana.encode('utf-8')
#     # Generar un salt (valor aleatorio) y cifrar la contraseña
#     salt = bcrypt.gensalt()
#     contraseña_cifrada = bcrypt.hashpw(contraseña_bytes, salt)
#     return contraseña_cifrada.decode('utf-8')

# def verificar_contraseña(contraseña_plana, contraseña_cifrada):
#     contraseña_bytes = contraseña_plana.encode('utf-8')
#     # Comparar la contraseña ingresada con el hash almacenado
#     return bcrypt.checkpw(contraseña_bytes, contraseña_cifrada.encode('utf-8'))


def cifrar_contraseña(contrasenia_plana):
	ph = PasswordHasher()
	contrasenia_cifrada = ph.hash(contrasenia_plana)
	return contrasenia_cifrada

def verificar_contraseña(constrasenia_plana, contrasenia_cifrada):
	ph = PasswordHasher()
	try:
	    return ph.verify(contrasenia_cifrada, constrasenia_plana)
	except:
		return False

# print(cifrar_contraseña('F43959951#f0208'))
# print(cifrar_contraseña('E74610611#e0208'))
# print(cifrar_contraseña('F43959951#f0208'))
# print(verificar_contraseña(
# 	'43665346#p',
# 	'$argon2id$v=19$m=65536,t=3,p=4$6I10LkaNAf4inSaQz4G+Gw$D+kOWVIYglqb2QFtakmrgyja/9UT36iQW06u1fTJmD4')
# )


