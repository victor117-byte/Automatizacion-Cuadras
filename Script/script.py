import PyPDF2
import pandas as pd
import numpy as np
import sys, os
import json
import re

# root = r"C:\Users\Victor\Documents\Cursos\Python\Automatizacion\PDF"
root = r"C:\Users\victo\Documents\Proyectos\Automatizacion-Cuadras\PDF"
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
            # texto += reader._get_page(pag).extractText()
            texto += reader._get_page(pag).extract_text()

        # print("PDF: ", i+1)
        txt = re.sub("\n", " ", texto)
        # print(txt)  # Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES

        # rfc
        rfc = re.search("RFC:.(.*?\s)", txt).group(1)
        # Fecha
        try:
            Fecha_y_hora_presentacion = re.search(
                "Fecha y hora de presentaci.n:.{11}", txt)[0]
            Fecha_y_hora_presentacion = re.split(':', Fecha_y_hora_presentacion)[1]
        except:
            Fecha_y_hora_presentacion = "NA"

        # numero de operacion
        try:
            Num_de_Operacion = re.search(
                "N.mero de operaci.n:.(\d*?\s)", txt).group(1)
        except:
            Num_de_Operacion = "NA"
        # periodo de la declaracion
        try:
            Periodo_de_declaracion = re.search(
                "Per.odo de la declaraci.n:\s(.+?\s)", txt).group(1)
        except:
            Periodo_de_declaracion = "NA"
        # Ejercicio
        try:
            Ejercicio = re.search("Ejercicio:\s(.+?\s)", txt).group(1)
        except:
            Ejercicio = "NA"
        # Denominación o razón social:

        try:
            RazonSocial = re.search("Hoja\d\sde\s\d.(.*?)Tipo", txt).group(1)
        except:
            RazonSocial = 'NA'

        # SELECCION LINEA DE CAPTURA
        try:
            total_a_pagar = re.search("total a pagar:(.+?\s)", txt).group(1)
            Vigente_hasta = re.search("Vigente hasta:(.+?\s)", txt).group(1)
            Linea_de_Captura = "Linea de Captura : " + \
                re.search("Línea de Captura:.(.*?)Importe", txt).group(1)
        except:
            total_a_pagar = "NA"
            Vigente_hasta = "NA"
            Linea_de_Captura = "NA "
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
            "Acuse Recepcion",
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

