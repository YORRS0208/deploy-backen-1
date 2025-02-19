import time
import random

from utils.config_chrome.driver_chrome import iniciar_chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..parametros import _RUTA_PATH_TOKEN_GUIA


class GetTokenGuiasElectronicas():
	LOGIN_URL = "https://api-seguridad.sunat.gob.pe/v1/clientessol/4f3b88b3-d9d6-402a-b85d-6a0bc857746a/oauth2/loginMenuSol?originalUrl=https://e-menu.sunat.gob.pe/cl-ti-itmenu/AutenticaMenuInternet.htm&state=rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAx3CAAAABAAAAADdAAEZXhlY3B0AAZwYXJhbXN0AEsqJiomL2NsLXRpLWl0bWVudS9NZW51SW50ZXJuZXQuaHRtJmI2NGQyNmE4YjVhZjA5MTkyM2IyM2I2NDA3YTFjMWRiNDFlNzMzYTZ0AANleGVweA=="
	TOKEN_KEY = "SUNAT.token"
	TOKEN_FILE_PATH = _RUTA_PATH_TOKEN_GUIA
	
	def __init__(self, ruc, usuario, clave):
		self._ruc = ruc
		self._usuario = usuario
		self._clave = clave

	def _esperar_elemento(self, driver, by, identifier, timeout=10):
		return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, identifier)))

	def _esperar_y_hacer_click(self, driver, by, identifier, timeout=10):
		elemento = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, identifier)))
		time.sleep(random.uniform(0.5, 1))
		elemento.click()

	def _esperar_y_rellenar(self, elemento, valor):
		elemento.clear()
		time.sleep(random.uniform(1, 2))
		elemento.send_keys(valor)
		elemento.send_keys(Keys.TAB)

	def abrir_sunat(self):
		driver =iniciar_chrome()
		driver.get(self.LOGIN_URL)

		try:		
			# Ingresar RUC, usuario y contraseña
			self._esperar_y_rellenar(self._esperar_elemento(driver, By.ID, "txtRuc"), self._ruc)
			self._esperar_y_rellenar(self._esperar_elemento(driver, By.ID, "txtUsuario"), self._usuario)
			self._esperar_y_rellenar(self._esperar_elemento(driver, By.ID, "txtContrasena"), self._clave)

			# Click en Iniciar Sesión
			self._esperar_y_hacer_click(driver, By.ID, "btnAceptar")

			# BUSCAMOS GUIA
			self._buscar_y_acceder_guia(driver)
			return self.extraer_token_pagina_cargada(driver)	 
	
		except :
			return self.extraer_token_pagina_directa(driver)
		finally:
			driver.quit()
	
	def _buscar_y_acceder_guia(self, driver):
		self._esperar_y_rellenar(self._esperar_elemento(driver, By.ID, "txtBusca"), 'GUIA')
		self._esperar_y_hacer_click(driver, By.ID, "nivel2_62_1")
		self._esperar_y_hacer_click(driver, By.ID, "nivel3_62_1_5")
		self._esperar_y_hacer_click(driver, By.ID, "nivel4_62_1_5_1_1")
	
	def extraer_token_pagina_cargada(self, driver): 
		try:
			self._esperar_elemento(driver, By.ID, "iframeApplication")
			driver.switch_to.frame("iframeApplication")
			
			WebDriverWait(driver, 10).until(
				lambda d: d.execute_script(f"return window.sessionStorage.getItem('{self.TOKEN_KEY}');") is not None 
			)

			time.sleep(2)
			token = driver.execute_script(f"return window.sessionStorage.getItem('{self.TOKEN_KEY}');")

			if token:
				self.guardar_token_txt(token)
				return True
			else:
				return False   
		except:
			return False
	
	def extraer_token_pagina_directa(self, driver): 
		url_guias = "https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm?action=execute&code=62.1.5.1.1&s=ww1"
		driver.get(url_guias)
		
		try:
			WebDriverWait(driver, 10).until(
				lambda d: d.execute_script(f"return window.sessionStorage.getItem('{self.TOKEN_KEY}');") is not None 
			)

			time.sleep(2)
			token = driver.execute_script(f"return window.sessionStorage.getItem('{self.TOKEN_KEY}');")

			if token:
				self.guardar_token_txt(token)
				return True
			else:
				return False   
		except TimeoutException:
			print("Error al extraer el token desde la página cargada.")
			return False
	

	def guardar_token_txt(self, token):
		try:
			with open(self.TOKEN_FILE_PATH, 'w', encoding='utf-8') as file:
				file.write(token)
		except OSError as e:
			print(f"Error al guardar el archivo: {e}")
