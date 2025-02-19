from flask import Blueprint, jsonify
from models.detracciones.get_detracciones import InformacionDetracciones

main = Blueprint('detracciones_blueprint', __name__)

@main.route('/<ruc>', methods=['GET'])
def get_detracciones(ruc):
    return InformacionDetracciones().get_lista_detracciones(ruc)
    
