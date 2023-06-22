import PyPDF2
import pandas as pd
import numpy as np
import sys, os
import json
import re


# root = r"C:\Users\victo\Documents\Proyectos\Automatizacion-Cuadras\PDF\PDF"
root = r"F:\Indicadores\PDF"
# root = r"C:\Users\victo\Documents\Proyectos\Automatizacion-Cuadras\PDF"
path = os.path.join(root, "PDF")

# Funcion que obtiene los archivos con su ruta y se encarga de clasificarlos en arreglos
def ArchivosPDF(root, path):
    Archivos_Acuse_Recepcion = []
    Archivos_Opinion_Cumplimiento = []
    Archivos_Acuse_Presentacion = []
    Archivos_Constancia = []
    Archivos_Diot = []
    Archivos_Pago = []
    Archivos_no_clasificados = []
    
    for path, subdirs, files in os.walk(root):
        for name in files:
            # print(os.path.join(path, name))
            if os.path.join(name).endswith(".pdf"):
                #Archivos Acuse Recepcion
                # print(os.path.join(name))
                if os.path.join(name).upper().startswith("DECLARACION"):
                    Archivos_Acuse_Recepcion.append(os.path.join(path, name))
                elif os.path.join(name).upper().startswith("OPINION"):
                    Archivos_Opinion_Cumplimiento.append(os.path.join(path, name))
                elif os.path.join(name).startswith("acuse presentacion"):
                    Archivos_Acuse_Presentacion.append(os.path.join(path, name))
                elif os.path.join(name).upper().startswith("CONSTANCIA"):
                    Archivos_Constancia.append(os.path.join(path, name))
                elif os.path.join(name).upper().startswith("DIOT"):
                    Archivos_Diot.append(os.path.join(path, name))
                elif os.path.join(name).upper().startswith("PAGO"):
                    Archivos_Pago.append(os.path.join(path, name))
                else: 
                    Archivos_no_clasificados.append(os.path.join(path, name))
                    
    return Archivos_Acuse_Recepcion, Archivos_Opinion_Cumplimiento, Archivos_Acuse_Presentacion, Archivos_Constancia, Archivos_Diot, Archivos_Pago, Archivos_no_clasificados


# -> Papelines de Extraccion 

# Varibales de PDF's'
# Se asigna el tipo de pdf a un variable

Archivos_Declaracion = (ArchivosPDF(root, path)[0])         #--> Solo contiene 1 archivo
Archivos_Opinion_Cumplimiento = (ArchivosPDF(root, path)[1])    #--> Solo contiene 1 archivo
Archivos_Acuse_Presentacion = (ArchivosPDF(root, path)[2])      #--> °Contiene archivos Dummies y 1 original para pruebas
Archivos_Constancia = (ArchivosPDF(root, path)[3])              #--> Solo contiene 1 archivo
Archivos_Diot = (ArchivosPDF(root, path)[4])                    #--> Solo contiene 1 archivo
Archivos_Pagos = (ArchivosPDF(root, path)[5])         #--> Solo contiene 1 archivo
Archivos_no_clasificados = (ArchivosPDF(root, path)[6])         #--> Solo contiene 1 archivo


print("Files Declaracion: ", len(Archivos_Declaracion))
print("Files Opinion Cumplimineto: ",len(Archivos_Opinion_Cumplimiento))
print("Files Acuse Presentacion: ",len(Archivos_Acuse_Presentacion))
print("Files Constancia: ",len(Archivos_Constancia))
print("Files Diot: ",len(Archivos_Diot))
print("Files Pagos: ",len(Archivos_Pagos))
print("Files Sin Clasificacion: ",len(Archivos_no_clasificados))


# Principal Functions Text Mining by PDF types
# -> Each function returns a numpy array with the result found but, if not found, defaults to NA
# -> Each function uses "txt" value containing all the text by per PDF iteration
# -> Each function should return the headers so, that they are recognized on the first line by Pandas


