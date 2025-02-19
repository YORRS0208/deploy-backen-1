import sys
import os

def resolver_ruta(ruta_relativa):
	if hasattr(sys, '_MEIPASS'):
		return str(os.path.join(sys._MEIPASS, ruta_relativa))	
	else:
		return str(os.path.join(os.path.abspath('.'), ruta_relativa))

	# if hasattr(sys, '_MEIPASS'):
	# 	   # Cuando se ejecuta desde el ejecutable empaquetado
	# 	   ruta_base = sys._MEIPASS
	# 	   # print(ruta_base)
	# else:
	#    # Cuando se ejecuta desde el código fuente
	#    ruta_base = os.path.abspath('.')
	#    # print(ruta_base)

	# # Ajusta la ruta en función de la estructura del paquete
	# if hasattr(sys, '_MEIPASS'):
	#    ruta_base = os.path.join(ruta_base,  '_internal')
	#    # print(ruta_base)
	# return os.path.join(ruta_base, ruta_relativa)

		

def set_medidas_frame_principal(self, parent):
	posx = parent.x()
	posy = parent.y()

	tama_x = parent.size().width()-315
	self.move(posx+tama_x, posy+83)
