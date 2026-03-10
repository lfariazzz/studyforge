"""
Esse arquivo tem a função de limpar o que for velho e dar início a um secretário no Banco de Dados, que é 
o usuário base para todos os outros. 
"""

import os
from src.database.RepositorioGeral import RepositorioGeral
from src.models.municipio import Municipio
from src.models.secretario import Secretario

def inicializar_sistema():
    # 1. Garante que o repositório aponte para o lugar certo
    repo = RepositorioGeral()
    
    # 2. Limpeza manual para evitar o erro de UNIQUE (Usando self.connect e self.cursor)
    print("🧹 Limpando dados antigos...")
    try:
        repo.cursor.execute("DELETE FROM secretario")
        repo.cursor.execute("DELETE FROM usuario")
        repo.cursor.execute("DELETE FROM municipio")
        repo.connect.commit()
    except Exception as e:
        print(f"Nota: Tabelas limpas ou ainda não existentes.")

    print("🛠️ Criando Município...")
    # Conforme seu Municipio.__init__ e RepositorioGeral.buscar_municipio_por_id
    # Ordem: nome, id, estado, verba, nota_corte
    municipio_obj = Municipio(
        "Juazeiro do Norte", 
        1, 
        "CE", 
        1000000.0, 
        7.0
    )
    repo.salvar_municipio(municipio_obj)

    print("🛠️ Criando Secretário...")
    # Importante: O CPF deve ser enviado exatamente como será digitado no login.
    # Se o seu validador CLI exige pontos, coloque pontos aqui.
    cpf_teste = "123.456.789-01" 
    
    # Ordem baseada no seu buscar_secretario_por_id: 
    # id, nome, cpf, email, senha, telefone, data_nasc, municipio_obj, depto
    # A ordem real que o seu banco está pedindo:
    admin_sec = Secretario(
        1,
        "Admin",                  # Nome curto e só letras
        "12345678901",            # CPF só números
        "admin@studyforge.com",
        "admin12345",
        "88999999999",
        "01/01/1980",
        municipio_obj,
        "EDUCACAO"
    )
    try:
        repo.salvar_usuario(admin_sec)
        print(f"\n✅ SUCESSO!")
        print(f"📍 Banco criado em: {os.path.abspath('data/studyforge.db')}")
        print(f"👤 CPF: {cpf_teste}")
        print(f"🔑 Senha: admin12345")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")

if __name__ == "__main__":
    inicializar_sistema()