import base64
from flask import Blueprint, jsonify, request
import time

from models.consultas_ruc.consulta_ruc import ApisNetPe, ApiSunatRucDni
from utils.token_claves.cifrado_de_claves import CifradoTokenClaveMaestra
from sentencias_sql_api import sentenciasConsultasApi


main = Blueprint('consultas_ruc_blueprint', __name__)

@main.route('/busqueda/', methods=['GET'])
def get_ruc_dni():
    token = request.args.get('token')
    search = request.args.get('search')
    tipo = request.args.get('tipo')
    
    if tipo == '0':
        return ApisNetPe(token).get_company(search)
    else:
        return ApisNetPe(token).get_person(search)

@main.route('/busqueda/sunat/', methods=['GET'])
def get_ruc_dni_sunat():
    search = request.args.get('search')
    tipo = request.args.get('tipo')
    
    if tipo == '0':
        return ApiSunatRucDni().get_company(search)
    else:
        return ApiSunatRucDni().get_persona(search)


@main.route('/', methods=['GET'])
def get_token_apisnet():   
    consultas = sentenciasConsultasApi()
    rst = consultas.search_token_por_api(('api_consultas_sunat',))
    ini = time.time()
    if not rst:
        return False

    token = base64.b64decode(rst[0])
    clave = base64.b64decode(rst[1])

    token_descifrado = CifradoTokenClaveMaestra().descifrar_dato(token, clave)
    consultas.cerrar_conexion()

    return  jsonify({'datos': token_descifrado})



