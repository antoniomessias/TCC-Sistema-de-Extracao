# ==========================================
# ============== IMPORTAÇÕES ==============
# ==========================================

# ===== Variáveis de ambiente =====
from dotenv import load_dotenv
import os

# ===== Banco de Dados PostgreSQL =====
import psycopg2


# ==========================================
# ========== CONFIGURAÇÃO AMBIENTE =========
# ==========================================

# Carrega variáveis do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ==========================================
# ============ CONEXÃO COM BANCO ===========
# ==========================================

def conectar():
    """
    Cria e retorna uma nova conexão com o banco PostgreSQL.
    """
    return psycopg2.connect(DATABASE_URL)


# ==========================================
# ============ CRIAÇÃO DE TABELAS ==========
# ==========================================

def criar_tabela():
    """
    Cria a tabela de usuários caso ela não exista.
    """

    conn = conectar()
    cursor = conn.cursor()

    # ===== Tabela de Usuários =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha TEXT NOT NULL
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("Tabela verificada/criada com sucesso!")