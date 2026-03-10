import sys
import os

# 1. AJUSTE DE PATH: Garante que o Python encontre a pasta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.RepositorioGeral import RepositorioGeral
from src.models.municipio import Municipio
from src.models.escola import Escola
from src.models.escola_endereco import Endereco
from src.models.gestor import Gestor
from src.models.professor import Professor
from src.models.aluno import Aluno
from src.models.turma import Turma

def popular():
    # 2. RESET DO BANCO: Deleta o arquivo antigo para não duplicar dados
    if os.path.exists("data/studyforge.db"):
        try:
            os.remove("data/studyforge.db")
            print("🗑️ Banco resetado para nova carga.")
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível remover o arquivo do banco: {e}")

    repo = RepositorioGeral()

    try:
        # 3. MUNICÍPIO (nome, id, estado, verba, nota)
        mun = Municipio("Juazeiro do Norte", None, "CE", 1000000.0, 7.5)
        repo.salvar_municipio(mun)
        print(f"✅ Município salvo: {mun.nome}")

        # 4. ESCOLA (nome, endereco, id, id_gestor, verba, id_mun, capacidade, objeto_mun)
        end = Endereco(None, None, "63000-000", "Rua Central", "100", "Centro")
        esc = Escola("Escola Farias Brito", end, None, None, 50000.0, mun._id_municipio, 100, mun)
        repo.salvar_escola(esc)
        print(f"✅ Escola salva: {esc.nome}")

        # 5. GESTOR (Beatriz - Senha min 8, Tel 11 digitos)
        beatriz = Gestor(
            None, "Beatriz Souza", "200.000.000-01", "gestor1@edu.com", 
            "senha123", "88999990001", "10/10/1980", esc
        )
        repo.salvar_usuario(beatriz)
        print(f"✅ Gestor Beatriz vinculado à Escola {esc._id_escola}")

        # 6. TURMA (id, nome, ano, objeto_escola, turno, capacidade)
        turma_a = Turma(None, "Nono Ano A", 2026, esc, "MANHÃ", 40)
        repo.salvar_turma(turma_a)
        # Sincroniza na memória para o cálculo imediato das estatísticas
        if not hasattr(esc, '_turmas_existentes'):
            esc._turmas_existentes = []
        esc._turmas_existentes.append(turma_a)
        print(f"✅ Turma '{turma_a.nome}' criada.")

        # 7. PROFESSOR (RF e Titulação validados)
        prof = Professor(
            None, "Ricardo Bug", "300.000.000-01", "prof@edu.com", 
            "senha123", "88999990002", "01/01/1980", "RF-2026-0001", 
            esc, "Mestre", "Matematica", 5000.0
        )
        repo.salvar_usuario(prof)
        if not hasattr(esc, '_professores_empregados'):
            esc._professores_empregados = []
        esc._professores_empregados.append(prof)
        print(f"✅ Professor {prof.nome} salvo.")

        # 8. ALUNOS (Nomes sem números e Matrícula padrão)
        nomes_exemplo = [
            "Ana Silva", "Bruno Costa", "Carla Souza", "Daniel Oliveira", 
            "Eduarda Lima", "Fabio Santos", "Gabriel Jesus", "Helena Rocha", 
            "Igor Mendes", "Julia Ferreira"
        ]

        for i, nome_aluno in enumerate(nomes_exemplo, 1):
            num_formatado = str(i).zfill(4)
            aluno = Aluno(
                None, nome_aluno, f"400.000.000-{i:02d}", f"aluno{i}@edu.com", 
                "senha123", f"889888877{i:02d}", "20/05/2012", 
                turma_a, f"MAT-2026-{num_formatado}"
            )
            repo.salvar_usuario(aluno)
            turma_a.adicionar_aluno(aluno)
        
        print(f"✅ {len(nomes_exemplo)} Alunos matriculados com sucesso.")
        print("\n🚀 SUCESSO TOTAL! O banco está pronto para a Opção 2.")

    except Exception as e:
        print(f"\n❌ ERRO NA CARGA: {e}")
        # Opcional: descomente a linha abaixo para ver o erro exato de identação se persistir
        # import traceback; traceback.print_exc()

if __name__ == "__main__":
    popular()