# ==========================================
# ============== IMPORTAÇÕES ==============
# ==========================================

import re
import utils.limpeza as limpeza

# ==========================================
# ===== PROCESSADOR BANCO BRADESCO ========
# ==========================================

def processar_banco_bradesco(texto):
    """
    Processa comprovantes do Bradesco (versão básica).

    Extrai:
    - ID da transação
    - Nome do favorecido
    - Data
    - Valor
    """

    # ===== Validação inicial =====
    if not texto:
        return []

    # ===== Normalização do texto =====
    linhas = [
        linha.strip()
        for linha in texto.split('\n')
        if linha.strip()
    ]

    # ======================================
    # ========== VARIÁVEIS DE EXTRAÇÃO =====
    # ======================================

    id_transacao = ""
    nome = ""
    data = ""
    valor = ""

    # ======================================
    # ========= EXTRAÇÃO DO ID ============
    # ======================================

    for linha in linhas:
        if "transação" in linha.lower() or "código" in linha.lower():

            match = re.search(r'[A-Z0-9]{20,}', linha)

            if match:
                id_transacao = match.group(0)
                break

    # ======================================
    # ========= EXTRAÇÃO DO VALOR ==========
    # ======================================

    for linha in linhas:
        if "valor" in linha.lower() and "r$" in linha.lower():

            match = re.search(r'R\$\s*([\d\.,]+)', linha)

            if match:
                valor_bruto = match.group(1)
                valor = f"R$ {valor_bruto}"
                break

    # ======================================
    # ========= EXTRAÇÃO DA DATA ===========
    # ======================================

    for linha in linhas:

        match = re.search(r'(\d{2})/(\d{2})/(\d{4})', linha)

        if match:
            data = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
            break

    # ======================================
    # ========= EXTRAÇÃO DO NOME ===========
    # ======================================

    em_destino = False

    for i, linha in enumerate(linhas):

        if "destino" in linha.lower() or "favorecido" in linha.lower():
            em_destino = True
            continue

        if em_destino and "nome" in linha.lower():

            # Caso esteja no formato: Nome: João
            if ":" in linha:
                partes = linha.split(":", 1)
                if len(partes) > 1:
                    nome = partes[1].strip()
                    break

            # Caso o nome esteja na linha seguinte
            elif i + 1 < len(linhas):
                nome = linhas[i + 1].strip()
                break

    # ======================================
    # ========= VALIDAÇÃO FINAL ============
    # ======================================

    if id_transacao or (nome and valor):

        return [{
            "Nome Recebido": limpeza.limpar_nome(nome),
            "Data": limpeza.limpar_data(data),
            "Id": id_transacao,
            "Valor": valor
        }]

    return []