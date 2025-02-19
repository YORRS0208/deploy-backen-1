from database.sql_statement import DatabaseManager, DatabaseFacade

class SentenciasLiquidacionViajes():
	def __init__(self):
		super().__init__()
		db_manager = DatabaseManager()
		self.consultas_exe = DatabaseFacade(db_manager)
		
	def cerrar_conexion(self):
		self.consultas_exe.close_connection()

	def fin_conexion(self):
		self.consultas_exe.update_conex()

	# ----------------------------------------
	def insert_liquidacion_viajes(self, param):
		query = (
			" INSERT INTO liquidacion_viajes (id_registro, fecha, empresa, conductor, status, ref_saldo_actual)"
			" VALUES (%s,%s,%s,%s,%s,%s)"
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def insert_id_liqui_en_depositos(self, param):
		query = (
			" INSERT INTO liquidacion_viajes_depositos (id_deposito, id_liqui) "
			" values(%s,%s)"
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	# -- Guias para liquidacion .......................
	def get_lista_guias_por_id(self, param):
		query = (
			" SELECT n_guia, n_guia , lvg.id_liqui as guias_liqui "
			" from guias_electronicas ge "
			" INNER JOIN guias_electronicas_detalle ged on ged.id_guia_detalle = ge.id_guia  "
			" left join liquidacion_viajes_guias lvg on concat(lvg.serie , '-', lvg.numero) = ge.n_guia  "
			" where ge.fecha BETWEEN DATE_SUB(CURDATE(), INTERVAL 10 DAY) AND DATE_ADD(CURDATE(), INTERVAL 1 DAY)  "
			" and ged.tracto = %s and ge.empresa= %s "
			" and ge.status_sunat = 'OK' "
			" having guias_liqui is null "
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)

	def get_lista_guias_detallado_por_id(self, param):
		query = (
			" SELECT n_guia, n_guia , "
			" c1.razonsocial, c2.razonsocial,"
			" ged.partida, ged.llegada,"
			" lvg.id_liqui as guias_liqui, "
			" lvg.efectivo AS ref_efectivo "
			" from guias_electronicas ge "
			" INNER JOIN guias_electronicas_detalle ged on ged.id_guia_detalle = ge.id_guia  "
			" left join liquidacion_viajes_guias lvg on concat(lvg.serie , '-', lvg.numero) = ge.n_guia  "
			" inner join clientes c1 on c1.ruc = ge.ruc_remite"
			" inner join clientes c2 on c2.ruc = ge.ruc_destino"
			" where ge.fecha BETWEEN DATE_SUB(CURDATE(), INTERVAL 10 DAY) AND DATE_ADD(CURDATE(), INTERVAL 1 DAY)  "
			" and ged.tracto = %s and ge.empresa= %s"
			" and ge.status_sunat = 'OK' "
			" having guias_liqui is null OR ref_efectivo = 'NO' "
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)

	def get_ultima_liquidacion(self, param):
		query =(
			" SELECT date_format(fecha, '%d-%m-%y'), id_registro,"
			" coalesce (group_concat( distinct concat(serie, '-', numero) separator ', '), '-') as nguias ,"
			
			" (SELECT coalesce(SUM(monto), 0) "
			" FROM liquidacion_viajes_detalle "
			" WHERE id_registro = lv.id_registro) AS t_liqui,"
			
			" lv.status, ref_saldo_actual "
			" from liquidacion_viajes lv"
			" left join liquidacion_viajes_guias lvg on lvg.id_liqui = lv.id_registro"
			" where lv.conductor =%s "
			" AND lv.status = 'AV'"
		) 
		return self.consultas_exe.execute_sql_transaccion(query, param)

	def get_numero_guia(self, param): 
		query = " SELECT n_guia from guias_electronicas where n_guia=%s and empresa=%s limit 1"
		return self.consultas_exe.execute_sqlone_transaccion(query, param)

	def insertar_guia_liquidacion(self, param):
		query = (
			" INSERT INTO liquidacion_viajes_guias (id_liqui, serie, numero)"
			" values(%s,%s,%s)"
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def insertar_detalle_gastos_image(self, param):
		query = (
			"INSERT INTO liquidacion_viajes_detalle (id_registro, fecha, tipo_gasto, "
			" nro_dcto, forma_pago, detalle_otros, galones_comb, monto, image_url)"
			" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def insertar_detalle_gastos(self, param):
		query = (
			"INSERT INTO liquidacion_viajes_detalle (id_registro, fecha, tipo_gasto, "
			" nro_dcto, forma_pago, detalle_otros, galones_comb, monto)"
			" VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True


	def set_update_secuencia(self, param):
		query = "UPDATE secuencia SET correlativo=%s WHERE ntabla = %s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True


	def guardar_url_combustible(self, param):
		query = "INSERT INTO liquidacion_viajes_detalle (image_url) values(%s)"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def get_saldos_liquidacion_depo(self, param):
		# query = (
		# 	" SELECT  "
		# 	" COALESCE(finanzas.total_monto, 0) AS total_monto, "
		# 	" COALESCE(lvm.saldo_liqui, 0) AS saldo_liqui, "
		# 	" finanzas.refe_banco  "
		# 	# " finanzas.monto_dep "
		# 	" FROM ( "
	
		# 	# -- Subconsulta para calcular la suma de montos y agrupar ref_banco por ref_dcto
		# 	" SELECT  "
		# 	" ref_dcto, "
		# 	" SUM(monto) AS total_monto, "
		# 	" GROUP_CONCAT(DISTINCT ref_banco SEPARATOR ', ') AS refe_banco "
		# 	# " group_concat(monto separator ', ') as monto_dep "
		# 	" FROM tb_finanzas_varios "
		# 	" WHERE ref_banco NOT IN (SELECT id_deposito FROM liquidacion_viajes_depositos) "
		# 	# " GROUP BY ref_dcto "
		# 	" ) AS finanzas "
	
		# 	" INNER JOIN tb_documentos_varios tdv ON tdv.id_registro = finanzas.ref_dcto "
		# 	" LEFT JOIN liquidacion_viajes_movimiento lvm ON lvm.id_usuario = tdv.ruc_dni "
		# 	" WHERE tdv.ruc_dni = %s "
		# 	" ORDER BY lvm.fecha_liqui ASC "
		# 	" LIMIT 1; "
		# )
		query = (
			" SELECT coalesce(ref_banco, '-'),  "
			" coalesce(SUM(monto), 0) AS total_monto,  "
			" coalesce(GROUP_CONCAT(DISTINCT ref_banco SEPARATOR ', '), '-') AS refe_banco   "
			" FROM tb_finanzas_varios  tfv "
			" LEFT JOIN liquidacion_viajes_depositos lvd ON tfv.ref_banco = lvd.id_deposito "
			" INNER JOIN tb_documentos_varios tdv on tdv.id_registro = tfv.ref_dcto "
			" WHERE lvd.id_deposito IS NULL  " #-- Solo los que no tienen coincidencia en liquidacion_viajes_depositos 
			" and ruc_dni = %s "
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)

	def get_saldos_liquidacion(self, param):
		query = (
			" SELECT saldo_liqui "
			" FROM liquidacion_viajes_movimiento  "
			" WHERE id_usuario = %s "
			" ORDER BY id_liqui DESC, fecha_liqui DESC  "
			" LIMIT 1"
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)

	def get_saldos_liquidacion_total(self, param):
		query = (
			" SELECT ref_saldo_actual, coalesce(saldo_liqui, 0) "
			" from liquidacion_viajes lv "
			" left join liquidacion_viajes_movimiento lvm on lvm.id_usuario = lv.conductor "
			" where conductor = %s "
			" AND lv.status = 'AV'"
			" order by fecha_liqui DESC "
			" limit 1 "
		)
		return self.consultas_exe.execute_sqlone_transaccion(query, param)


	def insertar_movimiento_liquidacion(self, param):
		query = (
			" INSERT INTO liquidacion_viajes_movimiento (id_usuario, id_liqui, fecha_liqui, saldo_liqui)"
			" values(%s,%s,%s,%s)"			
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def update_status_liquidacion(self, param):
		query = " UPDATE liquidacion_viajes set status=%s where id_registro=%s "
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True
		


	# -- sentencion  para lista liquidaciones .....
	# .............................................
	def get_liquidaciones_por_id(self, param):
		query = (
			" SELECT date_format(lv.fecha, '%d-%m-%Y') , lv.id_registro, "
			" sum(monto) , status"
			" from liquidacion_viajes lv"
			" left join liquidacion_viajes_detalle lvd on lvd.id_registro = lv.id_registro"
			" where conductor=%s"
			" group by id_registro order by lv.fecha desc, id_registro desc limit 5"
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)


	def get_detalle_liquidacion(self, param):
		query = (
			" SELECT date_format(fecha, '%d-%m-%y'),"
			" tipo_gasto, monto, forma_pago, detalle_otros, galones_comb, image_url, col_viajes_detalle "
			" from liquidacion_viajes_detalle "
			" where id_registro=%s "
			" order by fecha asc "
		)
		return self.consultas_exe.execute_sql_transaccion(query, param)


	def set_delete_gasto(self, param):
		query = "DELETE FROM liquidacion_viajes_detalle where col_viajes_detalle=%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True

	def update_saldo_referencia_liquidacion(self, param):
		query = " UPDATE liquidacion_viajes set ref_saldo_actual= ref_saldo_actual + %s "
		query += " where id_registro=%s"
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True
		
	def cambiar_ref_efectivo_guias(self, param):
		query = (
			" INSERT INTO liquidacion_viajes_guias (id_liqui, serie, numero, efectivo)"
			" VALUES (%s, %s, %s, %s)"
			" ON DUPLICATE KEY UPDATE "
			" efectivo = VALUES(efectivo) "
		)
		if self.consultas_exe.execute_commit_transaccion(query, param):
			return True
		