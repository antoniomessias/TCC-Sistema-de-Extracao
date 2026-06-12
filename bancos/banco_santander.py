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

def processar_banco_santander(page):

    dados = []
    texto_bruto = page.extract_text()

    if not texto_bruto:
        return dados

    texto = texto_bruto.replace("\r", " ").strip()
    texto_lower = texto.lower()

    # 🔹 Variáveis base
    id_transacao = None
    nome = None
    data = None
    valor = None

    # ===============================================================
    # LAYOUT 1 — Antigo
    # ===============================================================
    if "favorecido" in texto_lower and "autenticação bancária" in texto_lower:

        m_nome = re.search(r"favorecido[: ]+([A-Za-zÀ-ÿ\s]+)", texto, re.I)
        m_valor = re.search(r"valor[: ]+([\d.,]+)", texto, re.I)
        m_data = re.search(
            r"data da transa[cç][aã]o[: ]+(\d{2}/\d{2}/\d{4})",
            texto,
            re.I
        )
        m_id = re.search(
            r"autentica[cç][aã]o banc[aá]ria[: ]+([A-Za-z0-9]+)",
            texto,
            re.I
        )

        if m_nome:
            nome = m_nome.group(1).strip()

        if m_valor:
            valor = formatar_valor(m_valor.group(1).strip())

        if m_data:
            data = m_data.group(1).strip()

        if m_id:
            id_transacao = m_id.group(1).strip()

    # ===============================================================
    # LAYOUT 2 — PIX / moderno
    # ===============================================================
    else:

        m_valor = re.search(
            r"valor\s*[\n ]+r?\$?\s*([\d.,]+)",
            texto_lower,
            re.I
        )
        if m_valor:
            valor = formatar_valor(m_valor.group(1).strip())

        m_nome = re.search(
            r"para\s*[\n ]+([A-ZÀ-Ÿ\s]+)",
            texto,
            re.I
        )
        if m_nome:
            nome = m_nome.group(1).strip()

        m_id = re.search(
            r"id/?transa[cç][aã]o\s*[\n ]+([A-Za-z0-9]+)",
            texto_lower,
            re.I
        )
        if m_id:
            id_transacao = m_id.group(1).strip()

        m_data = re.search(
            r"data/?hora da transa[cç][aã]o\s*[\n -]+(\d{2}/\d{2}/\d{4})",
            texto_lower,
            re.I
        )
        if m_data:
            data = m_data.group(1).strip()

    # ===============================================================
    # ✅ VALIDAÇÃO FINAL (como você pediu)
    # ===============================================================
    if all([valor, id_transacao, nome, data]):
        dados.append({
            "Nome Recebido": limpeza.limpar_nome(nome),
            "Data": limpeza.limpar_data(data),
            "Id": id_transacao,
            "Valor": valor
        })

    return dados