from xml.dom import minidom
import os.path, sys
from .ruta_relativa import resolver_ruta as rtv

INICIALIZACION  = "database/inicializacion.xml"

class lecturaFileXml:
	pass

	def fnObtenDato(sDato):
		docXML = minidom.parse(rtv(INICIALIZACION))
		dato = docXML.getElementsByTagName(sDato)[0]
		return dato.firstChild.data

