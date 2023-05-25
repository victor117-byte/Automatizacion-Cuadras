"""
Creado el 23/05/2023
Desarrollado por: Hernandez Berrios Victor Andres
Objetivo: Programa que clasifica archivos PDF por su nombre de documneto desde un directorio raiz, devolviendo una Arreglo por el tipo de diccionario

Parametros:
    Directorio Raiz
    Tipo de archivo a leer
"""

# Librerias
import pandas as pd
import sys, os
import numpy as np
import PyPDF2
import json


# Variables
root = r"../"
path = os.path.join(root, "../../PDF/")

# Funcion que obtiene los archivos con su ruta y se encarga de clasificarlos en arreglos
def Funcion_Archivos(root, path):

    Lista_Archivos = list()
    
    for path, subdirs, files in os.walk(root):
        for name in files:
            # print(os.path.join(path, name))
            if os.path.join(name).endswith(".pdf"):
                #Archivos Acuse Recepcion
                ubicacion_file = os.path.join(name)
                print(os.path.join(name))
                # print(ubicacion_file)
                
                Lista_Archivos.append(ubicacion_file)    
                
                return Lista_Archivos

lista = Funcion_Archivos(root, path)
print(list)