# ==========================================
# ============== IMPORTAÇÕES ==============
# ==========================================

# ===== Bibliotecas padrão =====
import os
import io
import csv
from io import StringIO

# ===== Manipulação de PDF e Imagem =====
import fitz
from PIL import Image

# ===== Flask =====
from flask import (
    Flask, render_template, request,
    redirect, url_for, session,
    jsonify, send_file, Response
)

# ===== Segurança =====
from werkzeug.security import generate_password_hash, check_password_hash

# ===== Banco de Dados =====
from database import conectar, criar_tabela

# ===== Processador Inteligente =====
from main import processar_arquivo

# ==========================================
# ============ CONFIGURAÇÕES APP ===========
# ==========================================

app = Flask(__name__)
app.secret_key = "super_chave_secreta"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

criar_tabela()

# ===== Variáveis globais =====
current_file = None
total_pages = 1

# ==========================================
# ============== ROTAS GERAIS ==============
# ==========================================

@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# ==========================================
# ============ PROCESSAMENTO OCR ===========
# ==========================================

@app.route('/processar', methods=['POST'])
def processar():
    global current_file, total_pages

    file = request.files.get('file')
    if not file:
        return jsonify({"sucesso": False, "mensagem": "Nenhum arquivo enviado."})

    # ===== Salvar Arquivo =====
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)
    current_file = filename

    # ===== Processar Arquivo =====
    resultado = processar_arquivo(filename)

    dados = resultado.get("extracted", [])
    paginas_nao_capturadas = resultado.get("pages_without_data", [])
    total_paginas = resultado.get("pages", 0)

    # ===== Salvar na sessão =====
    session["ultimos_resultados"] = {
        "dados": dados,
        "nao_capturadas": paginas_nao_capturadas,
        "total_paginas": total_paginas
    }

    return jsonify({
        "sucesso": True,
        "resultados": dados,
        "paginas_nao_capturadas": paginas_nao_capturadas,
        "total_paginas": total_paginas
    })

# ==========================================
# ============== PREVIEW PÁGINAS ===========
# ==========================================

@app.route('/page/<int:page>')
def get_page(page):
    global current_file

    if not current_file:
        return "Nenhum arquivo carregado", 404

    # ===== Se for PDF =====
    if current_file.lower().endswith('.pdf'):

        doc = fitz.open(current_file)

        if page < 1 or page > len(doc):
            return "Página inválida", 404

        pdf_page = doc.load_page(page - 1)
        pix = pdf_page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        doc.close()

        return send_file(
            io.BytesIO(img_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name=f'page_{page}.png'
        )

    # ===== Se for imagem =====
    else:
        img = Image.open(current_file)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')

# ==========================================
# ============ AUTENTICAÇÃO ================
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        senha = request.form['senha']

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        conn.close()

        # ===== Validação de senha =====
        if usuario and check_password_hash(usuario[3], senha):
            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[1]
            return redirect(url_for('dashboard'))

        return render_template('login.html', erro="Email ou senha inválidos")

    return render_template('login.html')

@app.route('/logout')
def logout():
    global current_file

    # Apagar TODOS os arquivos da pasta uploads
    for f in os.listdir(UPLOAD_FOLDER):
        caminho = os.path.join(UPLOAD_FOLDER, f)
        if os.path.isfile(caminho):
            os.remove(caminho)

    current_file = None
    session.clear()

    return redirect(url_for('login'))

# ==========================================
# ============== DASHBOARD =================
# ==========================================

@app.route('/dashboard')
def dashboard():

    if 'usuario_id' not in session:
        return jsonify({"sucesso": False, "mensagem": "Usuário não autenticado"})

    return render_template('dashboard.html', nome=session['usuario_nome'])

# ==========================================
# ================ EXPORTAÇÃO ==============
# ==========================================
@app.route("/exportar_csv")
def exportar_csv():

    resultados = session.get("ultimos_resultados")

    if not resultados:
        return "Nenhum dado para exportar."

    dados = resultados["dados"]
    nao_capturadas = resultados["nao_capturadas"]
    total_paginas = resultados["total_paginas"]

    output = StringIO()

    # ===== PARTE 1 - Dados extraídos =====
    if dados:
    # Defina a ordem exata aqui
        fieldnames = ["Nome Recebido", "Data", "Id", "Valor"]
        
        writer = csv.DictWriter(
            output, 
            fieldnames=fieldnames, 
            delimiter=";",
            extrasaction='ignore' # Ignora chaves que não estão no fieldnames
        )
        
        writer.writeheader()
        writer.writerows(dados)

    # ===== PARTE 2 - Estatísticas =====
    output.write("\n\nResumo;\n")
    output.write(f"Total de páginas;{total_paginas}\n")
    output.write(f"Páginas não capturadas;{len(nao_capturadas)}\n")

    if total_paginas > 0:
        taxa = ((total_paginas - len(nao_capturadas)) / total_paginas) * 100
        output.write(f"Taxa de sucesso;{taxa:.1f}%\n")

    # ===== PARTE 3 - Páginas sem dados =====
    if nao_capturadas:
        output.write("\nPaginas sem dados;\n")
        for pagina in nao_capturadas:
            output.write(f"{pagina};\n")

    return Response(
        output.getvalue().encode("utf-8-sig"),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=resultados.csv"
        }
    )

# ==========================================
# ============== CRIAR USUÁRIO =============
# ==========================================

@app.route("/criar_usuario", methods=["GET", "POST"])
def criar_usuario():

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        # ===== Verificar se já existe =====
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            conn.close()
            return render_template("criar_usuario.html", erro="Email já cadastrado.")

        # ===== Criar hash da senha =====
        senha_hash = generate_password_hash(senha)

        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("criar_usuario.html")

# ==========================================
# ============== EXECUÇÃO APP ==============
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)