"""
Para executar este teste, use o comando:
    python -m unittest tests.teste_professor.TestProfessor -v
"""
import unittest
from datetime import date
from src.models.professor import Professor

# --- MOCKS PARA SIMULAR DEPENDÊNCIAS ---
class MockEscola:
    def __init__(self):
        self.id_escola = 1
        self.nome = "Escola Técnica Industrial"

class MockAluno:
    def __init__(self, nome):
        self.nome = nome
        self.notas_recebidas = []
        self.presencas = []

    def adicionar_nota(self, disciplina, valor):
        self.notas_recebidas.append((disciplina, valor))

    def registrar_presenca(self, data, presente):
        self.presencas.append({"data": data, "presenca": presente})

class MockTurma:
    def __init__(self, nome):
        self.nome = nome
        self.alunos_matriculados = []
        self._materiais_postados = []
        self.aulas_registradas = []
        self.notas_sistema = []

    def adicionar_aluno(self, aluno):
        self.alunos_matriculados.append(aluno)

    def registrar_aula(self, professor, data, conteudo):
        self.aulas_registradas.append({"data": data, "conteudo": conteudo})

    def registrar_nota_no_sistema(self, aluno, disciplina, valor, tipo, data):
        self.notas_sistema.append({"aluno": aluno.nome, "valor": valor})

# --- CLASSE DE TESTE PRINCIPAL ---
class TestProfessor(unittest.TestCase):

    def setUp(self):
        self.escola = MockEscola()
        self.professor = Professor(
            id_usuario=1,
            nome="Roberto Oliveira",
            cpf="999.888.777-66",
            email="roberto.prof@escola.com",
            senha="senha123",
            telefone="88912345678",
            data_nascimento="10/05/1975",
            registro_funcional="RF-2026-1234",
            escola_associada=self.escola,
            titulacao="Doutor",
            area_atuacao="Física",
            salario=7500.0
        )
        self.turma = MockTurma("3º Ano B")
        self.aluno = MockAluno("Carlos Eduardo")
        self.turma.adicionar_aluno(self.aluno)

    def test_validacao_rf_e_titulacao(self):
        """Testa se o Setter de RF e Titulação valida os formatos corretamente."""
        # RF Inválido
        with self.assertRaises(ValueError):
            self.professor.registro_funcional = "ABC-123"
        
        # Titulação Inválida
        with self.assertRaises(ValueError):
            self.professor.titulacao = "Amador"
            
        # Sucesso
        self.professor.titulacao = "Mestre"
        self.assertEqual(self.professor.titulacao, "Mestre")

    def test_lancar_nota_com_permissao(self):
        """Testa o lançamento de nota quando o professor está vinculado à turma."""
        # Primeiro, vincula o professor à turma
        self.professor._turmas_associadas.append(self.turma)
        
        resultado = self.professor.lancar_nota(
            self.turma, self.aluno, "Física", 9.5, "Prova Mensal", date.today()
        )
        
        self.assertIn("sucesso", resultado)
        self.assertEqual(len(self.aluno.notas_recebidas), 1)
        self.assertEqual(self.aluno.notas_recebidas[0][1], 9.5)

    def test_lancar_nota_sem_permissao(self):
        """Garante que professor não lança nota em turma que não leciona."""
        # Não adicionamos a turma ao professor aqui
        resultado = self.professor.lancar_nota(
            self.turma, self.aluno, "Física", 10.0, "Extra", date.today()
        )
        self.assertIn("Erro de permissão", resultado)

    def test_realizar_chamada(self):
        """Verifica se a chamada atualiza o aluno e a turma."""
        self.professor._turmas_associadas.append(self.turma)
        
        lista_presenca = [{"aluno": self.aluno, "presenca": True}]
        resultado = self.professor.realizar_chamada(
            self.turma, date.today(), lista_presenca, "Leis de Newton"
        )
        
        self.assertEqual(resultado, "Chamada e aula registradas com sucesso!")
        self.assertTrue(self.aluno.presencas[0]["presenca"])
        self.assertEqual(len(self.turma.aulas_registradas), 1)

    def test_enviar_material(self):
        """Testa o envio de links de materiais para a turma."""
        self.professor._turmas_associadas.append(self.turma)
        resultado = self.professor.enviar_material(self.turma, "PDF Aula 01", "http://drive.com/aula1")
        
        self.assertIn("sucesso", resultado)
        self.assertEqual(len(self.turma._materiais_postados), 1)
        self.assertEqual(self.turma._materiais_postados[0]["nome"], "PDF Aula 01")

    def test_exibir_perfil_professor(self):
        """Valida a formatação da string de perfil."""
        perfil = self.professor.exibir_perfil()
        self.assertIn("RF-2026-1234", perfil)
        self.assertIn("Doutor", perfil)
        self.assertIn("Física", perfil)

    def test_to_dict_professor(self):
        """Valida a exportação dos dados para dicionário."""
        dados = self.professor.to_dict_especifico()
        self.assertEqual(dados["registro_funcional"], "RF-2026-1234")
        self.assertEqual(dados["titulacao"], "Doutor")
        self.assertEqual(dados["area_atuacao"], "Física")

if __name__ == '__main__':
    unittest.main()