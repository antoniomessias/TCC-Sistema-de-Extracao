from pdf2image import convert_from_path
import pytesseract
import re

POPPLER_DIR = r"C:\poppler-25.07.0\Library\bin"

def ocr_pagina(page):
    caminho_pdf = page.pdf.stream.name
    numero_pagina = page.page_number

    imagens = convert_from_path(
        caminho_pdf,
        poppler_path=POPPLER_DIR,
        first_page=numero_pagina,
        last_page=numero_pagina
    )

    if not imagens:
        return ""

    return pytesseract.image_to_string(imagens[0], lang="por")

def texto_confiavel(texto):
    if not texto or len(texto.strip()) < 50:
        return False

    return bool(re.search(
        r"(pix|transfer|comprovante|valor|r\$|banco|data)",
        texto,
        re.IGNORECASE
    ))

