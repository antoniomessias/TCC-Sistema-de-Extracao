import re
from pdf2image import convert_from_path
import pytesseract
import utils.limpeza as limpeza
import utils.ocr as ocr

# -------------------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_DIR = r"C:\poppler-25.07.0\Library\bin"

MAPA_MESES = {
    "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04",
    "MAI": "05", "JUN": "06", "JUL": "07", "AGO": "08",
    "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
}

# -------------------------------------------------------------------
# UTILITÁRIOS
# -------------------------------------------------------------------

def formatar_data_pt(data_str):
    if not data_str:
        return ""

    partes = data_str.strip().split()
    if len(partes) >= 3:
        dia, mes, ano = partes[:3]
        mes_num = MAPA_MESES.get(mes.upper())
        if mes_num:
            return f"{dia.zfill(2)}/{mes_num}/{ano}"

    return ""

def extrair_nome(linhas):

    # =========================================================
    # 🔥 1. TENTATIVA PRINCIPAL → BLOCO DESTINO
    # =========================================================
    bloco = []
    capturando = False

    for linha in linhas:
        l = linha.strip()

        if "destino" in l.lower():
            capturando = True
            continue

        if "origem" in l.lower() and capturando:
            break

        if capturando:
            bloco.append(l)

    nome_partes = []

    for l in bloco:
        if (
            not l
            or re.search(r"(cpf|cnpj|institui|banco|agencia|conta|pix|valor|tipo|chave)", l, re.IGNORECASE)
        ):
            continue

        if "nome" in l.lower():
            partes = re.split(r"nome", l, flags=re.IGNORECASE)
            if len(partes) > 1:
                nome_extraido = partes[1].strip()
                if nome_extraido and not re.search(r"\d", nome_extraido):
                    nome_partes.append(nome_extraido)
            continue

        if not re.search(r"\d", l):
            nome_partes.append(l)

        if len(nome_partes) >= 3:
            break

    if nome_partes:
        return " ".join(nome_partes).strip()

    # =========================================================
    # 🔥 2. FALLBACK → BUSCA POR "NOME" (GENÉRICO)
    # =========================================================
    for i, linha in enumerate(linhas):
        if "nome" in linha.lower():

            nome_partes = []

            for j in range(i - 2, i + 4):
                if j < 0 or j >= len(linhas):
                    continue

                l = linhas[j].strip()

                if (
                    not l
                    or re.search(r"(cpf|cnpj|institui|banco|agencia|conta|pix|valor)", l, re.IGNORECASE)
                ):
                    continue

                if "nome" in l.lower():
                    partes = re.split(r"nome", l, flags=re.IGNORECASE)
                    if len(partes) > 1:
                        nome_extraido = partes[1].strip()
                        if nome_extraido and not re.search(r"\d", nome_extraido):
                            nome_partes.append(nome_extraido)
                    continue

                if not re.search(r"\d", l):
                    nome_partes.append(l)

            if nome_partes:
                return " ".join(nome_partes).strip()

    return None

def extrair_valor(texto):
    m = re.search(r"R\$ ?[\d\.,]+", texto)
    return m.group(0) if m else None


# 🔥 ID COMPLETO (PEGA O ÚLTIMO, IGNORA O QUEBRADO)
def extrair_id(texto):
    texto_limpo = texto.replace(" ", "").replace("\n", "")
    ids = re.findall(r"E\d{20,}[a-zA-Z0-9]+", texto_limpo)
    return ids[-1] if ids else None


def extrair_data(texto):

    texto = texto.upper()

    # 🔥 1. formato com hora
    m = re.search(
        r"(\d{1,2})\s+(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+(\d{4})\s*[-–]\s*\d{2}:\d{2}:\d{2}",
        texto
    )

    if m:
        dia, mes, ano = m.groups()
        return f"{dia.zfill(2)}/{MAPA_MESES[mes]}/{ano}"

    # 🔥 2. fallback sem hora
    m = re.search(
        r"(\d{1,2})\s+(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+(\d{4})",
        texto
    )

    if m:
        dia, mes, ano = m.groups()
        return f"{dia.zfill(2)}/{MAPA_MESES[mes]}/{ano}"

    return None


# -------------------------------------------------------------------
# PROCESSAMENTO PRINCIPAL
# -------------------------------------------------------------------

def processar_banco_nubank(page):
    """
    Processa comprovantes do Nubank (via OCR).
    """

    dados = []

    texto = ocr.ocr_pagina(page)

    if not texto or not texto.strip():
        return dados

    linhas = texto.split("\n")
    nome = extrair_nome(linhas)

    valor = extrair_valor(texto)
    data = extrair_data(texto)
    id_transacao = extrair_id(texto)

    if all([valor, id_transacao, nome, data]):
        dados.append({
            "Nome Recebido": limpeza.limpar_nome(nome),
            "Data": limpeza.limpar_data(data),
            "Id": limpeza.limpar_id(id_transacao),
            "Valor": valor
        })

    return dados