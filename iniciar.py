from database import conectar
from werkzeug.security import generate_password_hash

def criar_usuario():
    conn = conectar()
    cursor = conn.cursor()

    senha_hash = generate_password_hash("123456")

    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha)
        VALUES (%s, %s, %s)
    """, ("Antonio", "antonio@email.com", senha_hash))

    conn.commit()
    cursor.close()
    conn.close()

    print("Usuário criado com sucesso!")

if __name__ == "__main__":
    criar_usuario()
