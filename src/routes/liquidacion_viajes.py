import time
import os
import base64
from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
#from app import limiter 

from routes.login import token_required
from sentencias_sql_api import sentenciasConsultasApi
from models.liquidacion_viajes.sentencias_liqui import SentenciasLiquidacionViajes


main = Blueprint('liqui_viajes_blueprint', __name__)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
UPLOAD_FOLDER = "//SERVER-DELL/File Pdf/OPERACIONES/Liquidacion_Viajes"
# UPLOAD_FOLDER = "C:/inetpub/wwwroot/imagenes/vales-combustible"


@main.route('/secuencia', methods=['POST'])
def get_extrae_secuencia():
    data = request.json
    tipo_secuencia = data['secuencia']
    
    consultas = sentenciasConsultasApi()
    rst = consultas.get_secuencia_actual((tipo_secuencia, ))

    if rst:
        datos = [(rst[1],)]
        n_correl = int(rst[1]) + 1

        if not consultas.set_update_secuencia([( n_correl, tipo_secuencia)]):
            consultas.cerrar_conexion()
            return jsonify({'message': 'Tipo secuencia No encontrada -------------'}), 404
            
        consultas.fin_conexion()
        return jsonify({'data': datos}) 

    return jsonify({'message': 'Tipo secuencia No encontrada'}), 404
     

@main.route('/users_name', methods=['POST'])
@token_required
def get_users_name():
    data = request.json
    dni = data['username']
    
    consultas = sentenciasConsultasApi()
    rst = consultas.get_info_usuario((dni, ))
    if rst:
        return jsonify({'data': rst[2]}) 

    return jsonify({'message': 'No se encontro ningun dato para este Usuario'}), 404


# -- Generar Nueva Liquidacion ........................
# .....................................................
@main.route('/saldo_anterior', methods=['POST'])
@token_required
def get_saldo_anterior():
    data = request.json
    dni = data['dni']
    
    consultas = SentenciasLiquidacionViajes()
    rst_saldo = consultas.get_saldos_liquidacion((dni, ))
    rst_depo = consultas.get_saldos_liquidacion_depo((dni, ))
    
    if rst_saldo == []:
        rst_saldo = [(0,)]

    if rst_depo == []:
        rst_depo == [('-', 0, '-')]
        
    lista_union = (rst_saldo[0][0],) + rst_depo[0][1:]
    
    if lista_union:
        return jsonify({'data': [lista_union]}) 
    
    return jsonify({ 'data': [(0,0)], 'message': 'No se encontro Ningun Resultado'})


@main.route('/saldo_anterior_total', methods=['POST'])
@token_required
def get_saldo_anterior_total():
    data = request.json
    dni = data['dni']
    
    consultas = SentenciasLiquidacionViajes()
    rst = consultas.get_saldos_liquidacion_total((dni, ))

    if rst:
        return jsonify({'data': rst}) 
    
    return jsonify({ 'data': [(0,0)], 'message': 'No se encontro Ningun Resultado'})


@main.route('/liquidacion_activa', methods=['POST'])
#@limiter.limit("2 per second")
@token_required
def get_liquidacion_activa():
    data = request.json
    dni = data['dni']
    
    consultas = SentenciasLiquidacionViajes()
    rst = consultas.get_ultima_liquidacion((dni, ))
    consultas.cerrar_conexion()
    
    if not rst:
        return jsonify({'data': []}) 

    datos = {}
    for x in rst:
        datos = {
            'fecha': x[0], 
            'asiento':x[1], 
            'guia':x[2],
            'importe': str(x[3]),
            'activa': x[4],
            'saldo_actual': x[5],
        }

    return jsonify({'data': datos}) 


@main.route('/liquidaciones', methods=['POST'])
@token_required
def get_agregar_liquidacion():    
    dict_empresas = {
        'Transcargo': '1',
        'Lotransa': '2',
        'Translogistic': '3',
        'Paucar Inter': '4',
    }

    data = request.json
    lista_bancos = data['ref_bancos']
    # lista_importes = data['ref_importes']
    # resultado = list(zip(lista_bancos, map(int, lista_importes) ))


    lista_depositos = []
    for x in lista_bancos:
        valor_banco = False if x == '-' else True
        lista_depositos.append((
            x,
            data['asiento'],
            # float(x[1])
        ))

    param = [(
        data['asiento'],
        data['fecha'],
        dict_empresas.get(data['empresa']),
        data['conductor'],
        data['activa'],
        data['saldo_actual'],
    )]


    consultas = SentenciasLiquidacionViajes()
    valor = True
    if not consultas.insert_liquidacion_viajes(param):
        valor = False

    if valor_banco:
        if not consultas.insert_id_liqui_en_depositos(lista_depositos):
            valor = False

    if not valor:
        consultas.cerrar_conexion()
        return jsonify({'message': 'Inconsistencia Encontrada  :\n*'\
            ' Comuniquese Con su Administrador de Soporte'}), 404

    consultas.fin_conexion()
    return jsonify({'message': 'Registro de Liquidación creada Correctamente'}), 200


