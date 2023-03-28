import PyPDF2
import pandas as pd
import numpy as np
import sys, os
import json
import re

# root = r"C:\Users\Victor\Documents\Cursos\Python\Automatizacion\PDF"
root = r"../PDF/"
path = os.path.join(root, "PDF")

# Funcion que obtiene los archivos con su ruta y se encarga de clasificarlos en arreglos
def ArchivosPDF(root, path):
    Archivos_Acuse_Recepcion = []
    Archivos_Opinion_Cumplimiento = []
    Archivos_Acuse_Presentacion = []
    Archivos_Constancia = []
    Archivos_Diot = []
    Archivos_no_clasificados = []
    
    for path, subdirs, files in os.walk(root):
        for name in files:
            # print(os.path.join(path, name))
            if os.path.join(name).endswith(".pdf"):
                #Archivos Acuse Recepcion
                if os.path.join(name).startswith("acuse recepcion"):
                    Archivos_Acuse_Recepcion.append(os.path.join(path, name))
                elif os.path.join(name).startswith("opinion cumplimiento"):
                    Archivos_Opinion_Cumplimiento.append(os.path.join(path, name))
                elif os.path.join(name).startswith("acuse presentacion"):
                    Archivos_Acuse_Presentacion.append(os.path.join(path, name))
                elif os.path.join(name).startswith("constancia"):
                    Archivos_Constancia.append(os.path.join(path, name))
                elif os.path.join(name).startswith("diot"):
                    Archivos_Diot.append(os.path.join(path, name))
                else: 
                    Archivos_no_clasificados.append(os.path.join(path, name))
                    
    return Archivos_Acuse_Recepcion, Archivos_Opinion_Cumplimiento, Archivos_Acuse_Presentacion, Archivos_Constancia,Archivos_Diot, Archivos_no_clasificados


# -> Papelines de Extraccion 

# Varibales de PDF's'
# Se asigna el tipo de pdf a un variable

Archivos_Acuse_Recepcion = (ArchivosPDF(root, path)[0])         #--> Solo contiene 1 archivo
Archivos_Opinion_Cumplimiento = (ArchivosPDF(root, path)[1])    #--> Solo contiene 1 archivo
Archivos_Acuse_Presentacion = (ArchivosPDF(root, path)[2])      #--> °Contiene archivos Dummies y 1 original para pruebas
Archivos_Constancia = (ArchivosPDF(root, path)[3])              #--> Solo contiene 1 archivo
Archivos_Diot = (ArchivosPDF(root, path)[4])         #--> Solo contiene 1 archivo
Archivos_no_clasificados = (ArchivosPDF(root, path)[5])         #--> Solo contiene 1 archivo


print("Files Acuse Recepcion: ", len(Archivos_Acuse_Recepcion))
print("Files Opinion Cumplimineto: ",len(Archivos_Opinion_Cumplimiento))
print("Files Acuse Presentacion: ",len(Archivos_Acuse_Presentacion))
print("Files Constancia: ",len(Archivos_Constancia))
print("Files Diot: ",len(Archivos_Diot))
print("Files Sin Clasificacion: ",len(Archivos_no_clasificados))


# Principal Functions Text Mining by PDF types
# -> Each function returns a numpy array with the result found but, if not found, defaults to NA
# -> Each function uses "txt" value containing all the text by per PDF iteration
# -> Each function should return the headers so, that they are recognized on the first line by Pandas


