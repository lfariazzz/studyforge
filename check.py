import sqlite3
import os

# Caminho que o seu find confirmou
db_path = "data/studyforge.db"

def verificar_banco():
    if not os.path.exists(db_path):
        print(f"❌ Erro: O arquivo {db_path} não existe!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"✅ Conectado ao banco: {os.path.abspath(db_path)}")
    
    # 1. Verifica se a tabela usuário tem dados
    cursor.execute("SELECT * FROM usuario")
    usuarios = cursor.fetchall()
    
    if not usuarios:
        print("📭 A tabela 'usuario' está TOTALMENTE VAZIA!")
    else:
        print(f"👥 Total de usuários: {len(usuarios)}")
        for u in usuarios:
            # No seu buscar_usuario_por_cpf, o tipo é o índice 9
            print("-" * 30)
            print(f"ID: {u[0]}")
            print(f"NOME: {u[1]}")
            print(f"CPF: '{u[2]}' (Tamanho: {len(u[2])})")
            print(f"SENHA: {u[3]}")
            try:
                print(f"TIPO (Índice 9): '{u[9]}'")
            except:
                print("❌ A tabela não tem 10 colunas (o índice 9 falhou)")
    
    conn.close()

if __name__ == "__main__":
    verificar_banco()