def exportDataDeclaracion(Archivos):
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
            Fecha_y_hora_presentacion = ""

        # numero de operacion
        try:
            Num_de_Operacion = re.search(
                "N.mero de operaci.n:.(\d*?\s)", txt).group(1)
        except:
            Num_de_Operacion = ""
        # periodo de la declaracion
        try:
            Periodo_de_declaracion = re.search(
                "Per.odo de la declaraci.n:\s(.+?\s)", txt).group(1)
        except:
            Periodo_de_declaracion = ""
        # Ejercicio
        try:
            Ejercicio = re.search("Ejercicio:\s(.+?\s)", txt).group(1)
        except:
            Ejercicio = ""
        # Denominación o razón social:

        try:
            RazonSocial_base = re.search("Hoja\d\sde\s\d.(.*?)Tipo", txt).group(1)
            RazonSocial = RazonSocial_base.split(": ")[1]
            if RazonSocial_base.split(":")[0] =="Nombre":
                Tipo_RazonSocial = "Persona Fisica"
            else:
                Tipo_RazonSocial = "Persona Moral"

        except:
            RazonSocial = ""
            Tipo_RazonSocial = ""

        # SELECCION LINEA DE CAPTURA
        try:
            total_a_pagar = re.search("total a pagar:(.+?\s)", txt).group(1)
            Vigente_hasta = re.search("Vigente hasta:(.+?\s)", txt).group(1)
            Linea_de_Captura = re.search("Línea de Captura:.(.*?)Importe", txt).group(1)
        except:
            total_a_pagar = ""
            Vigente_hasta = ""
        
        # LINEA DE CAPTURA  
        try:
            Linea_de_Captura = re.search("Línea de Captura:(.*?)Importe", txt).group(1)
        except:
            Linea_de_Captura = ""
        # SALDO A FAVOR
        try:
            Impuesto_a_favor = re.search(
                "Impuesto.a.favor:.(.*?)ACUSE", txt).group(1)
            Impuesto_a_favor = re.split(' ', Impuesto_a_favor)[0]
            # print(Impuesto_a_favor)
        except:
            Impuesto_a_favor = ""

        # data_fila = [rfc, Fecha_y_hora_presentacion, Num_de_Operacion, Periodo_de_declaracion, Ejercicio,  total_a_pagar, Vigente_hasta, Linea_de_Captura, Archivos[i]]
        # print(txt)
        arreglo_conceptos = funcion_Conceptos(txt)
        # print(f">>>{arreglo_conceptos}")
            
        for w in range(len(arreglo_conceptos)):
            # print("----datos ----")
            Numero_Concepto = w+1
            try: 
                for values in arreglo_conceptos[w].values(): 
                    Precio_por_concepto = values

                for keys in arreglo_conceptos[w].keys():
                    concepto = keys
            except:
                Precio_por_concepto = ""
                concepto =""
            # print(arreglo_conceptos[w])
            data_fila = np.array([
                "Declaracion",
                rfc,
                Fecha_y_hora_presentacion,
                Num_de_Operacion,
                Periodo_de_declaracion,
                Ejercicio,
                total_a_pagar,
                Vigente_hasta,
                Linea_de_Captura,
                RazonSocial,
                Tipo_RazonSocial,
                Impuesto_a_favor,
                concepto,
                Precio_por_concepto,
                str(Numero_Concepto),
                Archivos[i]
                ])
            # print(data_fila)
            array_docs.append(data_fila)
        
        # print(array_rows)
        
        # array_docs.append(data_fila)
    return array_docs

    #     data_fila = np.array([
    #         "Declaracion",
    #         rfc,
    #         Fecha_y_hora_presentacion,
    #         Num_de_Operacion,
    #         Periodo_de_declaracion,
    #         Ejercicio,
    #         total_a_pagar,
    #         Vigente_hasta,
    #         Linea_de_Captura,
    #         RazonSocial,
    #         Impuesto_a_favor,
    #         Archivos[i]])
    #     array_docs.append(data_fila)

    # return array_docs

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
            Fecha_y_hora_presentacion = ""

        # numero de operacion
        try:
            Num_de_Operacion = re.search(
                "N.mero de operaci.n:.(\d*?\s)", txt).group(1)
        except:
            Num_de_Operacion = ""
        # periodo de la declaracion
        try:
            Periodo_de_declaracion = re.search(
                "Per.odo de la declaraci.n:\s(.+?\s)", txt).group(1)
        except:
            Periodo_de_declaracion = ""
        # Ejercicio
        try:
            Ejercicio = re.search("Ejercicio:\s(.+?\s)", txt).group(1)
        except:
            Ejercicio = ""
        # Denominación o razón social:

        try:
            RazonSocial = re.search("Hoja\d\sde\s\d.(.*?)Tipo", txt).group(1)
        except:
            RazonSocial = ""

        # SELECCION LINEA DE CAPTURA
        try:
            total_a_pagar = re.search("total a pagar:(.+?\s)", txt).group(1)
            Vigente_hasta = re.search("Vigente hasta:(.+?\s)", txt).group(1)
            Linea_de_Captura = "Linea de Captura : " + \
                re.search("L.nea de Captura:(.*?)Importe", txt).group(1)
        except:
            total_a_pagar = ""
            Vigente_hasta = ""
            Linea_de_Captura = "NA "
        # SALDO A FAVOR
        try:
            Impuesto_a_favor = re.search(
                "Impuesto.a.favor:.(.*?)ACUSE", txt).group(1)
            Impuesto_a_favor = re.split(' ', Impuesto_a_favor)[0]
            # print(Impuesto_a_favor)
        except:
            Impuesto_a_favor = ""

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
            usuario = ""

        # Archivo
        try:
            Archivo_Recibido = re.search("Archivo Recibido:.(.+?\s)", txt)[0]
            Archivo_Recibido = re.split(":_", Archivo_Recibido)[1]
        except:
            Archivo_Recibido = ""

        # Tamanio
        try:
            tamanio = re.search("Tama.o:.(.+?\s)", txt)[0]
        except:
            tamanio = ""
        # Fecha de recepcion
        try:
            Fecha_Recepcion = re.search("Fecha de Recepci.n:.(.+?\s)", txt)[0]
            Fecha_Recepcion = re.split(':', Fecha_Recepcion)[1]
        except:
            Fecha_Recepcion = ""
        # Hora de recepcion
        try:
            Hora_Recepcion = re.search("Hora de Recepci.n:.(.+?\s)", txt)[0]
            Hora_Recepcion = re.split('Recepci.n:', Hora_Recepcion)[1]
        except:
            Hora_Recepcion = ""
        # Folio
        try:
            Folio = re.search("Folio de Recepci.n:.(.+?\s)", txt)[0]
            Folio = re.split(':', Folio)[1]
        except:
            Folio = ""

        

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
            rfc = ""
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
                Razon_Social_Nombre = ""

        # REGIMEN CAPITAL O NOMBRE
        try:
            Regimen_Nombre = re.search(".CURP:.(.+?\s)", txt)[0]
            Regimen_Nombre = re.split(':', Regimen_Nombre)[1]
        except:
            try:
                Regimen_Nombre = re.search(".CURP:.(.+?\s)", txt)[0]
            except:
                Regimen_Nombre = ""
        # PRIMER APELLIDO
        try:
            Primer_Apellido = re.search("PrimerApellido:(.+?\s)", txt).group(1)
        except:
            Primer_Apellido = ""
        # SEGUNDO APELLIDO
        try:
            Segundo_Apellido = re.search("Segundo.Apellido:(.+?\s)", txt).group(1)
        except:
            Segundo_Apellido = ""
        # NOMBRE COMERICAL
        try:
            Nombre_Comercial = re.search(
                "NombreComercial:(.+?\s)Fecha.", txt).group(1)[1:]
            if Nombre_Comercial.startswith('Fecha') or Nombre_Comercial.startswith('Datos del domicilio'):
                Nombre_Comercial = ""
            if re.findall('Datos.', Nombre_Comercial):
                Nombre_Comercial = re.split('Datos.', Nombre_Comercial)[0]

        except:
            Nombre_Comercial = ""
        # FECHA OPERACIONES
        try:
            Fecha_Operaciones = re.search(
                "Fechainiciodeoperaciones:(.+?\s)Estatus", txt).group(1)[:-1]
        except:
            Fecha_Operaciones = ""
        # ESTATUS
        try:
            Estatus = re.search("Estatusenelpadr.n:(.+?\s)", txt).group(1)
        except:
            Estatus = ""
        # REGIMENES
        try:
            Regimenes = re.search("Reg.menes:(.+?\s)Obligaciones", txt)[0]

        except:
            Regimenes = ""

        

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
            folio = ""
        # Clave RFC
        try:
            RFC = re.search('Folio.(.+?\s)(.+?\s)Respuesta', txt).group(1)
            # print(f'RFC: {RFC} Tiene una longitud de: ', len(RFC))
        except:
            RFC = ""

        data_fila = np.array([
            'Opinion cumplimiento',
            RFC,
            folio,
            Archivos[i]
        ])
        array_docs.append(data_fila)

    return array_docs

