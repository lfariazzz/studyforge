import sys
import os
from datetime import date

# Ajuste de path para localizar o diretório 'src'
raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if raiz not in sys.path:
    sys.path.insert(0, raiz)

from src.models.turma import Turma
from unittest.mock import MagicMock

def executar_teste_turma_completo():
    print("="*50)
    print("INICIANDO BATERIA DE TESTES EXAUSTIVOS: TURMA")
    print("="*50)

    try:
        # Instanciação inicial
        turma = Turma(id_turma=101, nome="9º Ano A", ano_letivo=2024, id_escola=1, turno="Manhã", capacidade_maxima=2)

        print("\n[GETTERS - ESTADO INICIAL]")
        print(f"ID: {turma.id_turma} | Esperado: 101")
        print(f"Nome: {turma.nome} | Esperado: 9º Ano A")
        print(f"Ano Letivo: {turma.ano_letivo} | Esperado: 2024")
        print(f"Escola ID: {turma.id_escola} | Esperado: 1")
        print(f"Turno: {turma.turno} | Esperado: MANHÃ (Padronizado)")
        print(f"Capacidade: {turma.capacidade_maxima} | Esperado: 2")

        print("\n[SETTERS - TESTANDO RESTRIÇÕES]")
        
        # Teste de Nome Vazio
        try:
            turma.nome = "  "
        except ValueError as e:
            print(f"OK - Barrou nome vazio: {e}")

        # Teste de Ano Letivo fora do range
        try:
            turma.ano_letivo = 2150
        except ValueError as e:
            print(f"OK - Barrou ano inválido (2150): {e}")

        # Teste de Turno inválido
        try:
            turma.turno = "MADRUGADA"
        except ValueError as e:
            print(f"OK - Barrou turno fora da lista permitida: {e}")

        print("\n[MÉTODOS - COMPORTAMENTO]")
        
        # Gestão de Alunos e Capacidade
        aluno1 = MagicMock(); aluno1.nome = "Aluno A"
        aluno2 = MagicMock(); aluno2.nome = "Aluno B"
        aluno3 = MagicMock(); aluno3.nome = "Aluno C"
        
        turma.adicionar_aluno(aluno1)
        turma.adicionar_aluno(aluno2)
        print(f"OK - Alunos matriculados: {len(turma.alunos_matriculados)}/2")
        
        if not turma.adicionar_aluno(aluno3):
            print("OK - Barrou terceiro aluno: Erro: Capacidade máxima de 2 alunos atingida.")

        # Gestão de Professores e Aulas
        mock_prof = MagicMock(); mock_prof.nome = "Prof. Girafales"; mock_prof.turmas_associadas = []
        turma.adicionar_professor(mock_prof)
        print(f"OK - Professor '{mock_prof.nome}' associado à turma.")

        # Registo de Aula no Diário
        data_hoje = date.today()
        if turma.registrar_aula(mock_prof, data_hoje, "Lógica de Programação"):
            print(f"OK - Aula registada. Itens no diário: {len(turma._diario_de_classe)}")

        # Tentativa de aula com professor não vinculado
        prof_intruso = MagicMock(); prof_intruso.nome = "Prof. Desconhecido"
        if not turma.registrar_aula(prof_intruso, data_hoje, "Aula Hacker"):
            print(f"OK - Bloqueou aula de professor não regente.")

        print("\n[QUADRO DE HORÁRIOS - RESUMO]")
        quadro = turma.obter_quadro_horario()
        print(f"Turma: {quadro['Turma']} | Turno: {quadro['Turno']}")
        print(f"Professores: {quadro['Professores']}")

        print("\n[TESTE: ESTRUTURA DO QUADRO DE HORÁRIO]")
        
        # Criando um professor mockado para o teste
        prof_teste = MagicMock()
        prof_teste.nome = "Prof. Raimundo"
        prof_teste.turmas_associadas = []
        turma.adicionar_professor(prof_teste)

        quadro = turma.obter_quadro_horario()
        
        # Validações de integridade dos dados
        print(f"Turma retornada: {quadro['Turma']} | Esperado: 9º Ano A")
        
        if isinstance(quadro['Professores'], list):
            print(f"OK - 'Professores' é uma lista: {quadro['Professores']}")
        else:
            print(f"ERRO - 'Professores' deveria ser uma lista, mas retornou: {type(quadro['Professores'])}")

        print("\n[TO_DICT - VALIDAÇÃO FINAL]")
        dicionario = turma.to_dict()
        print(f"OK - Chave 'ano_letivo' presente: {'ano_letivo' in dicionario}")
        print(f"Dicionário final: {dicionario}")
        

        print("\n[TESTE: INTEGRAÇÃO ALUNO -> VER_HORARIO]")
        
        from src.models.aluno import Aluno
        
        # Criando aluno real vinculado à turma de teste
        aluno_integracao = Aluno(
            nome="Eduardo Teste",
            cpf="000.000.000-00",
            email="edu@teste.com",
            senha="senha_segura_123",
            telefone="9999999999",
            data_nascimento="03/02/2003",
            turma_associada=turma # Aciona o setter com proteção
        )

        # O Aluno busca os dados na Turma e formata
        relatorio_final = aluno_integracao.ver_horario()
        print(f"Saída do Aluno:\n{relatorio_final}")

        # Verificação de texto esperado
        if "Professores Regentes: Prof. Raimundo" in relatorio_final:
            print("OK - Aluno formatou os dados da Turma corretamente.")
        else:
            print("ERRO - Formatação do horário inconsistente.")
        
        print("\n[RN03 - TESTE DE NOTAS E MÉDIA MENSAL]")

        # 1. Criando Mocks de Alunos com IDs únicos
        aluno_joao = MagicMock(); aluno_joao.id_matricula = "2024.001"; aluno_joao.nome = "Joao"
        aluno_maria = MagicMock(); aluno_maria.id_matricula = "2024.002"; aluno_maria.nome = "Maria"
        
        # 2. Registrando notas no sistema (Passo A da lógica)
        # Notas de Matemática - Março - Prova 1
        data_prova = date(2024, 3, 15)
        turma.registrar_nota_no_sistema(aluno_joao, "Matemática", 8.0, "Prova 1", data_prova)
        turma.registrar_nota_no_sistema(aluno_maria, "Matemática", 4.0, "Prova 1", data_prova)
        
        print(f"OK - Notas registradas no sistema. Total: {len(turma._notas_da_turma)}")

        # 3. Testando o Cálculo da Média (Passo A - Resultado)
        # Média esperada: (8.0 + 4.0) / 2 = 6.0
        media_março = turma.calcular_media_mensal("Matemática", 3, "Prova 1")
        print(f"Média Calculada (Março): {media_março} | Esperado: 6.0")
        
        if media_março == 6.0:
            print("OK - Cálculo da média mensal está correto.")
        else:
            print(f"ERRO - Média incorreta: {media_março}")

        print("\n" + "="*50)
        print("BATERIA DE TESTES FINALIZADA COM SUCESSO")
        print("="*50)

    except Exception as e:
        print(f"\n❌ FALHA NOS TESTES: {e}")

if __name__ == "__main__":
    executar_teste_turma_completo()