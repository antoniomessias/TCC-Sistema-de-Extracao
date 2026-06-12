import re
import logging
import warnings
import utils.limpeza as limpeza

# -------------------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------------------

warnings.filterwarnings("ignore", message="Could get FontBBox")
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

# -------------------------------------------------------------------
# FUNÇÕES DE EXTRAÇÃO
# -------------------------------------------------------------------

def extrair_valor(texto):
    match = re.search(r"R\$ ?[\d\.,]+", texto)
    return match.group(0) if match else None


def extrair_id(texto):
    match = re.search(r"ID da transaç[aã]o\s*\n?([A-Za-z0-9]+)", texto)
    return match.group(1) if match else None


def extrair_nome_recebido(texto):
    match = re.search(
        r"Quem recebeu.*?Nome\s+([A-Za-zÀ-ÿ\s]+)",
        texto,
        re.S
    )
    return match.group(1).strip() if match else None


def extrair_data(texto):
    match = re.search(
        r"Data (?:da|do) (?:transa[cç][aã]o|pagamento)[^\n]*?(\d{2}/\d{2}/\d{4})",
        texto,
        re.IGNORECASE
    )
    return match.group(1) if match else None


# -------------------------------------------------------------------
# PROCESSAMENTO PRINCIPAL
# -------------------------------------------------------------------

def processar_banco_inter(page):
    """
    Processa comprovantes do Banco Inter.
    Campos obrigatórios:
    - Id
    - Nome Recebido
    - Data
    - Valor
    """

    dados = []
    texto = page.extract_text()

    if not texto:
        return dados

    valor = extrair_valor(texto)
    id_transacao = extrair_id(texto)
    nome = extrair_nome_recebido(texto)
    data = extrair_data(texto)

    if all([valor, id_transacao, nome, data]):
        dados.append({
            "Nome Recebido": limpeza.limpar_nome(nome),
            "Data": limpeza.limpar_data(data),
            "Id": id_transacao,
            "Valor": valor
        })

    return dados