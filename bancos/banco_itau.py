import re
import utils.limpeza as limpeza

# -------------------------------------------------------------------
# FUNÇÕES DE EXTRAÇÃO
# -------------------------------------------------------------------

def extrair_valor(texto):
    match = re.search(r"valor[: ]+R?\$? ?[\d\.,]+", texto, re.I)
    if match:
        valor = match.group(0).split(":")[-1].strip()
        if not valor.startswith("R$"):
            valor = "R$ " + valor
        return valor
    return None


def extrair_id(texto):
    # PIX -> ID da transação
    match = re.search(
        r"ID da transa[cç][aã]o[: ]+([A-Za-z0-9]+)",
        texto,
        re.I
    )
    if match:
        return match.group(1)

    # Transferência -> Autenticação
    match = re.search(
        r"Autentica[cç][aã]o(?: no comprovante)?[: ]*\n?([A-Za-z0-9]+)",
        texto,
        re.I
    )
    if match:
        return match.group(1)

    return None


def extrair_nome_recebido(texto):
    # PIX
    match = re.search(
        r"nome do recebedor[: ]+([A-Za-zÀ-ÿ\s]+)",
        texto,
        re.I
    )
    if match:
        return match.group(1).strip()

    # Transferência
    match = re.search(
        r"conta creditada.*?Nome[: ]+([A-Za-zÀ-ÿ\s]+)",
        texto,
        re.S | re.I
    )
    return match.group(1).strip() if match else None


def extrair_data(texto):
    # PIX
    match = re.search(
        r"transa[cç][aã]o efetuada em ([^\n]+)",
        texto,
        re.I
    )
    if match:
        return match.group(1).strip()

    # Transferência
    match = re.search(
        r"Transfer[êe]ncia efetuada em ([^\n]+)",
        texto,
        re.I
    )
    if match:
        return match.group(1).strip()

    return None


# -------------------------------------------------------------------
# PROCESSAMENTO PRINCIPAL
# -------------------------------------------------------------------

def processar_banco_itau(page):
    """
    Processa comprovantes do Banco Itaú (PIX e Transferência).
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
    else:
        print("⚠️ Dados incompletos nesta página Itaú")

    return dados