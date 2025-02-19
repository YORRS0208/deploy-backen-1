from werkzeug.security import check_password_hash
from flask import Blueprint, Flask, request, jsonify
import jwt
import datetime
from functools import wraps

from sentencias_sql_api import sentenciasConsultasApi
from utils.generales import verificar_contraseña


main = Blueprint('acceso_login', __name__)

SECRET_KEY = 'mi_clave_secreta'
refresh_tokens = []


# -- Decorador para proteger rutas .............
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token es requerido'}), 401

        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'El token ha expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401

        return f(*args, **kwargs)
    return decorated


# -- Ruta para iniciar sesión .................
@main.route('/login_acces', methods=['POST'])
def login():
    auth = request.json

    # -- Extraer usuario BD .........
    consultas = sentenciasConsultasApi()
    rst = consultas.get_info_usuario((auth['username'], ))
 
    if not rst:
        return jsonify({'message': 'Usuario y/o Contraseña incorrectos'}), 401

    contrasenia_descifrada = verificar_contraseña(auth['password'], rst[1])
   
    if auth['username'] == rst[0] and contrasenia_descifrada:
        access_token = jwt.encode({
            'user': auth['username'],
            'emp': auth['empresa'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)
        }, SECRET_KEY, algorithm="HS256")

        refresh_token = jwt.encode({
            'user': auth['username'],
            'emp': auth['empresa'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3)
        }, SECRET_KEY, algorithm="HS256")

        infor_name = rst[2]
        refresh_tokens.append(refresh_token) 
        return jsonify({
            'access_token': access_token, 
            'refresh_token': refresh_token, 
            'user_name': infor_name })
    return jsonify({'message': 'Usuario y/o Contraseña incorrectos'}), 401


# -- Ruta para renovar el access token ............
@main.route('/refresh_token', methods=['POST'])
def refresh():
    refresh_token = request.json.get('refresh_token')

    if refresh_token not in refresh_tokens:
        return jsonify({'message': 'Refresh token inválido'}), 401

    try:
        data = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])

        print(f"Refresh Token Expira: {datetime.datetime.utcfromtimestamp(data['exp'])}")
        
        new_access_token = jwt.encode({
            'user': data['user'],
            'emp': data['emp'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({'access_token': new_access_token})

    except jwt.ExpiredSignatureError:    
        refresh_tokens.remove(refresh_token)
        return jsonify({'message': 'El refresh token ha expirado'}), 401
        
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token inválido'}), 401


# -- Ruta protegida de ejemplo ..............
@main.route('/dashboard', methods=['GET'])
@token_required
def dashboard():
    return jsonify({'message': 'Bienvenido al Dashboard'})