def exportDataPagos(Archivos):
    array_docs = []
    array_rows = []
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
        # print(f">>>TEXTO {i}<<<")
        # print(f"{txt}")  # Muestra el texto en de todo el PDF

        # Text Mining
        # DATOS GENERALES
        
        # Get RFC
        try:
            rfc = re.search("RFC:(.+?\s)", txt).group(1)
            rfc = rfc.strip()
        except:
            rfc = ""
            
        # Razon Social
        try:
            Entidad = re.search("raz.n.social:(.+?)Tipo", txt).group(1)
            Entidad = Entidad.strip()
            Tipo = "Persona Moral"
        except:
            try:
                Entidad = re.search("Nombre:(.+?)Tipo", txt).group(1)
                Entidad = Entidad.strip()
                Tipo = "Persona Fisica"
            except:
                Entidad = ""
                Tipo = ""
                
        # Fecha
        try:
            Fecha_presentacion = re.search("presentaci.n:(.+?\s)", txt).group(1)
            Fecha_presentacion = Fecha_presentacion.strip()
        except:
            Fecha_presentacion = ""
            
        try:
            Importe_a_pagar = re.search("total a pagar:(.+?) Vigente", txt).group(1)
        except:
            Importe_a_pagar = ""
            
        try:
            Linea_de_captura = re.search("Línea de Captura:(.+?)Importe", txt).group(1)
            Linea_de_captura = Linea_de_captura.strip()
        except:
            Linea_de_captura = ""
        try:
            Num_operacion = re.search("N.mero de operaci.n:(.+?)Sello", txt).group(1)
            Num_operacion = Num_operacion.strip()
            try:
                Num_operacion = Num_operacion.split("Fecha")[0]
            except:
                Num_operacion = Num_operacion
        except:
            Num_operacion = ""
            
        # Fecha emision
        try:
            fecha_presentacion = re.search("hora de presentaci.n:.(.+?)Medio", txt).group(1)
            fecha_presentacion = fecha_presentacion.strip()
        except:
            fecha_presentacion = ""
        # Tipo_declaracion 
        try:
            Tipo_declaracion = re.search("Tipo.de.declaraci.n: (.+?)Tipo", txt).group(1)
            Tipo_declaracion = Tipo_declaracion.strip()
            try:
                Tipo_declaracion = Tipo_declaracion.split()[0]
            except: 
                Tipo_declaracion = Tipo_declaracion
        except:
            Tipo_declaracion = ""
        # Vigencia
        try:
            Vigencia = re.search("Vigente hasta: (.+?)Obligado", txt).group(1)
            Vigencia = Vigencia.strip()
        except:
            try:
                Vigencia = re.search("Vigente hasta: (.+?)INFORMACI.N", txt).group(1)
                Vigencia = Vigencia.strip()
            except:
                Vigencia = ""
        # # Periodo de declaracion
        # try:
        #     Periodo = re.search("Vigente hasta: (.+?)Obligado", txt).group(1)
        #     Periodo = Periodo.strip()
        # except:
            # Periodo = ""
        # Fecha de Pago
        try:
            Fecha_de_pago = re.search("Fecha del pago:(.+?) L.nea", txt).group(1)
            Fecha_de_pago = Fecha_de_pago.strip()
        except:
            Fecha_de_pago = ""
            
        # Conceptos de pago
        
        arreglo_conceptos = funcion_Conceptos(txt)
        # print(f">>>{arreglo_conceptos}")
        # print(arreglo_conceptos)
        for w in range(len(arreglo_conceptos)):
            # print("----datos ----")
            Numero_Concepto = w+1
            try: 
                for values in arreglo_conceptos[w].values(): 
                    Precio_por_concepto = values

                for keys in arreglo_conceptos[w].keys():
                    concepto = keys
            except:
                Precio_por_concepto = ""
                concepto =""
            # print(arreglo_conceptos[w])
            data_fila = np.array([
                'Acuse Confirmacion de Pago',
                rfc,
                Entidad,
                Tipo,
                Fecha_presentacion,
                Importe_a_pagar,
                Linea_de_captura,
                Num_operacion,
                Vigencia,
                Tipo_declaracion,
                # Periodo,
                Fecha_de_pago,
                concepto,
                Precio_por_concepto,
                str(Numero_Concepto),
                Archivos[i]
                ])
            # print(data_fila)
            array_docs.append(data_fila)
        
        # print(array_rows)
        
        # array_docs.append(data_fila)
    return array_docs


