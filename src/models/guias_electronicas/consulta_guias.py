import requests
from datetime import datetime
import base64

from ..parametros import _RUTA_PATH_TOKEN_GUIA
# _RUTA_PATH_TOKEN_GUIA = r'\\SERVER-DELL\File Pdf\TOKENS\TOKEN_API_SUNAT_GUIAS.txt'

class ConsultasGuiasElectronicas():
    def __init__(self):
        self._BEARER_TOKEN = self.leer_token_vigente()
        self._HEADERS = {
            "Authorization": f"Bearer {self._BEARER_TOKEN}",
            "Content-Type": "application/json",
            'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

    def leer_token_vigente(self):
        with open(_RUTA_PATH_TOKEN_GUIA, 'r') as file: 
            valor_token = file.read()
        return valor_token

    def consultar_guia_comprobante(self, numero_guia):
        url = f"https://api-cpe.sunat.gob.pe/v1/contribuyente/gre/comprobantes/{numero_guia}"
        response = requests.get(url, headers=self._HEADERS)
            
        partes = numero_guia.split('-')
        tipo = partes[1]
        if response.status_code == 200:
            if tipo == '09':
                return self.get_informacion_remitente(response), response.status_code
            else:
                return self.get_informacion_transportista(response), response.status_code
        else:
            return {'error': response.text}, response.status_code 

    
    def descargar_base64_pdf(self, numero_guia):
        url = f'https://api-cpe.sunat.gob.pe/v1/contribuyente/gre/comprobantes/{numero_guia}/descarga/pdf'
        response = requests.get(url, headers=self._HEADERS)

        if response.status_code == 200:
            base64_string = response.json().get('pdf')
            return base64_string, 200
        else:
            return {'error': response.text}, response.status_code 


    def get_informacion_remitente(self, response):
        data = response.json()

        fecha_emision = data.get('emision')
        fecha_str = str(fecha_emision.get('numFecEmision'))
        fecha_formateada = datetime.strptime(fecha_str, "%Y%m%d").strftime("%d-%m-%Y")

        direccion = data.get('traslado').get('partida').get('direccion')
        direccion_2 = data.get('traslado').get('llegada').get('direccion')

        try:
            vehiculo = data.get('traslado').get('vehiculo') 
            lista_placas = []
            for x in vehiculo:
                lista_placas.append(x.get('numPlaca'))
        except:
            lista_placas = []

        try:
            conductor = data.get('traslado').get('conductor') 
            dni = conductor[0].get('numDocIdentidad')
            licencia = conductor[0].get('numLicencia')
            nombres = conductor[0].get('desNombre')
        except:
            dni = ''
            licencia = ''
            nombres = ''
        
        lista = {
            'fecha': fecha_formateada,
            'estado' : data.get('codEstado'),
            'ruc_emite' : data.get('numRuc'),
            'remitente' : data.get('emisor').get('desNombre').upper(),
            'ruc_destino' : data.get('receptor').get('numDocIdentidad'),
            'destinatario': data.get('receptor').get('desNombre').upper(),

            'serie': data.get('numSerie'),
            'correlativa':data.get('numCpe'),
            'direccion_partida' : [(direccion.get('codUbigeo'),direccion.get('desDepartamento'), direccion.get('desProvincia'),
                direccion.get('desDistrito')), direccion.get('desDireccion')],

            'direccion_llegada' : [(direccion_2.get('codUbigeo'),direccion_2.get('desDepartamento'), direccion_2.get('desProvincia'),
                direccion_2.get('desDistrito')), direccion_2.get('desDireccion')],

            'peso': str(data.get('traslado').get('numPesoBruto')),
            'unidaMedida': str(data.get('traslado').get('codUnidadMedidaPb')),
            
            'placa' : lista_placas,
            'conductor':[dni, licencia, nombres],
        }
        return lista 


    def get_informacion_transportista(self, response):
        lista_guias = []
        if response.status_code == 200:
            data = response.json()
            
            emision = data.get('emision')
            remitente = data.get('remitente')
            receptor = data.get('receptor', 'NO ENCONTRADO')
            vehiculo = data.get('traslado').get('vehiculo')
            conductor = data.get('traslado').get('conductor')

            partida = data.get('traslado').get('partida')
            llegada = data.get('traslado').get('llegada')
            lista_vehiculos = []
        
            for x in vehiculo:
                lista_vehiculos.append(x.get('numPlaca'))

            # -- procesar si existe guias remitentes para guias no sunat 
            remitentes = True if data.get('docRelacionado') else False

            lista_guias_remit = []
            if remitentes:
                for x in data.get('docRelacionado'):
                    lista_guias_remit.append((x.get('numSerie'), x.get('numDocumento').lstrip('0') ))
            else:
                lista_guias_remit = self.array_guia_remitente(data.get('traslado').get('bien'))
 
            provincia_part = partida.get('direccion').get('desProvincia') if partida else '--'
            provincia_lleg = llegada.get('direccion').get('desProvincia') if llegada else '--'
           
            lista_guias = ((
                remitente.get('numDocIdentidad'),                           # 0
                remitente.get('desNombre'),                                 # 1
                receptor.get('numDocIdentidad') if receptor else '0',                            # 2
                receptor.get('desNombre') if receptor else 'NINGUNO',                                  # 3
                lista_vehiculos,                                            # 4
                data.get('id'),                                             # 5
                emision.get('fecEmision'),                                  # 6
                str(data.get('codEstado')),                                 # 7
                provincia_part,                                             # 8
                provincia_lleg,                                             # 8
                conductor[0].get('numLicencia'),                            # 10
                lista_guias_remit,                                          # 11
            ))      
        return lista_guias

    def array_guia_remitente(self, array):
        guias = []
        for x in array:
            join_guias = "".join(x.get('desBien').split())
            # lista_sin_guiones= x.get('desBien').split(',')
            lista_sin_guiones= join_guias.split(',')

            serie = lista_sin_guiones[0][20:24]
            correl = lista_sin_guiones[0][25:].lstrip('0')
            guias.append((serie, correl))

            if len(lista_sin_guiones) > 1:
                for x in lista_sin_guiones[1:]:
                    valor = "".join(x.split())
                    serie_ = valor[:4]
                    correl_ = valor[5:].lstrip('0')
                    guias.append((serie_,correl_))
        return guias

    # .........................................
    def get_lista_guias(self, *args, **kwargs):
        ruc, codigo_guia, fecha_ini, fecha_fin = args            
        cod_estado = kwargs.get('cod_estado', '')

        payloads = {
            'numRucEmisor': ruc,
            'numRucReceptor': '' ,
            'codCpe': codigo_guia,
            'numSerie': '' ,
            'numCpe': '', 
            'fecEmisionIni': fecha_ini,
            'fecEmisionFin': fecha_fin,
            'codEstado': cod_estado,
            'codSubEstado': '',
            'rangoHoras': '', 
            'page': '1',
            'per_page': '100',
            'tipBusqueda': '2'
        }


        if cod_estado:
            payloads['cod_estado'] = cod_estado

        url = "https://api-cpe.sunat.gob.pe/v1/contribuyente/gre/comprobantes"

        response = requests.get(url, headers=self._HEADERS, params=payloads)
        status = response.status_code
        
        if response.status_code == 200:
            data = response.json()
            
            rst = data.get('items')
            values = []
            for x in rst:
                fecha_obj = datetime.strptime(x.get('fecEmision'), '%d/%m/%Y %H:%M')
                fecha_formateada = fecha_obj.strftime('%d-%m-%Y %H:%M')
                
                values.append((
                    fecha_formateada,
                    str(x.get('numSerie')) + '-' +str(x.get('numCpe')) ,
                    x.get('rucEmisor'),
                    x.get('rucReceptor'),
                ))
            return values, 200
        else:
            return {'error': response.text}, response.status_code 
