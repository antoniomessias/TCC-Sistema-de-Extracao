import re
import utils.limpeza as limpeza

# -------------------------------------------------------------------
# UTILITÁRIO
# -------------------------------------------------------------------

def formatar_valor(valor_raw):
    """
    Garante que o valor esteja no formato: R$ XX,XX
    """
    if not valor_raw:
        return None

    v = str(valor_raw).strip()
    v = re.sub(r"[Rr]\$\s*", "", v)
    v = v.replace(".", ",")
    v = re.sub(r"[^\d,]", "", v)

    if v.isdigit() and len(v) > 2:
        v = v[:-2] + "," + v[-2:]
    elif v.isdigit() and len(v) <= 2:
        v = "0," + v.zfill(2)

    return f"R$ {v}"


# -------------------------------------------------------------------
# PROCESSAMENTO PRINCIPAL
# -------------------------------------------------------------------

def processar_banco_santander_empresarial(page):

    dados = []
    texto = page.extract_text()

    if not texto:
        return dados

    # 🔹 Variáveis base
    id_transacao = None
    nome = None
    data = None
    valor = None

    # ---------------------------------------------------------------
    # VALOR
    # ---------------------------------------------------------------
    m_valor = re.search(
        r"valor\s*\n?\s*r?\$?\s*([\d.,]+)",
        texto,
        re.I
    )
    if m_valor:
        valor = formatar_valor(m_valor.group(1).strip())

    # ---------------------------------------------------------------
    # NOME
    # ---------------------------------------------------------------
    m_nome = re.search(
        r"Para\s+Chave\s+CPF/CNPJ\s*\n?([A-ZÀ-Ÿ\s]+)",
        texto,
        re.I
    )
    if m_nome:
        nome_extraido = m_nome.group(1).strip()

        # Remove CPF do nome
        nome_extraido = re.sub(
            r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
            "",
            nome_extraido
        ).strip()

        nome = nome_extraido

    # ---------------------------------------------------------------
    # ID + DATA (mesma linha)
    # ---------------------------------------------------------------
    m_id_data = re.search(
        r"ID/?Transa[cç][aã]o.*?\n?([A-Z0-9]+)\s+(\d{2}/\d{2}/\d{4})",
        texto,
        re.I
    )
    if m_id_data:
        id_transacao = m_id_data.group(1).strip()
        data = m_id_data.group(2).strip()

    # ---------------------------------------------------------------
    # FALLBACKS
    # ---------------------------------------------------------------
    if not id_transacao:
        m_id = re.search(
            r"ID/?Transa[cç][aã]o\s*\n?\s*([A-Za-z0-9]+)",
            texto,
            re.I
        )
        if m_id:
            id_transacao = m_id.group(1).strip()

    if not data:
        m_data = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
        if m_data:
            data = m_data.group(1).strip()

    # ---------------------------------------------------------------
    # ✅ VALIDAÇÃO FINAL (PADRÃO NOVO)
    # ---------------------------------------------------------------
    if all([valor, id_transacao, nome, data]):
        dados.append({
            "Nome Recebido": limpeza.limpar_nome(nome),
            "Data": limpeza.limpar_data(data),
            "Id": id_transacao,
            "Valor": valor
        })

    return dados