def funcion_Conceptos(txt):
    Array_Conceptos = []
    Conceptos = re.findall("Concepto de pago \d:", txt)
    # print(f"Cantidad-> {len(Conceptos)}")
    numero_Pagos_por_concepto = re.findall("Cantidad a pagar:.(.+? )", txt)
    # print(f"Numero de conceptos de pago: {len(numero_Pagos_por_concepto)}")
    # print(txt)
    
    num_2 = 0
    for i in range(7):
        num = i+1
        
        try: 
            _txt_concepto = "Concepto.de.pago."+str(num)+":(.+?)A cargo" #Concepto de pago.1:(.+?) Impuesto
            _Concepto = re.search(_txt_concepto, txt).group(1)
            _Concepto = _Concepto.strip()
        except:
            try:
                _txt_concepto = "Concepto.de.pago."+str(num)+":(.+?).Imp" #Concepto de pago.1:(.+?) A cargo
                _Concepto = re.search(_txt_concepto, txt).group(1)
                _Concepto = _Concepto.strip()
            except:
                _Concepto = ""
        
        if len(_Concepto)>1:
            try:
                Pago_por_Concepto = numero_Pagos_por_concepto[num_2]
                Pago_por_Concepto = Pago_por_Concepto[:-1]
                num_2 = num_2+1
            except:
                Pago_por_Concepto = ""
        else:
            Pago_por_Concepto = ""
            pass
        
        dic_concepto = {
            _Concepto:Pago_por_Concepto
        }
        # print(dic_concepto)
        if len(_Concepto) > 1:
            Array_Conceptos.append(dic_concepto)
        
    return Array_Conceptos
        # print(f"->{Array_Conceptos}")


