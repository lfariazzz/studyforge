"""
Para executar este teste, use o comando:
    python -m unittest tests.teste_secretario.TestSecretario -v

Para executar TODOS os testes das 5 classes principais:
    python -m unittest tests.teste_usuario tests.teste_aluno tests.teste_professor tests.teste_gestor tests.teste_secretario -v
"""
import unittest
from datetime import datetime
from src.models.secretario import Secretario
from src.models.municipio import Municipio
from src.models.escola import Escola
from src.models.gestor import Gestor
from src.models.turma import Turma


class TestSecretario(unittest.TestCase):
    """Testes simplificados para a classe Secretário."""

    def setUp(self):
        """Configura os objetos necessários para cada teste."""
        # Criar Município
        self.municipio = Municipio(
            nome="Sao Paulo",
            id_municipio=1,
            estado="SP",
            verba_disponivel_municipio=500000.00,
            nota_de_corte=6.0
        )

        # Criar Secretário com os parâmetros corretos
        self.secretario = Secretario(
            id_usuario=1,
            nome="Fernando Santos",
            cpf="11122233344",
            email="fernando@secretaria.com",
            senha="senha123456",
            telefone="1198765432",
            data_nascimento="20/05/1975",
            municipio_responsavel=self.municipio,
            departamento="EDUCACAO"
        )

        # Criar Gestor com os parâmetros corretos
        self.gestor = Gestor(
            id_usuario=2,
            nome="Carlos Silva",
            cpf="12345678901",
            email="carlos@escola.com",
            senha="senha123456",
            telefone="1198765433",
            data_nascimento="15/05/1980",
            escola_associada=None
        )

        # Criar Escola
        self.escola = Escola(
            nome="Escola Municipal Central",
            endereco="Rua das Flores, 123",
            id_escola=1,
            gestor_atual=self.gestor,
            verba_disponivel_escola=50000.00,
            id_municipio=self.municipio.id_municipio,
            capacidade_infraestrutura=100
        )
        
        # Vincular escola ao gestor
        self.gestor._escola_associada = self.escola
        
        # Adicionar escola ao município
        self.municipio._escolas_situadas = [self.escola]

        # Criar Turma
        self.turma = Turma(
            id_turma=1,
            nome="6 Ano A",
            ano_letivo=2026,
            id_escola=self.escola.id_escola,
            turno="MANHÃ",
            capacidade_maxima=35
        )
        self.escola._turmas_existentes = [self.turma]

    def test_inicializacao_secretario(self):
        """Testa inicialização do Secretário."""
        self.assertEqual(self.secretario.nome, "Fernando Santos")
        self.assertEqual(self.secretario.email, "fernando@secretaria.com")
        self.assertIsNotNone(self.secretario.id_usuario)

    def test_set_municipio_responsavel(self):
        """Testa atribuição de município responsável."""
        novo_municipio = Municipio(
            nome="Rio Janeiro",
            id_municipio=2,
            estado="RJ",
            verba_disponivel_municipio=300000.00,
            nota_de_corte=6.0
        )
        self.secretario._municipio_responsavel = novo_municipio
        self.assertEqual(self.secretario.municipio_responsavel, novo_municipio)

    def test_set_departamento(self):
        """Testa atribuição de departamento."""
        self.secretario._departamento = "FINANCAS"
        self.assertEqual(self.secretario.departamento, "FINANCAS")

    def test_exibir_perfil(self):
        """Testa exibição do perfil do Secretário."""
        perfil = self.secretario.exibir_perfil()
        self.assertIn("PERFIL DO SECRETÁRIO", perfil)
        self.assertIn("Fernando Santos", perfil)
        self.assertIn("Sao Paulo", perfil)
        self.assertIn("EDUCACAO", perfil)

    def test_get_permissao(self):
        """Testa retorno de permissões."""
        permissoes = self.secretario.get_permissao()
        self.assertIsInstance(permissoes, list)
        self.assertIn("ADMINISTRAR_MUNICIPIO", permissoes)
        self.assertIn("GERENCIAR_VERBA_GLOBAL", permissoes)
        self.assertIn("CADASTRAR_GESTORES", permissoes)

    def test_realizar_cadastro_gestor(self):
        """Testa cadastro de gestor em escola."""
        # Criar um novo gestor sem escola associada para o teste
        novo_gestor = Gestor.__new__(Gestor)
        novo_gestor._id = 3
        novo_gestor._nome = "Novo Gestor"
        novo_gestor._cpf = "13579246801"
        novo_gestor._email = "novo@escola.com"
        novo_gestor._senha = "senha123456"
        novo_gestor._telefone = "1198765434"
        novo_gestor._data_nascimento = datetime.strptime("10/03/1985", "%d/%m/%Y")
        novo_gestor._login = False
        novo_gestor._status = True
        novo_gestor._tipo = "GESTOR"
        novo_gestor._escola_associada = None
        
        resultado = self.secretario.realizar_cadastro(novo_gestor, self.escola)
        self.assertIn("Sucesso", resultado)
        self.assertIn(novo_gestor.nome, resultado)
        self.assertIn(self.escola.nome, resultado)

    def test_realizar_cadastro_gestor_fora_municipio(self):
        """Testa que não pode cadastrar gestor em escola fora do município."""
        outro_municipio = Municipio(
            nome="Outro",
            id_municipio=3,
            estado="MG",
            verba_disponivel_municipio=100000.00,
            nota_de_corte=6.0
        )
        
        outra_escola = Escola(
            nome="Outra Escola",
            endereco="Rua Outra, 456",
            id_escola=2,
            gestor_atual=self.gestor,
            verba_disponivel_escola=30000.00,
            id_municipio=outro_municipio.id_municipio,
            capacidade_infraestrutura=50
        )
        
        resultado = self.secretario.realizar_cadastro(self.gestor, outra_escola)
        self.assertIn("Acesso negado", resultado)

    def test_enviar_mensagem_para_escola_especifica(self):
        """Testa envio de mensagem para escola específica."""
        resultado = self.secretario.enviar_mensagem(
            "Aviso da Secretaria",
            "Aula suspensa na segunda-feira.",
            self.escola
        )
        self.assertIn("sucesso", resultado.lower())

    def test_enviar_mensagem_para_rede_toda(self):
        """Testa envio de mensagem para toda a rede municipal."""
        resultado = self.secretario.enviar_mensagem(
            "Comunicado Geral",
            "Novo protocolo de segurança."
        )
        self.assertIsInstance(resultado, str)
        self.assertIn("Comunicado global finalizado", resultado)

    def test_enviar_mensagem_campos_vazios(self):
        """Testa que mensagem não pode ter campos vazios."""
        resultado = self.secretario.enviar_mensagem("", "conteudo")
        self.assertIn("Erro", resultado)

    def test_gerenciar_unidades_adicionar(self):
        """Testa adição de unidade escolar."""
        nova_escola = Escola(
            nome="Escola Nova",
            endereco="Rua Nova, 789",
            id_escola=3,
            gestor_atual=self.gestor,
            verba_disponivel_escola=40000.00,
            id_municipio=self.municipio.id_municipio,
            capacidade_infraestrutura=80
        )
        
        resultado = self.secretario.gerenciar_unidades("ADICIONAR", nova_escola)
        self.assertIn("Sucesso", resultado)
        self.assertIn("Escola Nova", resultado)

    def test_gerenciar_unidades_remover_sem_alunos(self):
        """Testa remoção de unidade escolar vazia."""
        resultado = self.secretario.gerenciar_unidades("REMOVER", self.escola)
        self.assertIn("Sucesso", resultado)

    def test_ver_estatisticas(self):
        """Testa visualização de estatísticas do município."""
        resultado = self.secretario.ver_estatisticas([self.escola])
        self.assertIsInstance(resultado, str)
        self.assertIn(self.municipio.nome, resultado)
        self.assertIn("Escolas", resultado)

    def test_secretario_inativo_nao_pode_agir(self):
        """Testa que Secretário inativo não pode realizar ações."""
        self.secretario._status = False
        resultado = self.secretario.exibir_perfil()
        perfil = resultado
        self.assertIn("Inativa/Suspensa", perfil)

    def test_to_dict(self):
        """Testa exportação para dicionário."""
        dados = self.secretario.to_dict()
        self.assertIsInstance(dados, dict)
        self.assertEqual(dados["nome"], "Fernando Santos")
        self.assertIn("email", dados)
        self.assertIn("cpf", dados)
        self.assertIn("id_usuario", dados)

    def test_get_permissao_contem_todas_esperadas(self):
        """Testa que todas as permissões esperadas estão presentes."""
        permissoes = self.secretario.get_permissao()
        esperadas = [
            "ADMINISTRAR_MUNICIPIO",
            "GERENCIAR_VERBA_GLOBAL",
            "CADASTRAR_GESTORES",
            "MODERAR_DEMANDAS",
            "VISUALIZAR_ESTATISTICAS_REDE"
        ]
        for perm in esperadas:
            self.assertIn(perm, permissoes)


if __name__ == '__main__':
    unittest.main()
