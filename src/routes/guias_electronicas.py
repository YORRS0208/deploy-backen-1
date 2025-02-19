from flask import Blueprint, jsonify, request, make_response
from models.guias_electronicas.consulta_guias import ConsultasGuiasElectronicas
from models.guias_electronicas.guias_duplicadas.guias_duplicadas import GuiasDuplicadasTransp

main = Blueprint('guias_electronicas_blueprint', __name__)

# -- para extraccion de guia por numero de forma individual .....
@main.route('/<numero_guia>', methods=['GET'])
def get_guia_by_id(numero_guia):
    data, status_code = ConsultasGuiasElectronicas().consultar_guia_comprobante(numero_guia)
    return make_response(jsonify(data), status_code)

# -- para Descargar Pdf - Base 64
@main.route('/<numero_guia>/pdf/', methods=['GET'])
def get_guia_pdf(numero_guia):
    data, status_code = ConsultasGuiasElectronicas().descargar_base64_pdf(numero_guia)
    return make_response(jsonify(data), status_code)

    
# -- para extraccion de lista de guias por Fecha
@main.route('/', methods=['GET'])
def get_guia_all():
    ruc = request.args.get('ruc')
    tipo = request.args.get('tipo')
    fechaini = request.args.get('fecha_ini')
    fechafin = request.args.get('fecha_fin')

    data, status_code = ConsultasGuiasElectronicas().get_lista_guias(ruc, tipo, fechaini, fechafin)
    return jsonify({'datos' : data, 'status':status_code})
    

# -- para consultas guias Duplicadas .......
@main.route('/guias_duplicadas/', methods=['GET'])
def get_guia_trans_duplicados_remit():
    data, status_code = GuiasDuplicadasTransp().get_guias_duplicadas()
    return jsonify({'datos' : data, 'status':status_code})


# -- Listar Guias All - Sunat ...........
@main.route('/all_guias_sunat/', methods=['GET'])
def get_all_guias_sunat():
    data, status_code = GuiasDuplicadasTransp().get_guias_duplicadas()
    return jsonify({'datos' : data, 'status':status_code})


