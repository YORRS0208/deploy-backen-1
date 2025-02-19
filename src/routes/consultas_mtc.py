from flask import Blueprint, jsonify, request, make_response
from models.consultas_mtc.consultas_placas_mtc import PlacasMtc


main = Blueprint('placas_mtc_blueprint', __name__)

# -- para extraccion de Informacion de placa MTC
@main.route('/<numero_placa>', methods=['GET'])
def get_certificado_by_placa(numero_placa):
    data, status_code = PlacasMtc().get_datos_por_placa(numero_placa)
    return make_response(jsonify(data), status_code)

    
# -- para extraccion de lista de Informacion de todas las Placas MTC por RUC
@main.route('/', methods=['GET'])
def get_placas_all():
    ruc = request.args.get('ruc')
    tipo = request.args.get('tipo')
    fechaini = request.args.get('fecha_ini')
    fechafin = request.args.get('fecha_fin')

    data, status_code = ConsultasGuiasElectronicas().get_lista_placas([ruc, tipo, fechaini, fechafin])
    return jsonify({'datos' : data, 'status':status_code})
    


