import sys
import os
from datetime import date

# Ajuste do Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.database.RepositorioGeral import RepositorioGeral
from src.services.avaliador_frequencia import AvaliadorFrequencia
from src.models.diario import Diario

def testar_gatilho_evasao():
    repo = RepositorioGeral()
    avaliador = AvaliadorFrequencia()
    
    print("🚀 Iniciando Teste de Automação (RN02)...")

    # 1. Tentar carregar uma turma real do banco
    # Se não tiver, você precisará passar um ID que exista no seu banco (ex: 1)
    id_turma_teste = 1 
    turma = repo.buscar_turma_por_id(id_turma_teste)

    if not turma:
        print("❌ Erro: Não encontrei uma turma com ID 1 no banco para testar.")
        return

    print(f"✅ Turma encontrada: {turma.nome}")

    # 2. Simular a criação de um Diário (Aula)
    # Conteudo: Teste de Evasão
    id_professor = 1 # ID de um professor existente
    novo_diario = Diario(None, "Matemática", date.today(), "Teste Evasão", id_professor, id_turma_teste)
    
    print("📝 Criando registro de aula com 100% de faltas...")
    id_diario = repo.criar_diario_classe(id_turma_teste, id_professor, date.today().isoformat(), "Teste de Gatilho")

    # 3. Registrar faltas para todos os alunos (Simula Evasão Crítica)
    alunos = repo.listar_alunos_por_turma(id_turma_teste)
    for aluno in alunos:
        repo.registrar_frequencia(id_diario, aluno._id_usuario, "FALTA")
    
    print(f"📉 Chamada realizada: {len(alunos)} faltas registradas.")

    # 4. DISPARAR O AVALIADOR (Igual ao código do Professor)
    print("🔍 Executando Avaliador de Frequência...")
    # Recarregamos a turma para que ela venha com os novos diários
    turma_atualizada = repo.buscar_turma_por_id(id_turma_teste)
    
    mes_atual = date.today().month
    nova_demanda = avaliador.verificar_media_frequencia_mensal(turma_atualizada, mes_atual)

    # 5. VERIFICAR SE A FACTORY CRIOU A DEMANDA
    if nova_demanda:
        print(f"🔥 SUCESSO! Factory gerou demanda: {nova_demanda.descricao}")
        
        # 6. TESTAR O REPOSITÓRIO DO SEU AMIGO
        try:
            repo.salvar_demanda(nova_demanda)
            print("💾 BANCO DE DADOS: Demanda salva com sucesso nas tabelas de herança!")
        except Exception as e:
            print(f"❌ BANCO DE DADOS: Falha ao salvar no SQL. Erro: {e}")
    else:
        print("ℹ️ Nenhuma demanda gerada (Média ainda acima de 75% ou sem dados suficientes).")

if __name__ == "__main__":
    testar_gatilho_evasao()