import re

def limpar_nome(nome):
    if not nome:
        return ""

    lixo = [
        "CPF", "CNPJ", "CHAVE", "AGÊNCIA", "AGENCIA",
        "BANCO", "VALOR", "QUEM RECEBEU",
        "QUEM RECEBE", "DESTINO"
    ]

    nome = nome.upper()

    for palavra in lixo:
        nome = re.sub(rf"\b{palavra}\b.*", "", nome)

    # remove "NOM" ou "NOME" quebrado
    nome = re.sub(r"\bNOM(E)?\b", "", nome)

    # remove "E" isolado (erro OCR)
    nome = re.sub(r"\bE\b", " ", nome)

    # normaliza espaços
    nome = re.sub(r"\s{2,}", " ", nome)

    return nome.strip().title()

def limpar_data(data):
    if not data:
        return ""

    m = re.search(r"\b\d{2}/\d{2}/\d{4}\b", data)
    return m.group(0) if m else ""

def limpar_id(id_bruto):
    if not id_bruto:
        return ""

    m = re.search(r"(E\d{20,}[a-z0-9]{10,12})", id_bruto, re.IGNORECASE)

    return m.group(1) if m else id_bruto

