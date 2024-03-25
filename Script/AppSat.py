import PyPDF2
import pandas as pd
import numpy as np
import sys, os
import json
import re
import datetime
import locale
import shutil
import pandas as pd
import numpy as np
from funcione2 import Clasificador_Archivos, exportDataDeclaracion, exportDataDiot, exportDataConstancia, exportDataOpinionCumplimiento, exportDataPagos, exportData_Info_Contribuyente

# Ruta PDF's'
root = r"\\192.168.1.201\avisos al rfc"
# Carpeta PDF´s
path = os.path.join(root, "avisos al rfc")

# # Path Raiz Proyecto
# path_raiz_proyecto = r'C:/Users/Administrador.WIN-3GR2N6O8MHU/Desktop/Aplicacion_SAT'
# EJERCICIO = "2023"
# cliente = "LH/"+EJERCICIO
# path_raiz_cliente = path_raiz_proyecto+"/"+cliente+"/"
# dir_excel = path_raiz_proyecto+"/Dataframes/"

# Path Raiz Testing
path_raiz_proyecto = r'C:\Users\victo\OneDrive\Documentos\Proyectos\R2D2\ProyectoSat\Automatizacion-Cuadras\Aplicacion_SAT'
EJERCICIO = "2023"
cliente = "LH/"
path_raiz_cliente = path_raiz_proyecto+"/"+cliente+"/"
dir_excel = path_raiz_proyecto+"/Dataframes/"

# # rutas provicionales
# path_declaraciones = r"\\192.168.1.201\declaraciones"
# path_pagos = r"\\192.168.1.201\declaraciones\Pagos"
# path_constancias = r"\\192.168.1.201\avisos al rfc"
# path_info_contribuyente = r"\\192.168.1.201\avisos al rfc\INFORMACION_CONTRIBUYENTE"

path_demo = r"C:\Users\victo\OneDrive\Documentos\Proyectos\R2D2\ProyectoSat\Automatizacion-Cuadras\TiposPDF"


# rutas = [path_declaraciones, path_constancias]
rutas = [path_demo]

# Esta funcion estar en tetsing
Archivos = Clasificador_Archivos(rutas, path_raiz_cliente, fecha_limite="2023-01-01")



# Funcion que obtiene los archivos con su ruta y se encarga de clasificarlos en arreglos

# Archivos = (ArchivosPDF_LH(path_raiz_cliente, cliente, EJERCICIO=EJERCICIO))


# Funciones para cada tipo de archivo