def exportDataAcusePresentacion(Archivos):
    array_docs = []
    for i in range(len(Archivos)):

        pdf = open(Archivos[i], 'rb')
        # print(Archivos[i])
        reader = PyPDF2.PdfReader(pdf)
        page = reader.pages
        texto = ''

        for pag in range(len(page)):
            # print("pdf: ", i+1, "pagina: ",pag+1)
            texto += reader._get_page(pag).extractText()

        print("PDF: ", i+1)
        txt = re.sub("\n", " ", texto)
        # print(txt)  # Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES

        # rfc
        rfc = re.search("RFC:.(.*?\s)", txt)[0]
        # Fecha
        try:
            Fecha_y_hora_presentacion = re.search(
                "Fecha y hora de presentaci.n:.{11}", txt)[0]
        except:
            Fecha_y_hora_presentacion = "NA"

        # numero de operacion
        try:
            Num_de_Operacion = re.search(
                "N.mero de operaci.n:.(\d*?\s)", txt)[0]
        except:
            Num_de_Operacion = "NA"
        # periodo de la declaracion
        try:
            Periodo_de_declaracion = re.search(
                "Per.odo de la declaraci.n:\s.(.+?\s)", txt)[0]
        except:
            Periodo_de_declaracion = "NA"
        # Ejercicio
        try:
            Ejercicio = re.search("Ejercicio:\s.(.+?\s)", txt)[0]
        except:
            Ejercicio = "NA"
        # Denominación o razón social:

        try:
            RazonSocial = re.search("Hoja\d\sde\s\d.(.*?)Tipo", txt).group(1)
        except:
            RazonSocial = 'NA'

        # SELECCION LINEA DE CAPTURA
        try:
            total_a_pagar = re.search("total a pagar:(.+?\s)", txt)[0]
            Vigente_hasta = re.search("Vigente hasta:(.+?\s)", txt)[0]
            Linea_de_Captura = "Linea de Captura : " + \
                re.search("Línea de Captura:.(.*?)Importe", txt).group(1)
        except:
            total_a_pagar = "total a pagar: NA "
            Vigente_hasta = "Vigente hasta: NA "
            Linea_de_Captura = "Linea de Captura : NA "
        # SALDO A FAVOR
        try:
            Impuesto_a_favor = re.search(
                "Impuesto.a.favor:.(.*?)ACUSE", txt).group(1)
            Impuesto_a_favor = re.split(' ', Impuesto_a_favor)[0]
            # print(Impuesto_a_favor)
        except:
            Impuesto_a_favor = 'NA'

        # data_fila = [rfc, Fecha_y_hora_presentacion, Num_de_Operacion, Periodo_de_declaracion, Ejercicio,  total_a_pagar, Vigente_hasta, Linea_de_Captura, Archivos[i]]
        

        data_fila = np.array([
            rfc,
            Fecha_y_hora_presentacion,
            Num_de_Operacion,
            Periodo_de_declaracion,
            Ejercicio,
            total_a_pagar,
            Vigente_hasta,
            Linea_de_Captura,
            RazonSocial,
            Impuesto_a_favor,
            Archivos[i]])
        array_docs.append(data_fila)

    return array_docs


def exportDataDiot(Archivos):
    array_docs = []
    for i in range(len(Archivos)):

        pdf = open(Archivos[i], 'rb')
        # print(Archivos[i])
        reader = PyPDF2.PdfReader(pdf)
        page = reader.pages
        texto = ''

        for pag in range(len(page)):
            # print("pdf: ", i+1, "pagina: ",pag+1)
            texto += reader._get_page(pag).extractText()

        print("PDF: ", i+1)
        txt = re.sub("\n", " ", texto)
        # print(txt) #Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES

        # Usuario
        try:
            usuario = re.search("Usuario:.(.+?\s)", txt)[0]
        except:
            usuario = "NA"

        # Archivo
        try:
            Archivo_Recibido = re.search("Archivo Recibido:.(.+?\s)", txt)[0]
        except:
            Archivo_Recibido = "NA"

        # Tamanio
        try:
            tamanio = re.search("Tama.o:.(.+?\s)", txt)[0]
        except:
            tamanio = "NA"
        # Fecha de recepcion
        try:
            Fecha_Recepcion = re.search("Fecha de Recepci.n:.(.+?\s)", txt)[0]
        except:
            Fecha_Recepcion = "NA"
        # Hora de recepcion
        try:
            Hora_Recepcion = re.search("Hora de Recepci.n:.(.+?\s)", txt)[0]
        except:
            Hora_Recepcion = "NA"
        # Folio
        try:
            Folio = re.search("Folio de Recepci.n:.(.+?\s)", txt)[0]
        except:
            Folio = "NA"

        

        data_fila = np.array([
            usuario,
            Archivo_Recibido,
            tamanio,
            Fecha_Recepcion,
            Hora_Recepcion,
            Folio,
            Archivos[i]
        ])
        array_docs.append(data_fila)

    return array_docs


