from database.sql_statement import DatabaseManager, DatabaseFacade

class sentenciasConsultasApi():
	def __init__(self):
		super().__init__()
		db_manager = DatabaseManager()
		self.consultas_exe = DatabaseFacade(db_manager)
		
	def cerrar_conexion(self):
		self.consultas_exe.close_connection()

	def fin_conexion(self):
		self.consultas_exe.update_conex()

	# -- Consultas usuario Bd ................
	def get_info_usuario(self, param):
		query = " SELECT id_usuario, password, username from usuarios_web where id_usuario=%s"
		return self.consultas_exe.execute_sqlone_transaccion(query, param)


	# -- Manejo de secuencuias especiales ..............
	def get_secuencia_actual(self, param):
		query = "select *from secuencia where ntabla =%s LIMIT 1"
		return self.consultas_exe.execute_sqlone_transaccion(query, param)

	def set_update_secuencia(self, param):
		query = "UPDATE secuencia SET correlativo=%s WHERE ntabla = %s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def search_ultima_fecha_detraccion(self, param):
		query = (
			" SELECT max(fecha) from tbdetracciones where rucp=%s"
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)

	def search_claves_sunat(self):
		query = " SELECT ruc, usuario, clave from tb_accesos_sunat order by fecha_update asc limit 1"
		return self.consultas_exe.execute_sql_transaccion(query)

	def search_claves_sunat_para_detracciones(self):
		query = " SELECT ruc, usuario, clave from tb_accesos_sunat"
		return self.consultas_exe.execute_sql_transaccion(query)

	def update_fecha_claves_sunat(self, param):
		query = " UPDATE tb_accesos_sunat set fecha_update= NOW()"
		query += " WHERE ruc = %s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True


	# TOKEN DE APIS VARIAS .......................................
	def search_token_por_api(self, param):
		query = (
			" SELECT token_cifrado, clave_maestra_cifrada from tokens_api "
			" where name_api = %s limit 1"
		)
		return self.consultas_exe.execute_sqlone_transaccion(query, param)


	def insertar_idcache_detracciones(self, param):
		query = (
		        " INSERT INTO tokens_api (name_api, token_cifrado, clave_maestra_cifrada)"
		        " VALUES (%s, %s, %s)"
		        " ON DUPLICATE KEY UPDATE "
		        " token_cifrado = VALUES(token_cifrado),"
		        " clave_maestra_cifrada = VALUES(clave_maestra_cifrada)"
		    )
		return self.consultas_exe.execute_commit_transaccion(query, param)


	# DETRACCIONES ACTUALIZACION .................................
	def insert_detracciones_bd(self, param):
		query = "INSERT INTO tbdetracciones (usuario, cuenta, constancia, periodo, rucp, proveedor, tipod,"
		query += " ruca, adquiriente, fecha, monto, bien, tipoo, tipoc, serie, numero, numeropago) "
		query += " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
		query += " ON DUPLICATE KEY UPDATE "
		query += " usuario = VALUES(usuario), "
		query += " serie = VALUES(serie), "
		query += " numero = VALUES(numero) "
		    
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def update_tb_accesos_sunat(self, param):
		query = " UPDATE tb_accesos_sunat set fecha_detra_update=%s where ruc=%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def update_status_id_cache(self, param):
		query = " UPDATE tb_accesos_sunat set status_cache=%s where ruc =%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def update_accesos_sunat_cache(self, param):
		query = " UPDATE tb_accesos_sunat set fecha_idcache_update=%s where ruc=%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def update_status_detra_ventas(self, param):
		query = " UPDATE factura_ventas set status_dt=%s where nfactura=%s and ruc=%s and empresa=%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True
	
	def update_status_detra_compras(self, param):
		query = " UPDATE flujo_documentario set status_detra=%s where concat(serie, '-', numero)=%s and ruc=%s and empresa=%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):		
			return True

	# CONSULTAS RUC SUNAT ........................................
	def clientes_all(self):
		query = " SELECT ruc from clientes order by ruc desc limit 25 "
		return self.consultas_exe.execute_sql_transaccion(query)


	# CONSULTAS TIPO DE CAMBIO ...................................
	def update_tipo_cambio_bd(self, param, mes):
		query = f"UPDATE catalogo_tipoc set {mes}=%s where dia=%s and periodo=%s"	
		if self.consultas_exe.execute_commit_transaccion(query, param):		
			return True

	# GUIAS ELECTRONICAS .........................................
	def update_guias_electronicas_transportistas(self, param):
		query = (
			" INSERT INTO guias_electronicas (id_guia, n_guia, fecha, ruc_remite, ruc_destino, "
			" ruc_pagador, placas, status_flete, status_sunat, empresa) "
			" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
			" ON DUPLICATE KEY UPDATE "
			# " status_flete = VALUES (status_flete), "
			" status_sunat = VALUES(status_sunat) "
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):		
			return True

	def update_detalle_guias_electronicas(self, param):
		query = (
			" INSERT IGNORE INTO guias_electronicas_detalle "
			" (id_guia_detalle, cod_estado, partida, llegada, tracto, acoplado, licencia) "
			" VALUES(%s,%s,%s,%s,%s,%s,%s)"
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):		
			return True

	def insert_guias_relacionadas(self, param):
		query = (
			" INSERT IGNORE INTO guias_electronicas_relaciones "
			" (id_guia, serie, correlativa)"
			" values(%s,%s,%s)"	
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):		
			return True

	def update_clientes(self, param):
		query = (
			" INSERT IGNORE INTO clientes "
			" (ruc, razonsocial) VALUES (%s,%s)"
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):		
			return True
			
	def update_fecha_guias_elec(self, param):
		query = " UPDATE tb_update_consultas_sunat set fecha_update=%s, observacion=%s where tipo=%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):		
			return True

	def last_guia(self, param):
		query = (
			" SELECT n_guia from guias_electronicas where empresa=%s "
			" and DATE(fecha) between %s and %s order by fecha desc"
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)

	def get_guias_baja(self, param):
		query = (
			" SELECT n_guia from guias_electronicas where empresa=%s "
			" and DATE(fecha) between %s and %s "
			" and status_sunat = 'NO' order by fecha desc"
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)


	def update_status_sunat(self, param):
		query = " UPDATE guias_electronicas set status_sunat = 'NO', status_flete=%s where n_guia=%s and empresa=%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):		
			return True


	# -- guias Duplicadas ...............
	def extraer_guias_duplicadas_remit(self):
		query = (
			" SELECT te.ncomercial AS empresa, "
			" concat(ger.serie, '-', ger.correlativa) AS guias_remit, "
			" group_concat(distinct n_guia separator ',\n ') as guia_transp, "
			" group_concat(DISTINCT ge.placas ORDER BY ge.n_guia separator ',\n') as placas,"
			" group_concat(date_format(fecha, '%d-%m-%Y') separator ',\n ') as n_fechas, "
			" c1.razonsocial as remitente, c2.razonsocial as destinatario, "
			" COUNT(DISTINCT ge.n_guia) AS N_Repetidas  "

			" FROM guias_electronicas ge "
			" INNER JOIN  guias_electronicas_relaciones ger  ON ger.id_guia = ge.id_guia "
			" inner join clientes c1 on c1.ruc = ge.ruc_remite "
			" inner join clientes c2 on c2.ruc = ge.ruc_destino "
			" inner join tempresas te on te.codigo = ge.empresa "
			" where ge.status_sunat = 'OK' "
			" AND fecha BETWEEN DATE_SUB(CURDATE(), INTERVAL 8 MONTH) AND DATE_ADD(CURDATE(), INTERVAL 2 DAY)"
			" and ger.condicion = 'N'"
			" GROUP BY concat(ger.serie, '-', ger.correlativa), ge.ruc_remite, ge.empresa "
			" HAVING COUNT(DISTINCT ge.n_guia) > 1 "
			" order by ge.fecha desc"
		)
		return self.consultas_exe.execute_sql_transaccion(query)

	def extraer_fecha_update(self, param):
		query = " SELECT fecha_update, observacion FROM tb_update_consultas_sunat where tipo=%s limit 1"
		return self.consultas_exe.execute_sqlone_transaccion(query, param)



