"""
Para executar este teste, use o comando:
    python -m unittest tests.teste_aluno.TestAluno -v
"""
import unittest
from datetime import date
from src.models.aluno import Aluno

# Mocks simples para simular o comportamento de outras classes sem precisar delas completas
class MockEscola:
    def __init__(self):
        self.nome = "Escola Estadual Teste"
        self._mural_oficial = [
            {"titulo": "Festa Junina", "conteudo": "Haverá pipoca!", "data": "10/06/2026", "autor": "Direção"}
        ]

class MockTurma:
    def __init__(self):
        self.id_turma = 1
        self.nome = "9º Ano A"
        self.alunos_matriculados = []
        self._diario_de_classe = [1, 2, 3, 4]  # Simula 4 aulas dadas
        self.escola = MockEscola()
        self._materiais_postados = [{"nome": "Apostila_V1", "link": "www.download.com"}]

    def adicionar_aluno(self, aluno):
        self.alunos_matriculados.append(aluno)

    def obter_quadro_horario(self):
        return {"Turma": self.nome, "Professores": ["Carlos (Mat)", "Ana (Port)"]}

class TestAluno(unittest.TestCase):

    def setUp(self):
        """Inicializa um aluno e uma turma mock para cada teste."""
        self.turma_mock = MockTurma()
        self.aluno = Aluno(
            nome="João Silva",
            cpf="123.456.789-00",
            email="joao@estudante.com",
            senha="senha_segura",
            telefone="88999999999",
            data_nascimento="01/01/2010",
            turma_associada=self.turma_mock
        )

    def test_geracao_matricula(self):
        """Testa se a matrícula segue o padrão ANO.000.000."""
        ano_atual = str(date.today().year)
        self.assertTrue(self.aluno.id_matricula.startswith(ano_atual))
        self.assertEqual(len(self.aluno.id_matricula), 12)

    def test_adicionar_e_visualizar_notas(self):
        """Testa o fluxo de notas e cálculo de média no boletim."""
        self.aluno.adicionar_nota("Matemática", 8.0)
        self.aluno.adicionar_nota("Matemática", 10.0)
        
        # Testar erro de nota inválida
        with self.assertRaises(ValueError):
            self.aluno.adicionar_nota("História", 11.0)
        
        boletim = self.aluno.visualizar_notas()
        self.assertIn("Matemática", boletim)
        self.assertIn("Média: 9.00", boletim)

    def test_frequencia_e_presenca(self):
        """Testa o registro de presença e o cálculo percentual."""
        # Registrar 3 presenças em 4 aulas totais (da turma_mock)
        self.aluno.registrar_presenca(date(2026, 3, 1), True)
        self.aluno.registrar_presenca(date(2026, 3, 2), True)
        self.aluno.registrar_presenca(date(2026, 3, 3), True)
        
        # Frequência esperada: (3/4) * 100 = 75.0%
        self.assertEqual(self.aluno.frequencia, 75.0)
        
        relatorio = self.aluno.ver_frequencia()
        self.assertIn("75.0%", relatorio)
        self.assertIn("Presente", relatorio)

    def test_ver_horario(self):
        """Testa a integração com o método da turma."""
        horario = self.aluno.ver_horario()
        self.assertIn("9º Ano A", horario)
        self.assertIn("Carlos (Mat)", horario)

    def test_ver_noticias(self):
        """Testa se o aluno consegue ler o mural da escola via turma."""
        noticias = self.aluno.ver_noticias()
        self.assertIn("Festa Junina", noticias)
        self.assertIn("Haverá pipoca!", noticias)

    def test_baixar_material(self):
        """Testa a busca de materiais na turma."""
        sucesso = self.aluno.baixar_material("Apostila_V1")
        falha = self.aluno.baixar_material("Video_Aula")
        
        self.assertIn("Download de 'Apostila_V1' realizado", sucesso)
        self.assertEqual(falha, "Material não encontrado na sua turma")

    def test_exibir_perfil(self):
        """Verifica se a string de perfil contém dados básicos."""
        perfil = self.aluno.exibir_perfil()
        self.assertIn("João Silva", perfil)
        self.assertIn("9º Ano A", perfil)

    def test_to_dict(self):
        """Verifica se a exportação para dicionário está completa."""
        dados = self.aluno.to_dict()
        self.assertEqual(dados["nome"], "João Silva")
        self.assertIn("id_matricula", dados)
        self.assertIn("notas", dados)

if __name__ == '__main__':
    unittest.main()