# PAGOS
column_names=["PDF","RFC", "Entidad", "Tipo", "Fecha Presentacion", "Importe a Pagar", "Linea de Captura", "Num Operacion", "Vigencia", "Tipo de Declaracion", "Fecha de Pago","Concepto de Pago","Pago por Concepto","Numero de Concepto", "Path"]
df_Pagos = pd.DataFrame(exportDataPagos(Archivos_Pagos), columns=column_names)
# print(df_Pagos)
# df_Pagos

# # ACUSE Declaracion
column_names = ["PDF","RFC","Fecha y hora presentacion","Num de Operacion","Periodo de Declaracion","Ejercicio","Total a Pagar","Vigente Hasta","Linea de Captura","Razon Social","Tipo Social","Impuesto a Favor","Concepto de Pago","Pago por Concepto","Numero de Concepto" ,"Path"]
df_Declaracion = pd.DataFrame(exportDataDeclaracion(Archivos_Declaracion), columns=column_names)

# # ACUSE Acuse
column_names = ["PDF","RFC","Fecha y hora presentacion","Num de Operacion","Periodo de Declaracion","Ejercicio","Total a Pagar","Vigente Hasta","Linea de Captura","Razon_Social","Impuesto a Favor","Path"]
df_Acuse_Presentacion = pd.DataFrame(exportDataAcuseRecepcion(Archivos_Acuse_Presentacion), columns=column_names)

# # DIOT
column_names = ["PDF","Usuario", "Archivo Recibido", "tamanio","Fecha_Recepcion", "Hora_Recepcion", "Folio", "Path"]
df_Diot = pd.DataFrame(exportDataDiot(Archivos_Diot), columns=column_names)


# CONTANCIA
column_names=["PDF","RFC", "Razon Social", "CURP", "Primer Apellido", "Segundo Apellido", "Nombre Comercial", "Fecha Operacion", "Estatus", "Regimenes", "Path"]
df_Constancia = pd.DataFrame(exportDataConstancia(Archivos_Constancia), columns=column_names)



# Opinion de cumplimiento
column_names=["PDF","RFC", "Folio", "Path"]
df_Opinion_Cumplimiento =  pd.DataFrame(exportDataOpinionCumplimiento(Archivos_Opinion_Cumplimiento), columns=column_names)

column_names=["Documentos sin clasificar"]
df_no_clasificados =  pd.DataFrame(Archivos_no_clasificados, columns=column_names)
# df_no_clasificados

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

# import os
 
dir = 'F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))
 

df_Pagos.to_excel('F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes/df_Pagos.xlsx', header=True, index=None)
df_Declaracion.to_excel('F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes/df_Declaracion.xlsx', header=True, index=None)
df_Acuse_Presentacion.to_excel('F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes/df_Acuse_Presentacion.xlsx', header=True, index=None)
df_Diot.to_excel('F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes/df_Diot.xlsx', header=True, index=None)
df_Constancia.to_excel('F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes/df_Constancia.xlsx', header=True, index=None)
df_no_clasificados.to_excel('F:\Indicadores\Automatizacion-Cuadras\Script\Dataframes/df_no_Clasificados.xlsx', header=True, index=None)