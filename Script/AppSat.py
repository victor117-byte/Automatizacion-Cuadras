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
from funciones_sat import copy_pdf, read_file_pdf, Clasificador_Archivos, ArchivosPDF, exportDataDeclaracion, exportDataAcuseRecepcion, exportDataDiot, exportDataConstancia, exportDataOpinionCumplimiento, exportDataPagos, funcion_Conceptos, convertir_pdf_a_base64, ArchivosPDF_LH, exportData_Info_Contribuyente

# Ruta PDF's'
root = r"\\192.168.1.201\avisos al rfc"
# Carpeta PDF´s
path = os.path.join(root, "avisos al rfc")

# Path Raiz Proyecto
path_raiz_proyecto = r'C:/Users/Administrador.WIN-3GR2N6O8MHU/Desktop/Aplicacion_SAT'
EJERCICIO = "2023"
cliente = "LH/"+EJERCICIO
path_raiz_cliente = path_raiz_proyecto+"/"+cliente+"/"
dir_excel = path_raiz_proyecto+"/Dataframes/"

# rutas provicionales
path_declaraciones = r"\\192.168.1.201\declaraciones"
path_pagos = r"\\192.168.1.201\declaraciones\Pagos"
path_constancias = r"\\192.168.1.201\avisos al rfc"
path_info_contribuyente = r"\\192.168.1.201\avisos al rfc\INFORMACION_CONTRIBUYENTE"


rutas = [path_declaraciones, path_constancias]

# Esta funcion estar en tetsing
Archivos = Clasificador_Archivos(rutas, path_raiz_cliente, EJERCICIO=EJERCICIO)



# Funcion que obtiene los archivos con su ruta y se encarga de clasificarlos en arreglos

# Archivos = (ArchivosPDF_LH(path_raiz_cliente, cliente, EJERCICIO=EJERCICIO))


# Funciones para cada tipo de archivo




# Generacion de Dataframes por cadatipo de Archivo


try:

    # PAGOS
    column_names=["PDF","RFC", "Entidad", "Tipo", "Fecha Presentacion", "Importe a Pagar", "Linea de Captura", "Num Operacion", "Vigencia", "Tipo de Declaracion", "Fecha de Pago","Concepto de Pago","Pago por Concepto","Numero de Concepto", "Path", "pdf base64"]
    df_Pagos = pd.DataFrame(exportDataPagos(Archivos[2]), columns=column_names)
    # print(df_Pagos)
    # df_Pagos

    # # ACUSE Declaracion
    column_names = ["PDF","RFC","Fecha y hora presentacion","Num de Operacion","Periodo de Declaracion","Ejercicio","Total a Pagar","Vigente Hasta","Linea de Captura","Razon Social","Tipo Social","Impuesto a Favor","Concepto de Pago","Pago por Concepto","Numero de Concepto" ,"Path", "pdf base64"]
    df_Declaracion = pd.DataFrame(exportDataDeclaracion(Archivos[1]), columns=column_names)

    # # # ACUSE Acuse
    # column_names = ["PDF","RFC","Fecha y hora presentacion","Num de Operacion","Periodo de Declaracion","Ejercicio","Total a Pagar","Vigente Hasta","Linea de Captura","Razon_Social","Impuesto a Favor","Path", "pdf base64"]
    # df_Acuse_Presentacion = pd.DataFrame(exportDataAcuseRecepcion(Archivos_Acuse_Presentacion), columns=column_names)

    # # DIOT
    column_names = ["PDF","Usuario", "Archivo Recibido", "tamanio","Fecha_Recepcion", "Hora_Recepcion", "Folio", "Path", "pdf base64"]
    df_Diot = pd.DataFrame(exportDataDiot(Archivos[4]), columns=column_names)

    # CONTANCIA
    column_names=["PDF","RFC", "Razon Social", "CURP", "Primer Apellido", "Segundo Apellido", "Nombre Comercial", "Fecha Operacion", "Estatus", "Regimenes", "Path", "pdf base64"]
    df_Constancia = pd.DataFrame(exportDataConstancia(Archivos[3]), columns=column_names)


    # Opinion de cumplimiento
    column_names=["PDF","RFC", "Folio", "Path", "pdf base64"]
    df_Opinion_Cumplimiento =  pd.DataFrame(exportDataOpinionCumplimiento(Archivos[5]), columns=column_names)

    # Información Contribuyente
    column_names=["PDF","RFC", "Nombre","Usuario","Calle Numero", "Estado", "Contraseña","Contraseña Firma", "Contraseña SIPARE", "Cuenta SIPARE" "Path", "pdf base64"]
    df_Informacion_Controbuyente =  pd.DataFrame(exportData_Info_Contribuyente(Archivos[6]), columns=column_names)

    # Sin Clasificar
    column_names=["Documentos sin clasificar"]
    df_no_identificados =  pd.DataFrame(Archivos[0], columns=column_names)

    # Export = pd.concat([df_Declaracion,
    #                     df_Acuse_Presentacion,
    #                     df_Diot,
    #                     df_Constancia,
    #                     df_Opinion_Cumplimiento,
    #                     df_Pagos
    #                     ])

    # Export
    # import sys
    # !{sys.executable} -m pip install xlsxwriter
    
    
    # ----------------------------------------------------------------------------------------------------------------------
    # Logica Almacenamiento de base de datos
    # ...
    
    # ----------------------------------------------------------------------------------------------------------------------
    # Export Data to Excel
    # import os
    
    # dir = 'F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes'
    for f in os.listdir(dir_excel):
        os.remove(os.path.join(dir_excel, f))
    

    df_Pagos.to_excel(dir_excel+'/df_Pagos.xlsx', header=True, index=None)
    df_Declaracion.to_excel(dir_excel+'/df_Declaracion.xlsx', header=True, index=None)
    # df_Acuse_Presentacion.to_excel('F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes/df_Acuse_Presentacion.xlsx', header=True, index=None)
    df_Diot.to_excel(dir_excel+'/df_Diot.xlsx', header=True, index=None)
    df_Constancia.to_excel(dir_excel+'/df_Constancia.xlsx', header=True, index=None)
    df_no_identificados.to_excel(dir_excel+'/df_no_Clasificados.xlsx', header=True, index=None)

except Exception as e:
    print("Error al llamar funciones de lectura:", e)
