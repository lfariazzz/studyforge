"""
Responsável por carregar os objetos no banco de dados 

"""


import sys
import os

# Garante que o Python encontre a pasta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.RepositorioGeral import RepositorioGeral
from src.models.municipio import Municipio
from src.models.secretario import Secretario
from src.models.gestor import Gestor
from src.models.professor import Professor
from src.models.aluno import Aluno
from src.models.escola import Escola
from src.models.turma import Turma
from src.models.escola_endereco import Endereco 

def popular_banco():
    if not os.path.exists("data"):
        os.makedirs("data")

    repo = RepositorioGeral()
    print("🚀 Iniciando a carga de dados...")

    try:
        # 🧹 LIMPEZA
        tabelas = ["frequencia", "diario", "nota", "demanda", "turma", "aluno", "professor", "gestor", "secretario", "usuario", "escola", "escola_endereco", "municipio"]
        for tabela in tabelas:
            try:
                repo.cursor.execute(f"DELETE FROM {tabela}")
            except: pass
        repo.connect.commit()
        print("✨ Tabelas limpas.")

        # --- 1. MUNICÍPIO ---
        mun = Municipio("Juazeiro do Norte", None, "CE", 1000000.0, 7.5)
        repo.salvar_municipio(mun)

        # --- 2. SECRETÁRIO ---
        sec = Secretario(None, "Ana Silva", "111.222.333-44", "ana@edu.com", "senha123", "88999998888", "01/01/1985", mun, "Secretaria Geral")
        repo.salvar_usuario(sec)

        # --- 3. ENDEREÇO E ESCOLA ---
        end_escola = Endereco(None, None, "63000-000", "Rua Central", "100", "Centro")
        esc = Escola("Escola Farias Brito", end_escola, None, None, 50000.0, mun, 800)
        repo.salvar_escola(esc)
        
        # --- 4. GESTORES ---
        nomes_gestores = ["Carlos Oliveira", "Beatriz Souza", "Marcos Lima", "Julia Costa", "Ricardo Almeida"]
        for i, nome in enumerate(nomes_gestores):
            gestor = Gestor(None, nome, f"200.000.000-0{i}", f"gestor{i}@edu.com", "senha123", f"8898800000{i}", "10/10/1980", esc)
            repo.salvar_usuario(gestor)

        # --- 5. TURMA ---
        turma = Turma(None, "Oitavo Ano B", 2026, esc, "MANHÃ", 35)
        repo.salvar_turma(turma)

        # --- 6. PROFESSORES ---
        nomes_profs = ["Fernando Silva", "Patricia Gomes", "Roberto Freitas", "Luciana Melo", "Andre Santos", "Carla Dias", "Wilson Neto", "Sandra Rosa", "Fabio Jr", "Teresa Cristina"]
        disciplinas = ["Matemática", "Português", "História", "Geografia", "Ciências"]
        for i, nome in enumerate(nomes_profs, 1):
            disc = disciplinas[i % 5]
            # Ajustado para o padrão RF-2026-000X
            rf_formatado = f"RF-2026-{str(i).zfill(4)}"
            prof = Professor(None, nome, f"300.000.000-{str(i).zfill(2)}", f"prof{i}@edu.com", "senha123", f"889776655{str(i).zfill(2)}", "15/03/1990", rf_formatado, esc, "Especialista", disc, 4500.0)
            repo.salvar_usuario(prof)

        # --- 7. ALUNOS ---
        for i in range(1, 21):
            num = str(i).zfill(2)
            # Ajustado para o padrão MAT-2026-000X caso seu Model exija
            mat_formatada = f"MAT-2026-{str(i).zfill(4)}"
            aluno = Aluno(None, f"Aluno Sobrenome", f"400.000.000-{num}", f"aluno{num}@edu.com", "senha123", f"889665544{num}", "20/05/2012", turma, mat_formatada)
            repo.salvar_usuario(aluno)

        print("\n✅ SUCESSO! O banco foi populado corretamente.")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    popular_banco()