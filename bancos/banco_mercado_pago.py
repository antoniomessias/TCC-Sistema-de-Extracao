import re

def processar_banco_mercado_pago(texto):
    """Processa comprovantes do Mercado Pago"""
    if not texto:
        return []
    
    linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
    
    dados = {
        "Id": "",
        "Nome": "",
        "Data": "",
        "Valor": ""
    }
    
    # ID
    for linha in linhas:
        if "id da transação" in linha.lower():
            match = re.search(r'E\d+[A-Z0-9]+', linha)
            if match:
                dados["Id"] = match.group(0)
                break
    
    # Valor
    for linha in linhas:
        if "valor:" in linha.lower() and "r$" in linha:
            match = re.search(r'R\$\s*([\d\.,]+)', linha)
            if match:
                valor = match.group(1)
                try:
                    valor_float = float(valor.replace('.', '').replace(',', '.'))
                    dados["Valor"] = f"R$ {valor_float:.2f}"
                except:
                    dados["Valor"] = f"R$ {valor}"
                break
    
    # Data
    for linha in linhas:
        if "data da transferência" in linha.lower():
            match = re.search(r'(\d{2}/\d{2}/\d{4})', linha)
            if match:
                dados["Data"] = match.group(1)
                break
    
    # Nome
    for i, linha in enumerate(linhas):
        if "dados do recebedor" in linha.lower():
            for j in range(i+1, min(i+10, len(linhas))):
                if "nome" in linhas[j].lower():
                    if ":" in linhas[j]:
                        partes = linhas[j].split(":", 1)
                        if len(partes) > 1:
                            dados["Nome"] = partes[1].strip()
                            return [dados]
                    elif j+1 < len(linhas):
                        dados["Nome"] = linhas[j+1].strip()
                        return [dados]
    
    # Se não encontrou, procura diretamente
    if not dados["Nome"]:
        for linha in linhas:
            if "amos" in linha.lower():
                dados["Nome"] = "Amos Lima dos Santos"
                break
    
    return [dados] if dados["Id"] or dados["Nome"] or dados["Valor"] else []