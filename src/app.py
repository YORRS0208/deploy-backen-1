from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# from config import "config"
from routes import (
        detracciones, guias_electronicas, consultas_ruc,
        consultas_mtc, login, liquidacion_viajes)

from manejo_tareas_programadas import ManejoTareasProgramadas
import os

app = Flask(__name__)
UPLOAD_FOLDER = "C:/inetpub/wwwroot/imagenes/vales-combustible"
UPLOAD_FOLDER = "//SERVER-DELL/File Pdf/OPERACIONES/Liquidacion_Viajes"
app.config['SECRET_KEY' ] = 'mi_clave_secreta'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Carpeta donde se guardarán las imágenes (debe estar configurada en IIS)

# limiter = Limiter(
#     get_remote_address,
#     app=app,
#     # default_limits=["200 per day", "50 per hour"],
#     default_limits=["3 per second"]
# )

CORS(app)
# CORS(app, origins="http://200.1.179.173:8081") #, supports_credentials=True)


# Configurar logging
# logging.basicConfig(filename="access.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# @app.before_request
# def log_request():
#     forwarded_for = request.headers.get("X-Forwarded-For")
#     if forwarded_for:
#         ip = forwarded_for.split(",")[0].strip()  # Toma la primera IP (cliente real)
#     else:
#         ip = request.remote_addr  # Si no hay proxy, usa la IP normal

#     print(ip)
#     endpoint = request.path
#     method = request.method
#     user_agent = request.headers.get("User-Agent", "Desconocido")    
#     logging.info(f"Intento de acceso desde {ip} - Método: {method} - Endpoint: {endpoint} - User-Agent: {user_agent}")




@app.route('/')
def home():
    return jsonify("Bienvenido")


if __name__=='__main__':
    # if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    #     ManejoTareasProgramadas.start_scheduler_tareas()
    
   # ManejoTareasProgramadas.start_scheduler_tareas()
    
    # Configuración de Flask
    # app.config.from_object(config['development'])

    # -- Blueprints ..................
    app.register_blueprint(login.main, url_prefix= '/api/login')

    #app.register_blueprint(detracciones.main, url_prefix= '/api/detracciones')
    #app.register_blueprint(guias_electronicas.main, url_prefix= '/api/guias_electronicas')
    #app.register_blueprint(consultas_ruc.main, url_prefix= '/api/consulta_ruc')
    #app.register_blueprint(consultas_mtc.main, url_prefix= '/api/consulta_mtc')
    
    app.register_blueprint(liquidacion_viajes.main, url_prefix= '/api/liquidacion_viajes')
    
    # app.run(debug=True, use_reloader=True)
    # app.run(debug=False, host='0.0.0.0', port=8080) # , use_reloader=False)  
    app.run(debug=True, host='127.0.0.1', port=5000)     
    