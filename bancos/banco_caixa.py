# ==========================================
# ============== IMPORTAÇÕES ==============
# ==========================================

import re
import utils.limpeza as limpeza

# ==========================================
# ========== FUNÇÕES AUXILIARES ============
# ==========================================

def extrair_valor(texto):
    """
    Extrai o valor monetário no formato R$ 0.000,00
    """
    match = re.search(r"R\$ ?[\d\.,]+", texto)
    return match.group(0) if match else None

def extrair_id(texto):
    """
    Extrai ID da transação.
    Suporta:
    - PIX
    - TEV (Código da operação como fallback)
    """

    # ===== PIX =====
    match = re.search(r"ID da transaç[aã]o[: ]+([A-Za-z0-9]+)", texto)
    if match:
        return match.group(1)

    # ===== TEV (Código alternativo) =====
    match = re.search(r"C[oó]digo da opera[cç][aã]o[: ]+([A-Za-z0-9]+)", texto)
    if match:
        return match.group(1)

    return None

def extrair_nome_recebido(texto):
    """
    Extrai nome do destinatário.
    Suporta:
    - PIX
    - TEV
    """

    # ===== PIX =====
    match = re.search(r"Destino.*?Nome[: ]+([A-Za-zÀ-ÿ\s]+)", texto, re.S)
    if match:
        return match.group(1).strip()

    # ===== TEV =====
    match = re.search(
        r"Nome destinat[áa]rio[: ]*([A-Za-zÀ-ÿ\s]+?)(?:\n|$|Quantidade|Valor|Data)",
        texto
    )
    if match:
        return match.group(1).strip()

    return None

def extrair_data(texto):
    """
    Extrai data da transação.
    Suporta:
    - PIX
    - TEV
    """

    # ===== PIX =====
    match = re.search(r"Data e Hora[: ]+([^\n]+)", texto)
    if match:
        return match.group(1).strip()

    # ===== TEV =====
    match = re.search(r"Data de d[ée]bito[: ]+([^\n]+)", texto)
    if match:
        return match.group(1).strip()

    return None

# ==========================================
# ===== PROCESSADOR BANCO CAIXA ===========
# ==========================================

def processar_banco_caixa(page):
    """
    Processa comprovantes da Caixa (PIX e TEV).
    """

    dados = []

    # ===== Extração de texto da página =====
    texto = page.extract_text()

    if not texto:
        return dados

    # ===== Extração de campos =====
    valor = extrair_valor(texto)
    id_transacao = extrair_id(texto)
    nome = extrair_nome_recebido(texto)
    data = extrair_data(texto)

    # ======================================
    # ========= VALIDAÇÃO MÍNIMA ===========
    # ======================================

    # Aceita comprovantes mesmo se o ID estiver ausente (ex: TEV)
    if valor and nome and data:

        dados.append({
            "Nome Recebido": limpeza.limpar_nome(nome),
            "Data": limpeza.limpar_data(data),
            "Id": limpeza.limpar_id(id_transacao),
            "Valor": valor
        })

    return dados