def exportDataAcuseRecepcion(Archivos):
    array_docs = []
    for i in range(len(Archivos)):

        pdf = open(Archivos[i], 'rb')
        # print(Archivos[i])
        reader = PyPDF2.PdfReader(pdf)
        page = reader.pages
        texto = ''

        for pag in range(len(page)):
            # print("pdf: ", i+1, "pagina: ",pag+1)
            # texto += reader._get_page(pag).extractText()
            texto += reader._get_page(pag).extract_text()

        # print("PDF: ", i+1)
        txt = re.sub("\n", " ", texto)
        # print(txt)  # Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES

        # rfc
        rfc = re.search("RFC:.(.*?\s)", txt).group(1)
        # Fecha
        try:
            Fecha_y_hora_presentacion = re.search(
                "Fecha y hora de presentaci.n:.{11}", txt)[0]
            Fecha_y_hora_presentacion = re.split(':', Fecha_y_hora_presentacion)[1]
        except:
            Fecha_y_hora_presentacion = "NA"

        # numero de operacion
        try:
            Num_de_Operacion = re.search(
                "N.mero de operaci.n:.(\d*?\s)", txt).group(1)
        except:
            Num_de_Operacion = "NA"
        # periodo de la declaracion
        try:
            Periodo_de_declaracion = re.search(
                "Per.odo de la declaraci.n:\s(.+?\s)", txt).group(1)
        except:
            Periodo_de_declaracion = "NA"
        # Ejercicio
        try:
            Ejercicio = re.search("Ejercicio:\s(.+?\s)", txt).group(1)
        except:
            Ejercicio = "NA"
        # Denominación o razón social:

        try:
            RazonSocial = re.search("Hoja\d\sde\s\d.(.*?)Tipo", txt).group(1)
        except:
            RazonSocial = 'NA'

        # SELECCION LINEA DE CAPTURA
        try:
            total_a_pagar = re.search("total a pagar:(.+?\s)", txt).group(1)
            Vigente_hasta = re.search("Vigente hasta:(.+?\s)", txt).group(1)
            Linea_de_Captura = "Linea de Captura : " + \
                re.search("Línea de Captura:.(.*?)Importe", txt).group(1)
        except:
            total_a_pagar = "NA"
            Vigente_hasta = "NA"
            Linea_de_Captura = "NA "
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
            "Acuse Recepcion",
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
            # texto += reader._get_page(pag).extractText()
            texto += reader._get_page(pag).extract_text()

        # print("PDF: ", i+1)
        txt = re.sub("\n", " ", texto)
        # print(txt) #Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES

        # Usuario
        try:
            usuario = re.search("Usuario:.(.+?\s)", txt)[0]
            usuario = re.split(':', usuario)[1]
        except:
            usuario = "NA"

        # Archivo
        try:
            Archivo_Recibido = re.search("Archivo Recibido:.(.+?\s)", txt)[0]
            Archivo_Recibido = re.split(":_", Archivo_Recibido)[1]
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
            Fecha_Recepcion = re.split(':', Fecha_Recepcion)[1]
        except:
            Fecha_Recepcion = "NA"
        # Hora de recepcion
        try:
            Hora_Recepcion = re.search("Hora de Recepci.n:.(.+?\s)", txt)[0]
            Hora_Recepcion = re.split('Recepci.n:', Hora_Recepcion)[1]
        except:
            Hora_Recepcion = "NA"
        # Folio
        try:
            Folio = re.search("Folio de Recepci.n:.(.+?\s)", txt)[0]
            Folio = re.split(':', Folio)[1]
        except:
            Folio = "NA"

        

        data_fila = np.array([
            "Diot",
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
            # texto += reader._get_page(pag).extractText()
            texto += reader._get_page(pag).extract_text()

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
            Primer_Apellido = re.search("PrimerApellido:(.+?\s)", txt).group(1)
        except:
            Primer_Apellido = 'NA'
        # SEGUNDO APELLIDO
        try:
            Segundo_Apellido = re.search("Segundo.Apellido:(.+?\s)", txt).group(1)
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
            Estatus = re.search("Estatusenelpadr.n:(.+?\s)", txt).group(1)
        except:
            Estatus = 'NA'
        # REGIMENES
        try:
            Regimenes = re.search("Reg.menes:(.+?\s)Obligaciones", txt)[0]

        except:
            Regimenes = 'NA'

        

        data_fila = np.array([
            "Constancia",
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
            # texto += reader._get_page(pag).extractText()
            texto += reader._get_page(pag).extract_text()

        # print("PDF: ", i+1)
        txt = re.sub("\n", " ", texto)
        # print(txt)  # Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES

        # Folio
        try:
            folio = re.search('Folio.(.+?\s)(.+?\s)Respuesta', txt).group(2)
            # print(f'Folio: {folio} Tiene una longitud de: ', len(folio))
        except:
            folio = 'NA'
        # Clave RFC
        try:
            RFC = re.search('Folio.(.+?\s)(.+?\s)Respuesta', txt).group(1)
            # print(f'RFC: {RFC} Tiene una longitud de: ', len(RFC))
        except:
            RFC = 'NA'

        data_fila = np.array([
            'Opinion cumplimiento',
            RFC,
            folio,
            Archivos[i]
        ])
        array_docs.append(data_fila)

    return array_docs


# # ACUSE RECEPCION
column_names = ["PDF","RFC","Fecha_y_hora_presentacion","Num_de_Operacion","Periodo_de_declaracion","Ejercicio","total_a_pagar","Vigente_hasta","Linea_de_Captura","Razon_Social","Impuesto_a_favor","Path"]
df_Acuse_Recepcion = pd.DataFrame(exportDataAcuseRecepcion(Archivos_Acuse_Recepcion), columns=column_names)

# # ACUSE Presentacion
column_names = ["PDF","RFC","Fecha_y_hora_presentacion","Num_de_Operacion","Periodo_de_declaracion","Ejercicio","total_a_pagar","Vigente_hasta","Linea_de_Captura","Razon_Social","Impuesto_a_favor","Path"]
df_Acuse_Presentacion = pd.DataFrame(exportDataAcusePresentacion(Archivos_Acuse_Presentacion), columns=column_names)

# # DIOT
column_names = ["PDF","Usuario", "Archivo_Recibido", "tamanio","Fecha_Recepcion", "Hora_Recepcion", "Folio", "Path"]
df_Diot = pd.DataFrame(exportDataDiot(Archivos_Diot), columns=column_names)


# CONTANCIA
column_names=["PDF","RFC", "Razon_Social", "CURP", "Primer_Apellido", "Segundo_Apellido", "Nombre_Comercial", "Fecha_Operacion", "Estatus", "Regimenes", "Path"]
df_Constancia = pd.DataFrame(exportDataConstancia(Archivos_Constancia), columns=column_names)



# Opinion de cumplimiento
column_names=["PDF","RFC", "Folio", "Path"]
df_Opinion_Cumplimiento =  pd.DataFrame(exportDataOpinionCumplimiento(Archivos_Opinion_Cumplimiento), columns=column_names)

Export = pd.concat([df_Acuse_Recepcion,
                    df_Acuse_Presentacion,
                    df_Diot,
                    df_Constancia,
                    df_Opinion_Cumplimiento
                    ])

# Export