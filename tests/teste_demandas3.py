"""
Esse teste serve para testar o fluxo da RN04
"""



import sys
import os

# Garante que o Python encontre a pasta 'src' independente de onde o teste é rodado
sys.path.append(os.getcwd())

from src.models.nota import Nota
from src.models.turma import Turma
from src.services.avaliador_lacuna import AvaliadorLacuna
from src.core.demanda_factory import DemandaFactory

# Mock simples para o Município e Usuário (Simulando o Banco de Dados)
class MockMunicipio:
    def __init__(self):
        self.id_municipio = "MUN-001"
        self.nome = "Juazeiro do Norte"
        self.nota_de_corte = 7.0             # Alunos abaixo de 7.0 estão em risco
        self.lacuna_maxima_permitida = 0.3   # Mais de 30% da turma em risco gera alerta
        self.media_frequencia = 0.75         # Meta de 75% de presença

class MockProfessor:
    def __init__(self, municipio):
        self.nome = "Prof. Newton"
        self.municipio_responsavel = municipio

def executar_teste():
    print("\n" + "="*60)
    print("SISTEMA DE MONITORAMENTO - TESTE DE FLUXO RN04 (NOTAS)")
    print("="*60)

    # 1. Configuração do Cenário
    municipio = MockMunicipio()
    professor = MockProfessor(municipio)
    
    # Criando a Turma com todos os argumentos obrigatórios que o seu modelo exige
    turma_9a = Turma(
        id_turma="T9A", 
        nome="9º Ano A", 
        ano_letivo=2024, 
        id_escola="ESC-101", 
        turno="Manhã"
    )
    
    # Simulando a lista de alunos matriculados para o cálculo do total
    turma_9a._alunos_matriculados = [1, 2, 3, 4, 5] 

    # 2. Criando Notas: 3 notas baixas (risco) e 2 notas altas (sucesso)
    # Proporção: 3/5 = 60%. Como 60% > 30% (limite do muni), deve gerar demanda.
    # 2. Criando Notas: Incluindo o argumento 'tipo' que é obrigatório
    turma_9a.notas = [
        Nota(1, 101, "T9A", "Matemática", 5.5, "2024-03-07", "Mensal"),
        Nota(2, 102, "T9A", "Matemática", 4.0, "2024-03-07", "Mensal"),
        Nota(3, 103, "T9A", "Matemática", 6.5, "2024-03-07", "Mensal"),
        Nota(4, 104, "T9A", "Matemática", 8.0, "2024-03-07", "Mensal"),
        Nota(5, 105, "T9A", "Matemática", 9.5, "2024-03-07", "Mensal"),
    ]

    print(f"[*] Cenário: Turma com 5 alunos | Nota de Corte: {municipio.nota_de_corte}")

    # 3. Executando o AvaliadorLacuna (O "Motor" de decisão)
    avaliador = AvaliadorLacuna()
    precisa, indice, relatorio = avaliador.validar_reforco(turma_9a, municipio, "Matemática")

    print(f"[*] Índice de Lacuna Calculado: {indice*100:.1f}%")

    # 4. Acionando a Factory para criar a DemandaPedagogica
    if precisa:
        print("[!] ALERTA: Reforço Necessário! Criando Demanda via Factory...")
        
        demanda = DemandaFactory.criar_demanda(
            tipo_demanda="PEDAGOGICA",
            solicitante=professor,
            descricao="Alerta Automático: Baixo desempenho em Matemática",
            prioridade="ALTA",
            turma=turma_9a,
            relatorio_alunos=relatorio,
            indice_lacuna=indice,
            disciplina_alvo="Matemática",
            professor=professor.nome,
            frequencia_turma=0.82 # Simulação de frequência acima da meta
        )

        # 5. Processando a solicitação para formatar o texto do relatório
        demanda.processar_solicitacao(usuario="Admin_Teste")

        print("\n" + "-"*20 + " RELATÓRIO FINAL " + "-"*20)
        print(demanda.alerta_gerado)
        print(f"Status Final no Sistema: {demanda.status}")
        print("-" * 57)
    else:
        print("[OK] Desempenho da turma está dentro da normalidade.")

if __name__ == "__main__":
    try:
        executar_teste()
    except Exception as e:
        print(f"\n[ERRO DURANTE O TESTE]: {e}")
        # Exibe onde o erro ocorreu para facilitar o debug
        import traceback
        traceback.print_exc()