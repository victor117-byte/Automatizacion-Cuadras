import PyPDF2
import pandas as pd
import numpy as np
import sys, os
import json
import re
import datetime
import locale
from sqlalchemy import create_engine, MetaData, Table, create_engine, inspect
import pandas as pd
import numpy as np
import base64
import pandas as pd
from sqlalchemy import create_engine
import pyodbc
import shutil

def copy_pdf(src, dest, eliminar=False):
    src = rf"{src}"
    try:
        # Copiar el archivo desde src a dest
        shutil.copy2(src, dest)
        print(f"Archivo copiado exitosamente de {src} a {dest}")

    except FileNotFoundError as ferror:
        print(f"Error: El archivo {src} no existe: {ferror}")
    
    except Exception as e:
        print(f"Error al copiar el archivo: {e}")

def convertir_pdf_a_base64(ruta_pdf):
    try:
        # Abrir el archivo PDF en modo binario
        with open(ruta_pdf, "rb") as archivo_pdf:
            # Leer el contenido del archivo
            contenido_pdf = archivo_pdf.read()

            # Codificar el contenido a base64
            pdf_base64 = base64.b64encode(contenido_pdf).decode('utf-8')

            # Devolver el resultado
            return pdf_base64

    except FileNotFoundError:
        print(f"El archivo {ruta_pdf} no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al convertir el archivo a base64: {str(e)}")

def copy_pdf_old_version(src, dest, eliminar=False):
    
    if eliminar == True:
        try:
            print(eliminar)
            shutil.move(src, dest)
        except:
            os.makedirs(os.path.dirname(dest))
            shutil.move(src, dest)
        
    else:
        try:
            shutil.copy(src, dest)
        except:
            os.makedirs(os.path.dirname(dest))
            shutil.copy(src, dest)

