import re

def identificar_banco(texto):
    if not texto:
        return None

    t = texto.lower()

    # ===== NUBANK =====
    if (
        "nu pagamentos s.a" in t or
        "nubank" in t or
        "nubank.com.br" in t
    ):
        return "nubank"

    # ===== INTER =====
    if (
        "banco inter" in t or
        "inter empresas" in t or
        "contadigital.inter.co" in t
    ):
        return "inter"

    # ===== CAIXA =====
    if (
        "caixa econômica federal" in t or
        "gerenciador caixa" in t or
        "internet banking caixa" in t
    ):
        return "caixa"

    # ===== ITAÚ =====
    if (
        "banco itaú" in t or
        "itau.com.br" in t or
        "via sispag" in t
    ):
        return "itau"

    # ===== SANTANDER =====
    if (
        "banco santander" in t or
        "internet banking empresarial" in t or
        "getnet" in t
    ):
        return "santander"

    return None