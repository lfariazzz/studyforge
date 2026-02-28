import sys
import os

# Ajuste de path para localizar o diretório 'src'
raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
pasta_src = os.path.join(raiz, 'src')
if pasta_src not in sys.path:
    sys.path.insert(0, pasta_src)

from models.escola import Escola
from unittest.mock import MagicMock

def executar_teste_visual_escola():
    print("="*50)
    print("INICIANDO BATERIA DE TESTES: CLASSE ESCOLA")
    print("="*50)

    # 1. Instanciação e Getters
    try:
        # Mock do Gestor para inicialização
        mock_gestor = MagicMock()
        mock_gestor.nome = "Diretor Jair"
        
        esc = Escola(
            nome="Escola Estudo Forjado", 
            endereco="Rua da POO, 123", 
            id_escola=10, 
            gestor_atual=mock_gestor, 
            verba_disponivel_escola=5000.0, 
            id_municipio=1, 
            capacidade_infraestrutura=100
        )
        
        print("\n[GETTERS - ESTADO INICIAL]")
        print(f"ID: {esc.id_escola} | Esperado: 10")
        print(f"Nome: {esc.nome} | Esperado: Escola Estudo Forjado")
        print(f"Gestor: {esc.gestor_atual.nome} | Esperado: Diretor Jair")
        print(f"Capacidade: {esc.capacidade_infraestrutura} alunos | Esperado: 100")
        print(f"Verba: R$ {esc.verba_disponivel_escola} | Esperado: 5000.0")

        # 2. Setters e Restrições
        print("\n[SETTERS - TESTANDO RESTRIÇÕES]")
        
        # Teste Verba Negativa
        try:
            esc.verba_disponivel_escola = -1.0
        except ValueError as e:
            print(f"OK - Barrou verba negativa: {e}")
            
        # Teste Capacidade Negativa
        try:
            esc.capacidade_infraestrutura = -10
        except ValueError as e:
            print(f"OK - Barrou capacidade negativa: {e}")

        # 3. Métodos - Comportamento e Infraestrutura
        print("\n[MÉTODOS - COMPORTAMENTO]")
        
        # Simulação de Turma com alunos
        mock_turma = MagicMock()
        mock_aluno1 = MagicMock(frequencia=100.0)
        mock_aluno2 = MagicMock(frequencia=80.0)
        mock_turma.alunos_matriculados = [mock_aluno1, mock_aluno2] # 2 alunos
        
        # Adição de Turma
        if esc.adicionar_turma(mock_turma):
            print(f"OK - Turma adicionada. Alunos atuais: 2")
        
        # Teste de bloqueio de redução de capacidade
        try:
            esc.capacidade_infraestrutura = 1 # Tentar reduzir para 1 tendo 2 alunos
        except ValueError as e:
            print(f"OK - Impediu reduzir prédio abaixo da lotação: {e}")

        # Teste de Frequência
        media = esc.gerar_relatorio_frequencia()
        print(f"OK - Média de frequência calculada: {media}% | Esperado: 90.0%")

        # Teste de Locação
        esc._professores_empregados = [MagicMock()]
        if esc.atualizar_locacao():
            print("OK - Locação atualizada com professores e turmas.")

        # 4. To_Dict - Validação Final
        print("\n[TO_DICT - VALIDAÇÃO FINAL]")
        dicionario = esc.to_dict()
        print(f"OK - Nome no dict: {dicionario['nome']}")
        print(f"Dicionário final: {dicionario}")
        
        print("\n" + "="*50)
        print("TESTES FINALIZADOS COM SUCESSO")
        print("="*50)

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO DURANTE OS TESTES: {e}")

if __name__ == "__main__":
    executar_teste_visual_escola()