import unittest
from datetime import date
from src.models.escola import Escola
from src.models.turma import Turma
from src.models.aluno import Aluno
Aluno._id = 0
from src.models.gestor import Gestor
from src.models.escola_endereco import Endereco

# ------------------------
# FIXTURES AUXILIARES
# ------------------------
class TestModels(unittest.TestCase):

    def setUp(self):
        self.endereco = Endereco(101, 10, "50000-000", "Rua A", 123, "Centro")
        self.escola = Escola(
            nome="Escola Municipal",
            endereco=self.endereco,
            id_escola=101,
            gestor_atual=None,  # será atribuído depois
            verba_disponivel_escola=10000,
            id_municipio=55,
            capacidade_infraestrutura=50
        )
        self.gestor = Gestor(
            id_usuario=1,
            nome="João",
            cpf="00011122233",
            email="joao@teste.com",
            senha="12345678",
            telefone="99990000000",
            data_nascimento="19/01/2001",
            escola_associada=self.escola
        )

        self.gestor.id = 1

        self.escola._gestor_atual = self.gestor
        

        self.turma = Turma(
            id_turma=1,
            nome="Turma 1",
            ano_letivo=2025,
            id_escola=self.escola.id_escola,
            turno="MANHÃ",
            capacidade_maxima=35
        )
        self.aluno = Aluno(
            id_usuario=2,
            nome="Maria",
            cpf="11122233344",
            email="maria@teste.com",
            senha="12345678",
            telefone="88880000000",
            data_nascimento="03/05/2005"
        )

        self.aluno._id = 2
        self.aluno._notas = {}

    # ------------------------
    # TESTES ESCOLA
    # ------------------------
    def test_escola_propriedades(self):
        self.assertEqual(self.escola.nome, "Escola Municipal")
        self.assertEqual(self.escola.verba_disponivel_escola, 10000.0)

    def test_escola_setter_verba_invalida(self):
        with self.assertRaises(ValueError):
            self.escola.verba_disponivel_escola = -1

    def test_escola_adicionar_turma(self):
        resultado = self.escola.adicionar_turma(self.turma)
        self.assertTrue(resultado)
        self.assertIn(self.turma, self.escola._turmas_existentes)

    def test_escola_relatorio_frequencia_sem_alunos(self):
        self.assertEqual(self.escola.gerar_relatorio_frequencia(), 0.0)

    def test_escola_adicionar_noticia(self):
        self.escola.adicionar_noticia("Título", "Conteúdo", "Autor")
        self.assertEqual(len(self.escola._mural_oficial), 1)

    # ------------------------
    # TESTES TURMA
    # ------------------------
    def test_turma_nome_invalido(self):
        with self.assertRaises(ValueError):
            self.turma.nome = ""

    def test_turma_turno_invalido(self):
        with self.assertRaises(ValueError):
            self.turma.turno = "MADRUGADA"

    def test_turma_adicionar_aluno(self):
        resultado = self.turma.adicionar_aluno(self.aluno)
        self.assertTrue(resultado)
        self.assertIn(self.aluno, self.turma.alunos_matriculados)

    def test_turma_registrar_nota_e_media(self):
        self.turma.registrar_nota_no_sistema(self.aluno, "Matemática", 8.0, "Prova 1", date.today())
        media = self.turma.calcular_media_mensal("Matemática", date.today().month, "Prova 1")
        self.assertEqual(media, 8.0)

    # ------------------------
    # TESTES ALUNO
    # ------------------------
    def test_aluno_matricula_gerada(self):
        self.assertTrue(str(self.aluno.id_matricula).startswith(str(date.today().year)))

    def test_aluno_adicionar_nota_valida(self):
      self.aluno.adicionar_nota("História", 9.0)
      self.assertGreater(len(self.aluno._notas), 0)

    def test_aluno_adicionar_nota_invalida(self):
        with self.assertRaises(ValueError):
            self.aluno.adicionar_nota("História", 11)

    # ------------------------
    # TESTES GESTOR
    # ------------------------
    def test_gestor_exibir_perfil(self):
        perfil = self.gestor.exibir_perfil()
        self.assertIn("PERFIL DO GESTOR", perfil)

    def test_gestor_ver_estatisticas(self):
        self.escola.adicionar_turma(self.turma)
        estatisticas = self.gestor.ver_estatisticas()
        self.assertIn("total_alunos", estatisticas)

    def test_gestor_enviar_mensagem(self):
        resultado = self.gestor.enviar_mensagem("Aviso", "Conteúdo importante")
        self.assertIn("Comunicado", resultado)

    def test_gestor_gerenciar_escola(self):
        resultado = self.gestor.gerenciar_escola(nova_capacidade=100)
        self.assertIn("Sucesso", resultado)

    # ------------------------
    # TESTES ENDERECO
    # ------------------------
    def test_endereco_str(self):
        texto = str(self.endereco)
        self.assertIn("Rua A", texto)

    def test_endereco_to_dict(self):
        d = self.endereco.to_dict()
        self.assertEqual(d["cep"], "50000-000")


if __name__ == "__main__":
    unittest.main()
