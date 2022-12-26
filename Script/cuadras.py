import PyPDF2

pdf = open("./Acuse presentacion de Impuestos Noviembre 2022.pdf", "rb")

reader = PyPDF2.PdfReader(pdf)
page = reader.get_page(0)

print(page.extract_text())