# WITH duplicadas AS (
#     SELECT concat(ger.serie, '-', ger.correlativa) AS guias_remit,
#         ge.empresa, ge.ruc_remite, COUNT(DISTINCT ge.n_guia) AS repetidas
#     FROM guias_electronicas ge
#     INNER JOIN guias_electronicas_relaciones ger ON ger.id_guia = ge.id_guia
#     WHERE ger.condicion = 'N'
# 	AND fecha BETWEEN DATE_SUB(CURDATE(), INTERVAL 8 MONTH) AND DATE_ADD(CURDATE(), INTERVAL 2 DAY)
#     GROUP BY concat(ger.serie, '-', ger.correlativa), ge.empresa, ge.ruc_remite
#     HAVING COUNT(DISTINCT ge.n_guia) > 1
# )

# SELECT 
#     te.ncomercial AS empresa, concat(ger.serie, '-', ger.correlativa) AS guias_remit,
#     c1.razonsocial AS remitente, c2.razonsocial AS destinatario,
#     ge.status_sunat, n_guia AS guia_transp,  ge.placas,
#     DATE_FORMAT(fecha, '%d-%m-%Y') AS n_fecha
# FROM guias_electronicas ge
# INNER JOIN guias_electronicas_relaciones ger ON ger.id_guia = ge.id_guia
# INNER JOIN clientes c1 ON c1.ruc = ge.ruc_remite
# INNER JOIN clientes c2 ON c2.ruc = ge.ruc_destino
# INNER JOIN tempresas te ON te.codigo = ge.empresa
# INNER JOIN duplicadas d ON d.guias_remit = concat(ger.serie, '-', ger.correlativa) AND d.empresa = ge.empresa AND d.ruc_remite = ge.ruc_remite
# WHERE  ge.status_sunat = 'NO' -- Solo mostramos las guías anuladas
# ORDER BY fecha DESC
