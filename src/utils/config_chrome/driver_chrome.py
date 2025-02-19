
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# import undetected_chromedriver  as uc


def iniciar_chrome(proxy=None):
	driver_path = ChromeDriverManager().install()
	service = Service(driver_path)
	
	# OPCIONES DE CHROME
	options = Options()
	user_agent =  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
	options.add_argument(f"user-agent={user_agent}")
	# options.add_argument("--headless")
	options.add_argument("--disable-extensiones")
	options.add_argument("--ignore-certificate-errors")
	options.add_argument("--allow-running-insecure-content")
	options.add_argument("--no-first-run")
	options.add_argument("--disable-blink-features=AutomationControlled")
	# options.add_argument(f'--proxy-server={proxy}')

	# PARAMETROS A OMITIR EN EL INICIO DE CHROMEDRIVER
	exp_opt = [
		"enable-automation",
		"ignore-certificate-errors",
		"enable-logging"
	]
	options.add_experimental_option("excludeSwitches", exp_opt)

	# PARAMETROS QUE DEFINIS PREFERENCIAS
	prefs = {
		"profile.default_content_setting_values.notifications" : 2,
		"intl.accept_languages": ["es-ES", "es"],
		"credentials_enable_service": False,
	}
	options.add_experimental_option("prefs", prefs)

	driver = webdriver.Chrome(service=service, options=options)
	return driver


	












































	

# def iniciar_chrome_undetected():
#     # OPCIONES DE CHROME
#     options = uc.ChromeOptions()
    
#     # Agregar argumentos de opciones
#     options.add_argument("--password-store=basic")
#     options.add_argument("--headless")  # Activa el modo headless
    
#     prefs = {
#         "credentials_enable_service": False,
#         "profile.password_manager_enabled": False
#     }
#     options.add_experimental_option("prefs", prefs)

#     # Crea el driver utilizando las opciones definidas
#     driver = uc.Chrome(options=options)  # No se pasa 'executable_path' aquí

#     return driver