def exportDataConstancia(Archivos):
    array_docs = []
    for i in range(len(Archivos)):

        pdf = open(Archivos[i], 'rb')
        # print(Archivos[i])
        reader = PyPDF2.PdfReader(pdf)
        page = reader.pages
        texto = ''

        for pag in range(len(page)):
            # print("pdf: ", i+1, "pagina: ",pag+1)
            texto += reader._get_page(pag).extractText()

        # print("PDF: ", i+1)
        txt = re.sub("\n", " ", texto)
        # print(txt)  # Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES

        # RFC
        try:
            rfc = re.search("RFC:.(.+?\s)", txt).group(1)
        except:
            rfc = "NA"
        # RazonSocial/CURP
        try:
            Razon_Social_Nombre = re.search(
                ".Social:.(.+?\s)R.gimen", txt)[0][:-8]
            Razon_Social_Nombre = re.split(':', Razon_Social_Nombre)[1]
        except:
            try:
                Razon_Social_Nombre = re.search(".CURP:.(.+?\s)", txt)[0]
                Razon_Social_Nombre = re.split(':', Razon_Social_Nombre)[1]
            except:
                Razon_Social_Nombre = "NA"

        # REGIMEN CAPITAL O NOMBRE
        try:
            Regimen_Nombre = re.search(".CURP:.(.+?\s)", txt)[0]
            Regimen_Nombre = re.split(':', Regimen_Nombre)[1]
        except:
            try:
                Regimen_Nombre = re.search(".CURP:.(.+?\s)", txt)[0]
            except:
                Regimen_Nombre = "NA"
        # PRIMER APELLIDO
        try:
            Primer_Apellido = re.search("PrimerApellido:(.+?\s)", txt)[0]
        except:
            Primer_Apellido = 'NA'
        # SEGUNDO APELLIDO
        try:
            Segundo_Apellido = re.search("Segundo.Apellido:(.+?\s)", txt)[0]
        except:
            Segundo_Apellido = 'NA'
        # NOMBRE COMERICAL
        try:
            Nombre_Comercial = re.search(
                "NombreComercial:(.+?\s)Fecha.", txt).group(1)[1:]
            if Nombre_Comercial.startswith('Fecha') or Nombre_Comercial.startswith('Datos del domicilio'):
                Nombre_Comercial = 'NA'
            if re.findall('Datos.', Nombre_Comercial):
                Nombre_Comercial = re.split('Datos.', Nombre_Comercial)[0]

        except:
            Nombre_Comercial = 'NA'
        # FECHA OPERACIONES
        try:
            Fecha_Operaciones = re.search(
                "Fechainiciodeoperaciones:(.+?\s)Estatus", txt).group(1)[:-1]
        except:
            Fecha_Operaciones = 'NA'
        # ESTATUS
        try:
            Estatus = re.search("Estatusenelpadr.n:(.+?\s)", txt)[0]
        except:
            Estatus = 'NA'
        # REGIMENES
        try:
            Regimenes = re.search("Reg.menes:(.+?\s)Obligaciones", txt)[0]

        except:
            Regimenes = 'NA'

        

        data_fila = np.array([
            rfc,
            Razon_Social_Nombre,
            Regimen_Nombre,
            Primer_Apellido,
            Segundo_Apellido,
            Nombre_Comercial,
            Fecha_Operaciones,
            Estatus,
            Regimenes,
            Archivos[i]
        ])
        array_docs.append(data_fila)
        

    return array_docs


def exportDataOpinionCumplimiento(Archivos):
    array_docs = []
    for i in range(len(Archivos)):

        pdf = open(Archivos[i], 'rb')
        # print(Archivos[i])
        reader = PyPDF2.PdfReader(pdf)
        page = reader.pages
        texto = ''

        for pag in range(len(page)):
            # print("pdf: ", i+1, "pagina: ",pag+1)
            texto += reader._get_page(pag).extractText()

        print("PDF: ", i+1)
        txt = re.sub("\n", " ", texto)
        print(txt)  # Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES

        # Folio
        try:
            folio = re.search('Folio.(.+?\s)(.+?\s)Respuesta', txt).group(2)
            print(folio)
        except:
            folio = 'NA'
        # Clave RFC
        try:
            RFC = re.search('Folio.(.+?\s)(.+?\s)Respuesta', txt).group(1)
            print(RFC)
        except:
            RFC = 'NA'

        data_fila = np.array([
            folio,
            RFC,
            Archivos[i]
        ])
        array_docs.append(data_fila)

    return array_docs


# # ACUSE RECEPCION
column_names = ["rfc","Fecha_y_hora_presentacion","Num_de_Operacion","Periodo_de_declaracion","Ejercicio","total_a_pagar","Vigente_hasta","Linea_de_Captura","RazonSocial","Impuesto_a_favor","Path"]
df_Acuse_Recepcion = pd.DataFrame(exportDataAcusePresentacion(Archivos_Acuse_Recepcion), columns=column_names)

# # DIOT
column_names = ["usuario", "Archivo_Recibido", "tamanio","Fecha_Recepcion", "Hora_Recepcion", "Folio", "Path"]
df_Diot = pd.DataFrame(exportDataDiot(Archivos_Diot), columns=column_names)


# CONTANCIA
column_names=["RFC", "Razon Social", "CURP", "Primer Apellido", "Segundo Apellido", "Nombre Comercial", "Fecha de Operacion", "Estatus", "Regimenes", "Path"]
df_Constancia = pd.DataFrame(exportDataConstancia(Archivos_Constancia), columns=column_names)



# Prueba
# datos_Opinion = exportDataOpinionCumplimiento(Archivos_Opinion_Cumplimiento)

# df = pd.DataFrame(datos_Opinion)
# df
