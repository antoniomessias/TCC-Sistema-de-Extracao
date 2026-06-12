# ==========================================
# ============== IMPORTAÇÕES ==============
# ==========================================

# ===== Bibliotecas padrão =====
import os
import re
import time

# ===== Manipulação de dados =====
import pandas as pd

# ===== Leitura de PDF =====
import pdfplumber
from pdf2image import convert_from_path

# ===== OCR =====
import pytesseract

# ===== Utilitários internos =====
from utils.identificador import identificar_banco
from utils.ocr import ocr_pagina, texto_confiavel
from codetiming import Timer

# ===== Processadores por banco =====
from bancos.banco_inter import processar_banco_inter
from bancos.banco_caixa import processar_banco_caixa
from bancos.banco_santander import processar_banco_santander
from bancos.banco_itau import processar_banco_itau
from bancos.banco_santander_empresarial import processar_banco_santander_empresarial
from bancos.banco_nubank import processar_banco_nubank

# ==========================================
# ============== CONFIGURAÇÃO OCR ==========
# ==========================================

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_DIR = r"C:\poppler-25.07.0\Library\bin"

# ==========================================
# ===== PROCESSAMENTO DE PDF POR PÁGINAS ===
# ==========================================

def processar_pdf_por_paginas(caminho_pdf):
    """
    Processa um PDF página por página.
    Detecta o banco automaticamente e aplica o parser adequado.
    """

    todos_dados = []
    paginas_sem_dados = []

    timer_total = Timer(name="pdf_total", logger=None)
    timer_total.start()  # inicia tempo total

    with pdfplumber.open(caminho_pdf) as pdf:
        total_paginas = len(pdf.pages)

        for i, page in enumerate(pdf.pages):

            # ===== Timer por página =====
            timer_pagina = Timer(name="pdf_page", logger=None)
            timer_pagina.start()

            # ===== Extração de texto padrão =====
            texto = page.extract_text() or ""
            origem = "texto"

            # ===== Fallback para OCR =====
            if not texto_confiavel(texto):
                texto = ocr_pagina(page)
                origem = "ocr"

            banco = identificar_banco(texto)

            print(f"📌 Página {i + 1} — Banco: {banco} | Origem: {origem}")

            dados = []

            # ===== Roteamento por banco =====
            if banco == "nubank":
                dados = processar_banco_nubank(page)

            elif banco == "inter":
                dados = processar_banco_inter(page)

            elif banco == "caixa":
                dados = processar_banco_caixa(page)

            elif banco == "santander":
                dados = processar_banco_santander_empresarial(page)
                if not dados:
                    dados = processar_banco_santander(page)

            elif banco == "itau":
                dados = processar_banco_itau(page)

            else:
                print(f"⚠️ Banco não identificado na página {i + 1}")

            # ===== Fallback OCR se parser falhou =====
            if not dados and origem == "texto":

                print(f"🔁 Tentando OCR por falha de extração na página {i + 1}")

                texto_ocr = ocr_pagina(page)
                banco_ocr = identificar_banco(texto_ocr)

                if banco_ocr == "nubank":
                    dados = processar_banco_nubank(page)

                elif banco_ocr == "inter":
                    dados = processar_banco_inter(page)

                elif banco_ocr == "caixa":
                    dados = processar_banco_caixa(page)

                elif banco_ocr == "santander":
                    dados = (
                        processar_banco_santander_empresarial(page)
                        or processar_banco_santander(page)
                    )

                elif banco_ocr == "itau":
                    dados = processar_banco_itau(page)

            # ===== Armazenamento =====
            if dados:
                todos_dados.extend(dados)
            else:
                paginas_sem_dados.append(i + 1)
                print(f"⚠️ Nenhum dado extraído na página {i + 1}")

            # ===== Finaliza timer da página =====
            timer_pagina.stop()
            print(f"⏱️ Tempo gasto na página {i + 1}: {timer_pagina.last:.2f} segundos\n")

    # ===== Finaliza timer total =====
    timer_total.stop()
    print(f"\n🚀 Tempo total do PDF: {timer_total.last:.2f} segundos")

    return {
        "extracted": todos_dados,
        "pages": total_paginas,
        "pages_without_data": paginas_sem_dados
    }

# ==========================================
# ========== PROCESSAMENTO DE IMAGEM =======
# ==========================================

def processar_imagem(caminho_imagem):
    """
    Processa arquivos de imagem utilizando OCR.
    """

    try:
        texto = pytesseract.image_to_string(caminho_imagem, lang="por")
        banco = identificar_banco(texto)

        dados = [{
            "source": os.path.basename(caminho_imagem),
            "banco_detectado": banco,
            "texto_extraido": texto
        }]

        return {
            "extracted": dados,
            "pages": 1,
            "pages_without_data": []
        }

    except Exception as e:
        return {
            "extracted": [],
            "pages": 1,
            "pages_without_data": [1],
            "error": str(e)
        }

# ==========================================
# =========== PROCESSADOR UNIVERSAL ========
# ==========================================

def processar_arquivo(caminho):
    """
    Decide automaticamente qual tipo de processamento aplicar
    com base na extensão do arquivo.
    """

    ext = os.path.splitext(caminho)[1].lower()

    # ===== PDF =====
    if ext == ".pdf":
        return processar_pdf_por_paginas(caminho)

    # ===== Imagens =====
    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".tif"]:
        return processar_imagem(caminho)

    # ===== Tipo não suportado =====
    else:
        return {
            "extracted": [],
            "pages": 0,
            "pages_without_data": [],
            "error": "Tipo de arquivo não suportado"
        }