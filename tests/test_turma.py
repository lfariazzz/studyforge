import unittest
from datetime import date
from src.models.turma import Turma
from src.models.aluno import Aluno
from src.models.professor import Professor


class TestTurma(unittest.TestCase):
    def setUp(self):
     # PATCH para corrigir atributo esperado pela classe Aluno
     Aluno._id = property(lambda self: self._id_usuario)
     
     self.turma = Turma(
        id_turma=1,
        nome="9º Ano A",
        ano_letivo=2025,
        turno="MANHÃ",
        id_escola=1,
        capacidade_maxima=2
     )

     self.aluno1 = Aluno(
       id_usuario=1,
       nome="Maria",
       cpf="12345678901",
       email="maria@teste.com",
       senha="senha123!",
       telefone="9999999999",
       data_nascimento="05/05/2005",
       matricula="2025001"
    )

     self.aluno2 = Aluno(
       id_usuario=2,
       nome="João",
       cpf="98765432100",
       email="joao@teste.com",
       senha="senha123!",
       telefone="9888888888",
       data_nascimento="10/06/2005",
       matricula="2025002"
    )

     self.professor = Professor(
        id_usuario=3,
        nome="Carlos",
        cpf="33333333333",
        email="carlos@teste.com",
        senha="01234567!",
        telefone="7777777777",
        data_nascimento="19/01/2001",
        registro_funcional="RF-2026-0001",
        escola_associada=1,
        titulacao="Mestre",
        area_atuacao="Matemática",
        salario=3500.0
    )
     
    # ------------------------
    # Testes de propriedades
    # ------------------------
    def test_nome_valido(self):
        self.assertEqual(self.turma.nome, "9º Ano A")

    def test_nome_invalido(self):
        with self.assertRaises(ValueError):
            self.turma.nome = ""

    def test_ano_letivo_valido(self):
        self.assertEqual(self.turma.ano_letivo, 2025)

    def test_ano_letivo_invalido(self):
        with self.assertRaises(ValueError):
            self.turma.ano_letivo = 1800

    def test_turno_valido(self):
        self.assertEqual(self.turma.turno, "MANHÃ")

    def test_turno_invalido(self):
        with self.assertRaises(ValueError):
            self.turma.turno = "MADRUGADA"

    # ------------------------
    # Testes de métodos
    # ------------------------
    def test_adicionar_aluno_sucesso(self):
        resultado = self.turma.adicionar_aluno(self.aluno1)
        self.assertTrue(resultado)
        self.assertIn(self.aluno1, self.turma.alunos_matriculados)

    def test_adicionar_aluno_capacidade_excedida(self):
        self.turma.adicionar_aluno(self.aluno1)
        self.turma.adicionar_aluno(self.aluno2)
        aluno_extra = Aluno(
            id_usuario=4,
            nome="Ana",
            cpf="44455566677",
            email="ana@teste.com",
            senha="senha123!",
            telefone="6666666666",
            data_nascimento="07/07/2007"
        )
        self.turma.adicionar_aluno(aluno_extra)
        
        resultado = self.turma.adicionar_aluno(aluno_extra)
        self.assertFalse(resultado)

    def test_adicionar_professor(self):
        self.turma.adicionar_professor(self.professor)
        quadro = self.turma.obter_quadro_horario()
        self.assertIn("Carlos", quadro["Professores"])

    def test_registrar_nota_e_calcular_media(self):
        self.turma.adicionar_aluno(self.aluno1)
        self.turma.registrar_nota_no_sistema(self.aluno1, "Matemática", 8.0, "Prova 1", date.today())
        media = self.turma.calcular_media_mensal("Matemática", date.today().month, "Prova 1")
        self.assertEqual(media, 8.0)

    def test_registrar_aula_sucesso(self):
        self.turma.adicionar_professor(self.professor)
        resultado = self.turma.registrar_aula(self.professor, date.today(), "Conteúdo da aula")
        self.assertTrue(resultado)
        self.assertEqual(len(self.turma._diario_de_classe), 1)

    def test_registrar_aula_professor_invalido(self):
        resultado = self.turma.registrar_aula(self.professor, date.today(), "Conteúdo")
        self.assertFalse(resultado)

    def test_registrar_aula_conteudo_invalido(self):
        self.turma.adicionar_professor(self.professor)
        resultado = self.turma.registrar_aula(self.professor, date.today(), "Oi")
        self.assertFalse(resultado)

    def test_to_dict(self):
        d = self.turma.to_dict()
        self.assertEqual(d["nome"], "9º Ano A")

    def test_str(self):
        texto = str(self.turma)
        self.assertIn("Turma: 9º Ano A", texto)


if __name__ == "__main__":
    unittest.main()