# -- Apartado de consultas de guias Transportistas ..........
# ...........................................................
@main.route('/list_guias', methods=['POST'])
@token_required
def get_lista_guias_transp():
    data = request.json

    dict_empresas = {
        'Transcargo': '1',
        'Lotransa': '2',
        'Translogistic': '3',
        'Paucar Inter': '4',
    }

    consultas = SentenciasLiquidacionViajes()
    rst = consultas.get_lista_guias_por_id( (str(data['placa']), dict_empresas.get(data['empresa'])) )
    consultas.cerrar_conexion()
    
    if not rst:
        return jsonify({'message': 'No se encontraron Guias Pdtes de Asociar', 'data': []})

    # -- Deprocesamos data ......
    result  = []
    for x in rst:
        value = {
            'id': x[0],
            'serie': x[1][:4],
            'correlativa': x[1][5:],
            'seleccion': False,
        }
        result.append(value)

    return jsonify({'data': result})


@main.route('/list_guias_details', methods=['POST'])
@token_required
def get_lista_guias_transp_details():
    data = request.json

    dict_empresas = {
        'Transcargo': '1',
        'Lotransa': '2',
        'Translogistic': '3',
        'Paucar Inter': '4',
    }

    consultas = SentenciasLiquidacionViajes()
    rst = consultas.get_lista_guias_detallado_por_id( (str(data['placa']), dict_empresas.get(data['empresa'])) )
    consultas.cerrar_conexion()
    
    if not rst:
        return jsonify({'message': 'No se encontraron Guias Pdtes de Asociar', 'data': []})

    # -- Deprocesamos data ......
    result  = []
    for x in rst:
        value = {
            'id': x[0],
            'serie': x[1][:4],
            'correlativa': x[1][5:],
            'remitente': x[2],
            'destinatario': x[3],
            'partida': x[4],
            'llegada': x[5],
            'seleccion': False,
        }
        result.append(value)

    return jsonify({'data': result})


@main.route('/numero_guia', methods=['GET'])
@token_required
def get_numero_guia_transportista():
    numero = request.args.get('numero')
    empresa = request.args.get('empresa')

    consultas = SentenciasLiquidacionViajes()
    rst = consultas.get_numero_guia((numero, empresa))
    consultas.cerrar_conexion()
    
    if not rst:
        return jsonify({'data': []})

    return jsonify({'data': rst})



@main.route('/numero_guia/guardar', methods=['POST'])
@token_required
def set_numero_guia_transportista():
    data = request.json
    
    param = [(
        data['asiento'],
        data['serie'],
        data['correlativa'],
    )]

    consultas = SentenciasLiquidacionViajes()
    if not consultas.insertar_guia_liquidacion(param):
        consultas.cerrar_conexion()
        return jsonify({'message': 'Proceso Cancelado : \n* Guia ya se encuentra en una Liquidacion'}), 404
    
    consultas.fin_conexion()
    return jsonify({'message': 'Guia Agregadas Correctamente'}), 200



