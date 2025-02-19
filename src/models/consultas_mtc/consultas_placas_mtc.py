import requests
from bs4 import BeautifulSoup
import time

# scraping web .................... Elaborado por Yorrs Rivera

class PlacasMtc():
	URL_PRINCIPAL = 'https://www.mtc.gob.pe/tramitesenlinea/tweb_tLinea/tw_consultadgtt/Frm_rep_intra_mercancia_display.aspx'
	URL_SECUNDARIA = 'https://www.mtc.gob.pe/tramitesenlinea/tweb_tLinea/tw_consultadgtt/Frm_rep_intra_mercancia_datos.aspx'
	# _sesion = requests.Session()
	def __init__(self, parent= None):
		self.lista_datos = []
		pass

	def get_cng_payload(self, valor, opcion='placa'):
		options = {
			'placa': '4',
			'ruc': '2'
		}
		opcion_seleccionada = options.get(opcion)
		payload = {
			'rbOpciones': opcion_seleccionada,
			'txtValor': valor,
			'hdopcion': opcion_seleccionada,
			'hdvalore': valor,
			'hdopc': 2
		}
		return payload
	
	def extraer_cng(self, valor, tipo='placa'):
		return self.get_cng_payload(valor.upper(), tipo)


	# extraccion de ambas tablas .....................................
	def get_tabla_principal(self, payload):
		try:
			response = requests.post(self.URL_PRINCIPAL, data=payload)
			response.raise_for_status()
		except requests.RequestException as e:
			return {}, 404
	
		soup = BeautifulSoup(response.text, 'html.parser')
		tabla = soup.find('span', id='lblHtml')

		if not tabla:
			return {}, 404

		lista = [x.get_text(strip=True) for x in tabla.find_all('td')]
		param_list = list(zip(*[iter(lista)] * 5))[1:]
	
		values = []
		for x in param_list:
			if x[1][-3:].strip() == "CNG":
				values.append((x[3], x[1], payload.get('txtValor')))
				break
		
		if not values:
			return {}, 404
	
		# Ejecutamos segunda busqueda por ruc y cng encontrado de la placa buscada
		return self.get_tabla_secundaria(values[0])


	def get_tabla_secundaria(self, valores):
		payload_secundario = {
			'hdruc': str(valores[0]),
			'hdpartida': str(valores[1])
		}

		try:
			response = requests.post(self.URL_SECUNDARIA, data=payload_secundario)
			response.raise_for_status()
		except requests.RequestException as e:
			return {}, 404

		soup = BeautifulSoup(response.text, 'html.parser')
		# vigencia = soup.find('span', id='lblVigencia')
		# print(vigencia.text.strip())
		

		if valores[2] == valores[0]:
			return self.datos_por_ruc(soup)
		else:
			return self.datos_por_placa(soup, valores)


	def datos_por_placa(self, html_parseado, valor):
		tabla = html_parseado.find('table')
		td_especifico = tabla.find('td', class_='texto_5', string=lambda text: valor[2] in text if text else False)
		
		if td_especifico:
			tr_padre = td_especifico.find_parent('tr')
			if tr_padre:
				celdas_td = tr_padre.find_all('td') #, class_='texto_5') 
				valores = [celda.get_text(strip=True) for celda in celdas_td]

				if valores:
					return {
						'ruc':valor[0],
						'placa':valores[1],
						'constancia':valores[2],
						'categoria':valores[3],
						'serie_chasis': valores[4],
						'anio_fabricacion': valores[5],
						'nro_ejes': valores[6],
						'carga_util': valores[7]
					} , 200
					
		return {}, 404				

		# tabla = html_parseado.find_all('tr', class_='textDisplay')

		# for x in tabla:
		# 	fila = x.find_all('td')
		# 	if fila[1].get_text(strip=True) == valor[2]:
		# 		return {
		# 			'ruc':valor[0],
		# 			'placa':fila[1].get_text(strip=True),
		# 			'constancia':fila[2].get_text(strip=True),
		# 		}
		# return {}				
 
	def datos_por_ruc(self, html_parseado):
		tabla = html_parseado.find_all('tr', class_='textDisplay')
		
		lista = []
		for x in  tabla:
			celdas = x.find_all('td')
			lista.append(
				{
					'placa': celdas[1].get_text(strip=True),
					'constancia' : celdas[2].get_text(strip=True),
					'categoria' : celdas[3].get_text(strip=True),
					'chasis' : celdas[4].get_text(strip=True),
					'anio_fabricacion' : celdas[5].get_text(strip=True),
				}
			)

		return lista, 200 if lista else [], 500
	

	# funciones de consulta en app .............................
	# ..........................................................
	def get_datos_por_placa(self, valor):
		payload = self.extraer_cng(valor.upper(), 'placa')
		return self.get_tabla_principal(payload)

	def get_datos_por_ruc(self, valor):
		payload = self.extraer_cng(valor, 'ruc')
		return self.get_tabla_principal(payload)


	