def read_file_pdf(Archivos, path_raiz_cliente):
    """Funcion Lee cada archivo para buscar que tipo de tittulo contiene el PDF
    La funcion se encarga de copiar y eliminar archivos ordenando con la siguiente nomenclatura
    
    RFC+Periodo+Tipo_pdf+Num_pdf.pdf

    Args:
        Archivos (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        conexion1 = r"C:\Users\Administrador.WIN-3GR2N6O8MHU\Desktop\Aplicacion_SAT\Dataframes"
        conexion2 = "mssql+pyodbc://sa:Foretagbi_01@BDD\\APLICACIONSAT/AppSat?driver=ODBC+Driver+17+for+SQL+Server"


        pdf = open(Archivos, 'rb')
        # print(Archivos[i])
        reader = PyPDF2.PdfReader(pdf)
        page = reader.pages
        texto = ''    
        for pag in range(len(page)):
            texto += reader._get_page(pag).extract_text()

        txt = re.sub("\n", " ", texto)
        # print(txt)  # Muestra el texto en de todo el PDF
        
        
        #####################################################################################################################
        # Ordenamiento
        # Cada funcion requiere rfc para almacenar el archivo
        
        
        # hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") #Hora actual
        # hora_actual_text = hora_actual.replace(" ", "_").replace(":","-") #Hora actual text
        
        ruta_guardado = "{path_raiz_cliente}{rfc}/{Tipo_pdf}/{nomenclatura}"

        # Declaraciones Mensuales    
        if txt.find("ACUSE DE RECIBO DECLARACIÓN PROVISIONAL O DEFINITIVA DE IMPUESTOS FEDERALES") != -1:
            Tipo_pdf = "DECLARACION"
            # crear ruta
            try:
                rfc = re.search("RFC:.(.*?\s)", txt).group(1)
                rfc = rfc.strip()
            except:
                rfc = "NA"
            try:
                Fecha_y_hora_presentacion = re.search(
                    "Fecha y hora de presentaci.n:(.+?\s.{6})", txt).group(1).strip()
                Fecha_y_hora_presentacion = Fecha_y_hora_presentacion.replace("/", "_").replace(":","-").replace(" ","_")
            except:
                Fecha_y_hora_presentacion = ""
                
            nomenclatura = rfc+"_"+Fecha_y_hora_presentacion+"_"+Tipo_pdf+".pdf"
            ruta_guardado = ruta_guardado.format(path_raiz_cliente=path_raiz_cliente,rfc=rfc, Tipo_pdf=Tipo_pdf+"ES", nomenclatura=nomenclatura )
            
            #################################################################################################################
            # Mover archivo pdf
            copy_pdf(Archivos, ruta_guardado)
            File = {
                "Tipo_pdf": Tipo_pdf,
                "src": Archivos,
                "dest":ruta_guardado}
            data = exportDataDeclaracion(txt, Archivos, Tipo_pdf, conexion1, conexion2)
            
            
        # Constancias de situacion fiscal
        elif txt.find("CONSTANCIA DE SITUACIÓN FISCAL") != -1:
            Tipo_pdf = "CONSTANCIA_DE_SITUACION_FISCAL"
            try:
                fecha_emision = re.search("Emisi.n(.+?\sA)(.+?\s\d{4})", txt).group(2)
                fecha_emision = fecha_emision.strip()
                try:
                    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
                    fecha_emision = fecha_emision.replace("DE", "").replace("  "," ")
                    fecha_objeto = datetime.datetime.strptime(fecha_emision, "%d %B %Y")
                    fecha_formateada = fecha_objeto.strftime("%d/%m/%Y")
                    fecha_formateada = str(fecha_formateada).replace("/", "_")
                except:
                    fecha_formateada = ""
            except:
                fecha_emision = ""
            
            try:
                rfc = re.search("RFC:(.+?\s)", txt).group(1)
                rfc = rfc.strip()
            except:
                rfc = "NA"
                
            nomenclatura = rfc+"_"+fecha_formateada+"_"+Tipo_pdf+".pdf"
            ruta_guardado = ruta_guardado.format(path_raiz_cliente=path_raiz_cliente,rfc=rfc, Tipo_pdf=Tipo_pdf, nomenclatura=nomenclatura )
            
            #################################################################################################################
            # Mover archivo pdf
            copy_pdf(Archivos, ruta_guardado)
            File = {
                "Tipo_pdf": Tipo_pdf,
                "src": Archivos,
                "dest":ruta_guardado}
            data = exportDataConstancia(txt, Archivos, Tipo_pdf, conexion1, conexion2)
            
            
        # Formato de Informacion de contribuyente LH
        elif txt.find("Información del cliente o empresa") != -1:
            Tipo_pdf = "INFORMACION_CONTRIBUYENTE"
            try:
                rfc = re.search("RFC(.+?\s)", txt).group(1)
                rfc = rfc.strip()
            except:
                rfc = "NA"
            nomenclatura = rfc+"_"+Tipo_pdf+".pdf"
            ruta_guardado = ruta_guardado.format(path_raiz_cliente=path_raiz_cliente,rfc=rfc, Tipo_pdf=Tipo_pdf, nomenclatura=nomenclatura )
            
            #################################################################################################################
            # Mover archivo pdf
            copy_pdf(Archivos, ruta_guardado)
            File = {
                "Tipo_pdf": Tipo_pdf,
                "src": Archivos,
                "dest":ruta_guardado}
            
            
            # df_Informacion_Controbuyente =  pd.DataFrame(exportData_Info_Contribuyente(txt, ruta_guardado), columns=column_names)
            data = exportData_Info_Contribuyente(txt, ruta_guardado, Tipo_pdf, conexion1, conexion2)
            
                      
        # Formato de Pagos
        elif txt.find("INFORMACIÓN REGISTRADA DE PAGOS DE CONTRIBUCIONES FEDERALES") != -1:
            Tipo_pdf = "PAGO"
            try:
                rfc = re.search("RFC:(.+?\s)", txt).group(1)
                rfc = rfc.strip()
            except:
                rfc = "NA"
            try:
                fecha_pago = re.search("Fecha del pago:(.+?\s)",txt).group(1)
                fecha_pago = fecha_pago.strip().replace("/", "_")
            except:
                fecha_pago = ""
                
            nomenclatura = rfc+"_"+fecha_pago+"_"+Tipo_pdf+".pdf"
            ruta_guardado = ruta_guardado.format(path_raiz_cliente=path_raiz_cliente,rfc=rfc, Tipo_pdf=Tipo_pdf+"S", nomenclatura=nomenclatura )
            
            #################################################################################################################
            # Mover archivo pdf
            copy_pdf(Archivos, ruta_guardado)
            File = {
                "Tipo_pdf": Tipo_pdf,
                "src": Archivos,
                "dest":ruta_guardado}
            
            data = exportDataPagos(txt, Archivos, Tipo_pdf, conexion1, conexion2)
            
            
        # Formato DIOT
        elif txt.find("Acuse de Recibo de Declaración Informativa de Operaciones con Terceros") != -1:
            Tipo_pdf = "DIOT"
            
            try:
                rfc = re.search("Usuario:.(.+?\s)", txt)[0]
                rfc = re.split(':', rfc)[1]
                rfc = rfc.strip()
            except:
                rfc = "NA"
            try:
                Fecha_Recepcion = re.search("Fecha de Recepci.n:.(.+?\s)", txt)[0]
                Fecha_Recepcion = re.split(':', Fecha_Recepcion)[1]
                Fecha_Recepcion = Fecha_Recepcion.strip().replace("/", "_")
            except:
                Fecha_Recepcion = ""
            # print(fecha_pago)
            nomenclatura = rfc+"_"+Fecha_Recepcion+"_"+Tipo_pdf+".pdf"
            ruta_guardado = ruta_guardado.format(path_raiz_cliente=path_raiz_cliente,rfc=rfc, Tipo_pdf=Tipo_pdf, nomenclatura=nomenclatura )
            
            #################################################################################################################
            # Mover archivo pdf
            copy_pdf(Archivos, ruta_guardado)
            File = {
                "Tipo_pdf": Tipo_pdf,
                "src": Archivos,
                "dest":ruta_guardado}
            
            data = exportDataDiot(txt, Archivos, Tipo_pdf, conexion1, conexion2)
            
        
        # Formato OPINION DE CUMPLIMIENTO
        elif txt.find("Opinión del cumplimiento de obligaciones fiscales") != -1:
            Tipo_pdf = "OPINION_DE_CUMPLIMIENTO"
            try:
                rfc = re.search("Folio.(.+?\s)(.+?\s)Respuesta", txt).group(1)
                rfc = rfc.strip()
                if rfc =="Clave":
                    rfc = re.search("R.F.C.(.+?\s)(.+?\s)Nombre", txt).group(2)
                    rfc = rfc.strip()
                else:
                    pass
            except:
                rfc = "NA"
            nomenclatura = rfc+"_"+Tipo_pdf+".pdf"
            ruta_guardado = ruta_guardado.format(path_raiz_cliente=path_raiz_cliente,rfc=rfc, Tipo_pdf=Tipo_pdf, nomenclatura=nomenclatura )
            
            #################################################################################################################
            # Mover archivo pdf
            copy_pdf(Archivos, ruta_guardado)
            File = {
                "Tipo_pdf": Tipo_pdf,
                "src": Archivos,
                "dest":ruta_guardado}
            data = exportDataOpinionCumplimiento(txt, Archivos, Tipo_pdf, conexion1, conexion2)
            
        # # No identificado
        else:
            # print("No identificados")
            Tipo_pdf = "No identificado"
            
            File = {
                "Tipo_pdf": Tipo_pdf,
                "src": Archivos,
                "dest":""}
            
        # print(File)
        return File
    except Exception as e:
        print("Error read_file_pdf: ", e)
        pass

# Funcion que obtiene los archivos con su ruta y se encarga de clasificarlos
def Clasificador_Archivos(rutas, path_raiz_cliente,  fecha_limite=None):
    
    if fecha_limite is None:
        # Si no se proporciona una fecha límite, se usa la fecha actual
        fecha_limite = datetime.now()
    else:
        # Si se proporciona una fecha límite, se convierte a formato datetime
        fecha_limite = datetime.datetime.strptime(fecha_limite, "%Y-%m-%d")
    
    array_Info_Contri = []
    array_Declaraciones = []
    array_Constancia = []
    array_Diot = []
    array_Pagos = []
    array_Seguro = []
    array_Opinion_Cumplimiento = []
    array_no_identificado = []
    array_docs = []
    
    count_files = 0
    
    for root in rutas:
        for path, subdirs, files in os.walk(root):
            for name in files:
                file_path = os.path.join(path, name)
                fecha_creacion = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                if fecha_creacion >= fecha_limite and name.endswith(".pdf"):
                    Carpeta_ejercicio = fecha_creacion.year
                    dic_document = read_file_pdf(file_path, path_raiz_cliente + str(Carpeta_ejercicio)+"/")
                    # print("-->", dic_document)
                    array_docs.append(dic_document)
                
    # Resultados
    print("Archivos Ordenados:", len(array_docs))

    
    for i in array_docs:
        array = list(i.values())
        """definicion
        array = ["identificador de documento", "path prigen/src", "path despues de ordenar"]
        array = [               0            ,        1         ,            2             ]
        """
        if array[0]=="No identificado":
            array_no_identificado.append(array[1])
        elif array[0]=="DECLARACION":
            array_Declaraciones.append(array[2])
        elif array[0]=="PAGO":
            array_Pagos.append(array[2])
        elif array[0]=="CONSTANCIA_DE_SITUACION_FISCAL":
            array_Constancia.append(array[2])
        elif array[0]=="DIOT":
            array_Diot.append(array[2])
        elif array[0]=="OPINION_DE_CUMPLIMIENTO":
            array_Opinion_Cumplimiento.append(array[2])
        elif array[0]=="INFORMACION_CONTRIBUYENTE":
            array_Info_Contri.append(array[2])
        else:
            try:
                array_no_identificado.append(array[1])
            except:
                pass
            pass
        # print(array)
    print("0- Archivos no identificado:", len(array_no_identificado))
    print("1- Archivos de Declaraciones:", len(array_Declaraciones))
    print("2- Archivos de Pagos:", len(array_Pagos))
    print("3- Archivos de Constancia:", len(array_Constancia))
    print("4- Archivos Diot:", len(array_Diot))
    print("5- Archivos Opinion de Cumplimiento:", len(array_Opinion_Cumplimiento))
    print("6- Archivos Informacion Contribuyente:", len(array_Info_Contri))
                    
    return array_no_identificado, array_Declaraciones, array_Pagos, array_Constancia, array_Diot, array_Opinion_Cumplimiento, array_Info_Contri

def exportDataDeclaracion(pdf_txt, path_pdf, Tipo_pdf, conexion1, conexion2):
    try:
        pdf_base64 = ProcessPDF(path_pdf, Tipo_pdf)
        txt = pdf_txt
        # Text Mining
        # DATOS GENERALES

        # rfc
        rfc = re.search("RFC:.(.*?\s)", txt).group(1)
        rfc = rfc.strip()
        # Fecha
        try:
            Fecha_y_hora_presentacion = re.search(
                "Fecha y hora de presentaci.n:.{11}", txt)[0]
            Fecha_y_hora_presentacion = re.split(':', Fecha_y_hora_presentacion)[1]
            Fecha_y_hora_presentacion = Fecha_y_hora_presentacion.strip()
        except:
            Fecha_y_hora_presentacion = ""

        # numero de operacion
        try:
            Num_de_Operacion = re.search("N.mero de operaci.n:(\d*?\s)", txt).group(1)
            Num_de_Operacion = Num_de_Operacion.strip()
        except:
            try:
                Num_de_Operacion = re.search("N.mero de operaci.n:(.+?\s)", txt).group(1)
                Num_de_Operacion = Num_de_Operacion.strip()
            except:
                Num_de_Operacion = ""
        # periodo de la declaracion
        try:
            Periodo_de_declaracion = re.search(
                "Per.odo de la declaraci.n:(.+?\s)", txt).group(1)
            Periodo_de_declaracion = Periodo_de_declaracion.strip()
        except:
            Periodo_de_declaracion = ""
        # Ejercicio
        try:
            Ejercicio = re.search("Ejercicio:(.+?\s)", txt).group(1)
            Ejercicio = Ejercicio.strip()
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
            try:
                RazonSocial_base = re.search("Hoja.\d.de\s\d(.*?)Tipo", txt).group(1)
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
        except:
            total_a_pagar = ""
        
        try:
            Vigente_hasta = re.search("Vigente hasta:(.+?\s)", txt).group(1)
            Vigente_hasta = Vigente_hasta.strip()
            
        except:
            try:
                Vigente_hasta = re.search("Vencimiento Obligación:(.+?\s)", txt).group(1)
                Vigente_hasta = Vigente_hasta.strip()
            except:    
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
            
            column_names = ["Tipo_pdf","RFC","Fecha y hora presentacion","Num de Operacion","Periodo de Declaracion","Ejercicio","Total a Pagar","Vigente Hasta","Linea de Captura","Razon Social","Tipo Social","Impuesto a Favor","Concepto de Pago","Pago por Concepto","Numero de Concepto" ,"Path"]
            valor=[
                Tipo_pdf,
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
                path_pdf
                ]
            df = pd.DataFrame([valor], columns=column_names)
            # array_docs.append(data_fila)
            df = pd.merge(df, pdf_base64, how='outer')
            try:
                almacenar_dataframe_en_excel(df, Tipo_pdf, conexion1)
            except Exception as e:
                print("Error al almacenar en excel: ", e)
            try:
                almacenar_dataframe_en_sqlserver(df, Tipo_pdf, conexion2)
            except Exception as e:
                print("Error al almacernar el db: ", e)
        
            return df
    except Exception as e:
        print("Error en funcion exportDataDeclaracion: ", e)

def exportDataAcuseRecepcion(pdf_txt, path_pdf, Tipo_pdf, conexion1, conexion2):
    try:
        pdf_base64 = ProcessPDF(path_pdf, Tipo_pdf)
        txt = pdf_txt
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
        
        column_names = ["Tipo_pdf","RFC","Fecha y hora presentacion","Num de Operacion","Periodo de Declaracion","Ejercicio","Total a Pagar","Vigente Hasta","Linea de Captura","Razon_Social","Impuesto a Favor","Path"]
        valor=[
            Tipo_pdf,
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
            path_pdf
            ]
        df = pd.DataFrame([valor], columns=column_names)
        df = pd.merge(df, pdf_base64, how='outer')
        try:
            almacenar_dataframe_en_excel(df, Tipo_pdf, conexion1)
        except Exception as e:
            print("Error al almacenar en excel: ", e)
        try:
            almacenar_dataframe_en_sqlserver(df, Tipo_pdf, conexion2)
        except Exception as e:
            print("Error al almacernar el db: ", e)
        return df
    except Exception as e:
        print("Error en funcion exportDataAcuseRecepcion: ", e)
        
def exportDataDiot(pdf_txt, path_pdf, Tipo_pdf, conexion1, conexion2):
    try:
        pdf_base64 = ProcessPDF(path_pdf, Tipo_pdf)
        txt = pdf_txt
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

        column_names = ["Tipo_pdf","Usuario", "Archivo Recibido", "tamanio","Fecha_Recepcion", "Hora_Recepcion", "Folio", "Path"]

        valor=[
            Tipo_pdf,
            usuario,
            Archivo_Recibido,
            tamanio,
            Fecha_Recepcion,
            Hora_Recepcion,
            Folio,
            path_pdf
        ]
        df = pd.DataFrame(valor, columns=column_names)
        df = pd.merge(df, pdf_base64, how='outer')
        try:
            almacenar_dataframe_en_excel(df, Tipo_pdf, conexion1)
        except Exception as e:
            print("Error al almacenar en excel: ", e)
        try:
            almacenar_dataframe_en_sqlserver(df, Tipo_pdf, conexion2)
        except Exception as e:
            print("Error al almacernar el db: ", e)
        return df
    except Exception as e:
        print("Error en funcion exportDataDiot: ", e)

def exportDataConstancia(pdf_txt, path_pdf, Tipo_pdf, conexion1, conexion2):
    try:
        pdf_base64 = ProcessPDF(path_pdf, Tipo_pdf)
        txt = pdf_txt
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

        column_names=["Tipo_pdf","RFC", "Razon Social", "CURP", "Primer Apellido", "Segundo Apellido", "Nombre Comercial", "Fecha Operacion", "Estatus", "Regimenes", "Path"]

        valor=[
            Tipo_pdf,
            rfc,
            Razon_Social_Nombre,
            Regimen_Nombre,
            Primer_Apellido,
            Segundo_Apellido,
            Nombre_Comercial,
            Fecha_Operaciones,
            Estatus,
            Regimenes,
            path_pdf
        ]
        df = pd.DataFrame([valor], columns=column_names)
        df = pd.merge(df, pdf_base64, how='outer')
        try:
            almacenar_dataframe_en_excel(df, Tipo_pdf, conexion1)
        except Exception as e:
            print("Error al almacenar en excel: ", e)
        try:
            almacenar_dataframe_en_sqlserver(df, Tipo_pdf, conexion2)
        except Exception as e:
            print("Error al almacernar el db: ", e)
        return df
    except Exception as e:
        print("Error en funcion exportDataConstancia: ", e)
        
def exportDataOpinionCumplimiento(pdf_txt, path_pdf, Tipo_pdf, conexion1, conexion2):
    try:
        pdf_base64 = ProcessPDF(path_pdf, Tipo_pdf)
        txt = pdf_txt
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
            
        column_names=["Tipo_pdf","RFC", "Folio", "Path"]
        valor=[
            Tipo_pdf,
            RFC,
            folio,
            path_pdf
        ]
        df = pd.DataFrame([valor], columns=column_names)
        df = pd.merge(df, pdf_base64, how='outer')
        try:
            almacenar_dataframe_en_excel(df, Tipo_pdf, conexion1)
        except Exception as e:
            print("Error al almacenar en excel: ", e)
        try:
            almacenar_dataframe_en_sqlserver(df, Tipo_pdf, conexion2)
        except Exception as e:
            print("Error al almacernar el db: ", e)
        return df
    except Exception as e:
        print("Error en funcion exportDataOpinionCumplimiento: ", e)
        
def exportDataPagos(pdf_txt, path_pdf, Tipo_pdf, conexion1, conexion2):
    try:
        pdf_base64 = ProcessPDF(path_pdf, Tipo_pdf)
        txt = pdf_txt

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
            column_names=["Tipo_pdf","RFC", "Entidad", "Tipo", "Fecha Presentacion", "Importe a Pagar", "Linea de Captura", "Num Operacion", "Vigencia", "Tipo de Declaracion", "Fecha de Pago","Concepto de Pago","Pago por Concepto","Numero de Concepto", "Path"]
            valor=[
                Tipo_pdf,
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
                path_pdf
                ]
            df = pd.DataFrame([valor], columns=column_names)
            df = pd.merge(df, pdf_base64, how='outer')
            try:
                almacenar_dataframe_en_excel(df, Tipo_pdf, conexion1)
            except Exception as e:
                print("Error al almacenar en excel: ", e)
            try:
                almacenar_dataframe_en_sqlserver(df, Tipo_pdf, conexion2)
            except Exception as e:
                print("Error al almacernar el db: ", e)
            return df
    except Exception as e:
        print("Error en funcion exportDataPagos: ", e)

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

def exportData_Info_Contribuyente(pdf_txt, path_pdf, Tipo_pdf, conexion1, conexion2):
    try:
        pdf_base64 = ProcessPDF(path_pdf, Tipo_pdf)
        # Text Mining
        # DATOS GENERALES
        txt = pdf_txt

        # data_fila = [rfc, Fecha_y_hora_presentacion, Num_de_Operacion, Periodo_de_declaracion, Ejercicio,  total_a_pagar, Vigente_hasta, Linea_de_Captura, Archivos[i]]
        # print(txt)
        try:
            rfc = re.search("RFC.(.*?\s)", txt).group(1)
            rfc = rfc.strip()
        except:
            rfc = ""
        try:
            nombre = re.search("Nombre completo cliente  o empresa..(.*?\s)RFC", txt).group(1)
            nombre = nombre.strip()
        except:
            try:
                nombre = re.search("Nombre completo  cliente o empresa..(.*?\s)RFC", txt).group(1)
                nombre = nombre.strip()
            except:
                nombre = ""
        try:
            contraseña = re.search("Contraseña portal del  SAT.(.*?\s)", txt).group(1)
            contraseña = contraseña.strip()
        except:
            contraseña = ""
        try:
            estado = re.search("Estado..(.*?\s) Cuenta", txt).group(1)
            estado = estado.strip()
        except:
            estado = ""
        try:
            calle_numero = re.search("Calle y numero..(.*?\s) Código", txt).group(1)
            calle_numero = calle_numero.strip()
        except:
            calle_numero = ""
        try:
            usuario = re.search("USUARIO REPONSABLE..(.*?\s)", txt).group(1)
            usuario = usuario.strip()
        except:
            usuario = ""
        try:
            contraseña_firma = re.search("Contraseña firma..(.*?\s)Cuenta", txt).group(1)
            contraseña_firma = contraseña_firma.strip()
        except:
            try: 
                contraseña_firma = re.search("Contraseña ﬁrma(.*?\s)Cuenta", txt).group(1)
                contraseña_firma = contraseña_firma.strip()
                contraseña_firma = contraseña_firma.replace(" ", "")
            except:
                contraseña_firma = ""
        try:
            contraseña_sipare = re.search("Contraseña..SIPARE..(.*?\s)Contacto", txt).group(1)
            contraseña_sipare = contraseña_sipare.strip()
        except:
            contraseña_sipare = ""
        try:
            cuenta_sipare = re.search("Cuenta SIPARE..(.*?\s)Contraseña", txt).group(1)
            cuenta_sipare = cuenta_sipare.strip()
        except:
            cuenta_sipare = ""
        
        column_names=["Tipo_pdf","RFC", "Nombre","Usuario","Calle Numero", "Estado", "Contraseña","Contraseña Firma", "Contraseña SIPARE", "Cuenta SIPARE", "Path"]
            
        valor=[
            Tipo_pdf,
            rfc,
            nombre,
            usuario,
            calle_numero,
            estado,
            contraseña,
            contraseña_firma,
            contraseña_sipare,
            cuenta_sipare,
            path_pdf
            ]
        df = pd.DataFrame([valor], columns=column_names)
        df = pd.merge(df, pdf_base64, how='outer')
        try:
            almacenar_dataframe_en_excel(df, Tipo_pdf, conexion1)
        except Exception as e:
            print("Error al almacenar en excel: ", e)
        try:
            almacenar_dataframe_en_sqlserver(df, Tipo_pdf, conexion2)
        except Exception as e:
            print("Error al almacernar el db: ", e)
        return df
    except Exception as e:
        print("Error en funcion exportData_Info_Contribuyente: ", e)
        


def almacenar_dataframe_en_excel(dataframe, nombre, path):
    """
    Almacena un DataFrame en un archivo Excel. Si el archivo no existe, lo crea.

    Parameters:
    - dataframe: El DataFrame que se almacenará en el archivo Excel.
    - nombre: Nombre base del archivo Excel (sin extensión).
    - path: Ruta del directorio donde se almacenará el archivo.

    Returns:
    - Ruta completa del archivo Excel creado o actualizado.
    """
    # Combinar nombre y extensión del archivo
    nombre_archivo = f"{nombre}.xlsx"
    
    # Crear la ruta completa del archivo
    ruta_completa = os.path.join(path, nombre_archivo)

    # Verificar si el archivo ya existe
    if os.path.exists(ruta_completa):
        # Si el archivo existe, cargar el contenido existente y agregar las filas del DataFrame
        existente_df = pd.read_excel(ruta_completa)
        nuevo_df = pd.concat([existente_df, dataframe], ignore_index=True)
    else:
        # Si el archivo no existe, usar el DataFrame original
        nuevo_df = dataframe

    # Guardar el DataFrame en el archivo Excel
    nuevo_df.to_excel(ruta_completa, index=False)

    print(f"DataFrame almacenado en '{ruta_completa}'.")


def almacenar_dataframe_en_sqlserver(dataframe, tabla, conexion_str):
    """
    Almacena un DataFrame en una tabla de SQL Server.

    Parameters:
    - dataframe: El DataFrame que se almacenará en la tabla.
    - tabla: Nombre de la tabla en la base de datos.
    - conexion_str: Cadena de conexión a la base de datos SQL Server.
    """
    # Crear una conexión a la base de datos
    engine = create_engine(conexion_str)

    # Utilizar el objeto 'inspector' para verificar si la tabla existe
    inspector = inspect(engine)
    if tabla in inspector.get_table_names():
        # Si la tabla existe, agregar el DataFrame a la tabla
        dataframe.to_sql(name=tabla, con=engine, index=False, if_exists='append', method='multi', chunksize=1000)
        print(f"DataFrame agregado a la tabla '{tabla}'.")
    else:
        # Si la tabla no existe, crear la tabla y almacenar el DataFrame
        dataframe.to_sql(name=tabla, con=engine, index=False, if_exists='replace')
        print(f"Tabla '{tabla}' creada y DataFrame almacenado.")
        
def ProcessPDF(WDir, FName):  
    with open(WDir, "rb") as Tempfile: # Abrir el archivo PDF
        my_string = base64.b64encode(Tempfile.read()) # Obtener el contenido del archivo PDF en formato base64
        my_string = my_string.decode('ascii') # Eliminar la referencia binaria del código base64

    Data_ = {} # Crear un diccionario para los encabezados del DataFrame
    field_names = ['Tipo_pdf']
    [field_names.append('B' + str(i)) for i in range(3)] # Ajustar para tener 31 columnas

    # Crear un diccionario con los datos
    Data_['Tipo_pdf'] = FName
    for j in range(31):  # Iterar sobre las 31 columnas
        start = j * 32000
        end = (j + 1) * 32000
        if end > len(my_string):  # Ajustar si la longitud de la cadena es menor
            end = len(my_string)
        Data_['B' + str(j)] = my_string[start:end]

    # Crear el DataFrame a partir del diccionario
    df = pd.DataFrame(Data_, index=[0])

    return df