# -- Consultas guardado de gastos detalle liquidacion  ....
# ......................................................... 
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/set_detalle_gastos_image', methods=['POST'])
@token_required
def set_detalle_gastos_liquidacion_image():

    if "file" not in request.files:
        return jsonify({"error": "No se encontró el archivo"}), 400

    file = request.files.get("file")

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Archivo no válido"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        param = [(
            request.form.get('asiento'),
            request.form.get('fecha'),
            request.form.get('tipoGasto'),
            request.form.get('nroDcto'),
            request.form.get('formaPago'),
            # '--',
            request.form.get('detalleOtros').upper(),
            request.form.get('cantidadGlns'),
            request.form.get('importe'),
            f"{filename}"
        )]

        consultas = SentenciasLiquidacionViajes()

        if not consultas.insertar_detalle_gastos_image(param):
            consultas.cerrar_conexion()
            return jsonify({'error': '\nProceso Cancelado : \n-----------------------\n*'+
                ' Error al intentar Guardar gasto'}), 404
        
        # -- Guardamos file en servidor ..........
        consultas.fin_conexion()
        file.save(file_path)
        return jsonify({'message': ' Gasto agregado Correctamente'}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@main.route('/set_detalle_gastos', methods=['POST'])
@token_required
def set_detalle_gastos_liquidacion():
    data = request.json
    
    try:
        param = [(
            data['asiento'],
            data['fecha'],
            data['tipoGasto'],
            data['nroDcto'],
            data['formaPago'],
            # '-',
            data['detalleOtros'].upper(),
            data.get('cantidadGlns', '0'),
            data['importe'],
        )]
       
        consultas = SentenciasLiquidacionViajes()

        if not consultas.insertar_detalle_gastos(param):
            consultas.cerrar_conexion()
            return jsonify({'error': 'Proceso Cancelado : \n\n* Error al intentar Guardar gasto'}), 404
        
        consultas.fin_conexion()
        return jsonify({'message': 'Gasto agregado Correctamente'}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/upload/imagen', methods=['POST'])
@token_required
def set_imagen_url_combustible():    
    if "file" not in request.files:
        return jsonify({"message": "No se encontró el archivo"}), 400

    file = request.files["file"]

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"message": "Archivo no válido"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(file_path)
        file_url = f"http://localhost:5173//uploads/{filename}"
        consultas = SentenciasLiquidacionViajes()

        if not consultas.guardar_url_combustible([(file_url, )]):
            return jsonify({'message': 'Erorrrrrrrrrrrrr'})
        
        consultas.fin_conexion()
        return jsonify({"message": "Archivo subido", "url": file_url}), 201

            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -- Cierre de liquidacion .................
@main.route('/set_cierre_liquidacion', methods=['POST'])
@token_required
def set_cerramos_liquidacion():    
    data = request.json
    
    try:
        param = [(
            data['usuario'],
            data['id_liqui'],
            data['fecha'],
            data['saldo'],
        )]

        asiento = data['asiento']
        param_status = [('CD', asiento )]

        consultas = SentenciasLiquidacionViajes()
        valor = True
        if not consultas.insertar_movimiento_liquidacion(param):
            valor = False
        if not consultas.update_status_liquidacion(param_status):
            valor = False

        if not valor:
            consultas.cerrar_conexion()
            return jsonify({'message': 'Proceso Cancelado : \n\n* Error al intentar Cerrar Liquidación'}), 404

        consultas.fin_conexion()
        return jsonify({'message': 'Liquidación Cerrada Correctamente'}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -- Funciones lista liquidaciones ...........
# ............................................
@main.route('/liquidacionesByid', methods=['POST'])
@token_required
def get_liquidaciones_by_id():
    data = request.json
    dni = data['dni']
  

    consultas = SentenciasLiquidacionViajes()
    rst = consultas.get_liquidaciones_por_id((dni,))

    consultas.cerrar_conexion()

    if not rst:
        return jsonify({'message': 'No se encontraron Liquidaciones Generadas', 'data': []})

    return jsonify({'data': rst})


@main.route('/detalleLiquidacionAsiento', methods=['POST'])
@token_required
def get_detalle_by_asiento():
    data = request.json
    asiento_liqui = data['asientoLiqui']

    consultas = SentenciasLiquidacionViajes()
    rst = consultas.get_detalle_liquidacion((asiento_liqui,))

    consultas.cerrar_conexion()

    if not rst:
        return jsonify({'message': 'No se encontro ningun Detalle Asociado a la Liquidación', 'data': []})

    return jsonify({'data': rst})



@main.route('/delete_gasto_liquidacion', methods=['POST'])
@token_required
def set_delete_gasto_liquidacion():
    data = request.json
    id_gasto = data['idGasto']

    consultas = SentenciasLiquidacionViajes()

    if not consultas.set_delete_gasto([(id_gasto,)]):
        return jsonify({'message': 'No se pudo eliminar el Gasto Seleccionado'})
        consultas.cerrar_conexion()

    consultas.fin_conexion()
    return jsonify({'message': 'Gasto eliminado Correctamente'})



@main.route('/efectivo_liqui_cliente', methods=['POST'])
@token_required
def set_efectivo_cliente():    
    data = request.json
    
    # try:
    param = [(
        data['monto_efectivo'],
        data['id_liqui'],
    )]

    param_efectivo = [(
        data['id_liqui'],
        data['numeroGuia'][:4],
        data['numeroGuia'][5:],
        'OK'
    )]

    consultas = SentenciasLiquidacionViajes()
    valor = True
    if not consultas.update_saldo_referencia_liquidacion(param):
        valor = False
    if not consultas.cambiar_ref_efectivo_guias(param_efectivo):
        valor = False

    if not valor:
        consultas.cerrar_conexion()
        return jsonify({'message': 'Proceso Cancelado : \n\n* Error al intentar guardar el Efectivo'}), 404

    consultas.fin_conexion()
    return jsonify({'message': 'Efectivo cargado Correctamente'}), 200
    
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500



# -- Visualizacion de Imagenes .....................
# ..................................................
@main.route('/imagenes/<filename>', methods=['GET'])
@token_required
def get_image(filename):
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(image_path):
        return jsonify({"error": "Imagen no encontrada"}), 404
    return send_from_directory(UPLOAD_FOLDER, filename)




# https://www.jluislopez.es/diseno-web-responsive/