# lista_rucs = ['20606636556', '20563256380', '20604773459', '20519000815', ]
# # # lista_rucs = ['amg941', 'AAU555', 'BFN932', 'ARM718']
# gg = PlacasMtc()
# tt = gg.get_datos_por_placa('BJY917')
# print(tt)
# # lista = []
# # fila = 1
# for q in lista_rucs:
# 	tt =  gg.get_datos_por_ruc(q)[0]
# 	print()
# 	# print('.....................')
	
# 	print(tt)

# 	# if tt:
# 	# 	for x in tt:
# 	# 		if tt:
# 	# 			placa = x.get('placa')
# 	# 			constancia = x.get('constancia')
# 	# 			lista.append((placa, constancia))
# 					# lista.append((placa, constancia))
# 			# 	print(f"{fila}.   {q} * Placa : {placa} - contancia : {constancia}")
# 			# else:
# 			# 	print(f"Placa : {x}  No existe en el MTC")
# 			# fila+=1
# # print(lista)

# lista_mtc = set(lista)
# # lista_bd = set([('F1G989', '151704663'), ('ALP973', '151909056'), ('ACN975', '151715959'), ('BBE829', '151919127'), ('BBP989', '15M22020101E'), ('ARL770', '15M21007195E'), ('AUD701', '15M22021731E'), ('AWR981', '15M21005225E'), ('BFY987', '15M23033801E'), ('BJY917', '15M21007191E'), ('AFC972', '151900653'), ('AXI897', '15M21013618E'), ('AXJ729', '15M21013622E'), ('ALP999', '151909057'), ('ADM982', '151721880'), ('F9K742', '151704638'), ('ART700', '15M21007196E'), ('ATB936', '152021600'), ('BKY978', '15M24014753E'), ('APN842', '15M23005575E'), ('F1G987', '151704648'), ('ATQ983', '152021599'), ('ARZ992', '152010622'), ('BES772', '15M23039760E'), ('ATB805', '152010620'), ('ATU974', '15M24031143E'), ('AJP980', '151834933'), ('ARM718', '15M21007194E'), ('BKU994', '15M24013684E'), ('BPA843', '15M22013386E'), ('ACN994', '151715956'), ('BJZ875', '15M21007193E'), ('D2G974', '151709510'), ('ALE984', '151904730'), ('BBO998', '15M22020102E'), ('BNO925', '15M24034522E'), ('CAU875', '15M24043408E'), ('BHS899', '152103400'), ('BYU937', '15M24016477E'), ('ACQ992', '151715958'), ('BXW749', '15M24000465E'), ('AVA988', '152103077'), ('BBE869', '151919128'), ('BJY889', '15M21007189E'), ('BAD992', '15M22003098E'), ('BHU949', '152104541'), ('ADK990', '151721881'), ('BXO852', '15M23059938E'), ('BKV972', '15M24013685E'), ('AAW816', '15M23004327E'), ('BFB988', '15M23023242E'), ('F5D992', '151704651'), ('AKX994', '151903325'), ('AHT973', '151829584'), ('BFN932', '152103097'), ('BNW881', '15M22051920E'), ('F5Z988', '151816635'), ('BXW781', '15M24000464E'), ('AHF987', '151818564'), ('ARS756', '152007963'), ('AMO998', '151917427'), ('BYV745', '15M24014038E'), ('BET860', '15M23039761E'), ('BBE814', '151919126'), ('D4C978', '151704662'), ('AHF988', '15M21041697E'), ('AWA982', '152108863'), ('F9I989', '151842918'), ('BJY791', '15M21007192E'), ('F3O981', '151704656'), ('BMT741', '15M24041802E'), ('ARS895', '152007964'), ('BYU938', '15M24016479E'), ('BXQ776', '15M23059710E'), ('BFF983', '15M23023290E'), ('AUG979', '152100247'), ('T8P925', '151900655'), ('AAU876', '151704674'), ('ACR972', '151715957'), ('BJY885', '15M21007190E'), ('BNO853', '15M24034319E'), ('BXW742', '15M24000462E'), ('F1D992', '151739712'), ('AVN867', '151809529'), ('BNX754', '15M22031229E'), ('ASB994', '152010621'), ('AUQ994', '152100246'), ('BAW899', '15M22026837E'), ('T8P932', '151900656'), ('AMY919', '151704672'), ('AVZ991', '152108860'), ('AXI948', '15M21013624E'), ('BXQ709', '15M23059939E'), ('BAW905', '15M22026838E'), ('BMK972', '15M24035861E'), ('BFN929', '152103076'), ('ALP974', '151909058'), ('AVZ975', '152108861'), ('BNM778', '15M24034435E'), ('BJO976', '15M23058366E'), ('AKR998', '151846098'), ('AKZ984', '151903323'), ('TDQ974', '151900251'), ('AVY983', '152108859')])
# lista_bd = set([])

# comparamos = lista_mtc - lista_bd
# print(comparamos)