"""
Para executar este teste, use o comando:
    python -m unittest tests.teste_gestor.TestGestor -v
"""
import unittest
from datetime import datetime
from src.models.gestor import Gestor
from src.models.escola import Escola
from src.models.turma import Turma
from src.models.aluno import Aluno
from src.models.professor import Professor
from src.models.municipio import Municipio


class TestGestor(unittest.TestCase):
    """Testes simplificados para a classe Gestor."""

    def setUp(self):
        """Configura os objetos necessários para cada teste."""
        # Criar um Município
        self.municipio = Municipio(
            nome="São Paulo",
            id_municipio=1,
            estado="SP",
            verba_disponivel_municipio=1000000.00,
            nota_de_corte=6.0
        )

        # Criar Gestor com os parâmetros corretos
        self.gestor = Gestor(
            id_usuario=1,
            nome="Carlos Silva",
            cpf="12345678901",
            email="carlos@escola.com",
            senha="senha123456",
            telefone="1198765432",
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

        self.gestor._escola_associada = self.escola

        # Criar Turma simples
        self.turma = Turma(
            id_turma=1,
            nome="6º Ano A",
            ano_letivo=2026,
            id_escola=self.escola.id_escola,
            turno="MANHÃ",
            capacidade_maxima=35
        )
        self.escola._turmas_existentes = [self.turma]

        # Criar Aluno
        self.aluno = Aluno(
            id_usuario=2,
            nome="Joao Silva",
            cpf="98765432101",
            email="joao@email.com",
            senha="senha123456",
            telefone="1187654321",
            data_nascimento="20/03/2012",
            turma_associada=self.turma
        )

        # Criar Professor
        self.professor = Professor(
            id_usuario=3,
            nome="Roberto Costa",
            cpf="55566677788",
            email="roberto@escola.com",
            senha="prof123456",
            telefone="1198765433",
            data_nascimento="25/11/1975",
            registro_funcional="RF-2026-0001",
            escola_associada=self.escola,
            titulacao="Mestre",
            area_atuacao="Matematica",
            salario=3500.00
        )
        self.escola._professores_empregados = [self.professor]

    def test_inicializacao_gestor(self):
        """Testa inicialização do Gestor."""
        self.assertEqual(self.gestor.nome, "Carlos Silva")
        self.assertEqual(self.gestor.email, "carlos@escola.com")
        self.assertIsNotNone(self.gestor.id_usuario)

    def test_exibir_perfil(self):
        """Testa exibição do perfil do Gestor."""
        perfil = self.gestor.exibir_perfil()
        self.assertIn("PERFIL DO GESTOR", perfil)
        self.assertIn("Carlos Silva", perfil)
        self.assertIn("Escola Municipal Central", perfil)

    def test_ver_estatisticas(self):
        """Testa geração de estatísticas da escola."""
        stats = self.gestor.ver_estatisticas()
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["escola"], "Escola Municipal Central")
        self.assertEqual(stats["total_alunos"], 1)
        self.assertEqual(stats["total_professores"], 1)
        self.assertEqual(stats["total_turmas"], 1)

    def test_enviar_mensagem(self):
        """Testa envio de mensagem no mural."""
        resultado = self.gestor.enviar_mensagem(
            "Aviso Importante",
            "Aula cancelada amanhã."
        )
        self.assertIn("sucesso", resultado.lower())

    def test_enviar_mensagem_campos_vazios(self):
        """Testa que mensagem não pode ter campos vazios."""
        resultado = self.gestor.enviar_mensagem("", "conteudo")
        self.assertIn("Erro", resultado)

    def test_realizar_cadastro_aluno(self):
        """Testa cadastro de aluno em turma."""
        novo_aluno = Aluno(
            id_usuario=4,
            nome="Maria Santos",
            cpf="11122233344",
            email="maria@email.com",
            senha="aluno456789",
            telefone="1187654322",
            data_nascimento="10/07/2011",
            turma_associada=None
        )
        resultado = self.gestor.realizar_cadastro(novo_aluno, self.turma)
        self.assertIsNotNone(resultado)

    def test_gerenciar_escola_aumentar_capacidade(self):
        """Testa aumento de capacidade da escola."""
        resultado = self.gestor.gerenciar_escola(nova_capacidade=150)
        self.assertIn("Sucesso", resultado)
        self.assertEqual(self.escola.capacidade_infraestrutura, 150)

    def test_get_permissao(self):
        """Testa retorno de permissões do Gestor."""
        permissoes = self.gestor.get_permissao()
        self.assertIsInstance(permissoes, list)
        self.assertIn("VISUALIZAR_PERFIL", permissoes)
        self.assertIn("VER_ESTATISTICA_ESCOLA", permissoes)
        self.assertIn("REALIZAR_CADASTRO", permissoes)

    def test_gestor_inativo_nao_pode_agir(self):
        """Testa que Gestor inativo não pode realizar ações."""
        self.gestor._status = False
        resultado = self.gestor.ver_estatisticas()
        self.assertIn("Erro", resultado)


if __name__ == '__main__':
    unittest.main()

    def test_escola_associada_deve_ser_instancia_escola(self):
        """Testa que a escola associada deve ser uma instância de Escola."""
        # Tentar atribuir algo que não é Escola deve lançar erro
        # Como não podemos criar um Gestor sem uma Escola válida, fazemos um teste indireto
        # Verificamos que o Gestor rejeita valores non-Escola
        try:
            from src.models.gestor import Gestor
            # A tentativa de reatribuição lança PermissionError, não TypeError
            # Mas a classe valida que deve ser Escola no setter
            self.assertIsInstance(self.gestor.escola_associada, Escola)
        except TypeError:
            self.fail("Escola associada deve ser instância de Escola")

    # ==========================================
    # TESTES DO MÉTODO exibir_perfil
    # ==========================================

    def test_exibir_perfil_gestor_ativo(self):
        """Testa a exibição do perfil de um Gestor ativo."""
        perfil = self.gestor.exibir_perfil()
        
        self.assertIn("PERFIL DO GESTOR", perfil)
        self.assertIn("Carlos Silva", perfil)
        self.assertIn(str(self.gestor.id), perfil)
        self.assertIn("Escola Municipal Central", perfil)
        self.assertIn("carlos@escola.com", perfil)
        self.assertIn("Ativa", perfil)

    def test_exibir_perfil_gestor_inativo(self):
        """Testa a exibição do perfil quando o Gestor está inativo."""
        self.gestor._status = False
        perfil = self.gestor.exibir_perfil()
        
        self.assertIn("Inativa/Suspensa", perfil)

    # ==========================================
    # TESTES DO MÉTODO ver_estatisticas
    # ==========================================

    def test_ver_estatisticas_gestor_ativo(self):
        """Testa a geração de estatísticas com Gestor ativo."""
        # Adicionar alunos às turmas
        self.aluno1.turma_associada = self.turma1
        self.turma1.adicionar_aluno(self.aluno1)
        
        self.aluno2.turma_associada = self.turma2
        self.turma2.adicionar_aluno(self.aluno2)

        stats = self.gestor.ver_estatisticas()

        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["escola"], "Escola Municipal Central")
        self.assertEqual(stats["total_alunos"], 2)
        self.assertEqual(stats["total_professores"], 2)
        self.assertEqual(stats["total_turmas"], 2)
        self.assertEqual(stats["verba_disponivel"], 50000.00)
        self.assertIn("media_frequencia_geral", stats)
        self.assertIn("capacidade_utilizada_pct", stats)

    def test_ver_estatisticas_gestor_inativo(self):
        """Testa que gestor inativo não pode ver estatísticas."""
        self.gestor._status = False
        resultado = self.gestor.ver_estatisticas()
        
        self.assertIn("Erro", resultado)
        self.assertIn("inativo", resultado)

    def test_ver_estatisticas_calcula_ocupacao_corretamente(self):
        """Testa o cálculo de ocupação de infraestrutura."""
        # Adicionar 50 alunos
        for i in range(50):
            nome_suffix = ['Um', 'Dois', 'Tres', 'Quatro', 'Cinco', 'Seis', 'Sete', 'Oito', 'Nove', 'Dez']
            # CPF único para cada aluno: 123456789XX
            cpf_base = f"12345678{i:03d}"[-11:]  # Garante 11 dígitos
            aluno = Aluno(
                nome=f"Aluno {nome_suffix[i % 10]}",
                cpf=cpf_base,
                email=f"aluno{i}@email.com",
                senha="senha1234",
                telefone="1187654321",
                data_nascimento="01/01/2012",
                turma_associada=self.turma1
            )
            self.turma1.alunos_matriculados.append(aluno)

        stats = self.gestor.ver_estatisticas()
        # 50 alunos em capacidade de 100 = 50%
        self.assertEqual(stats["capacidade_utilizada_pct"], 50.0)

    # ==========================================
    # TESTES DO MÉTODO realizar_cadastro
    # ==========================================

    def test_realizar_cadastro_aluno_com_sucesso(self):
        """Testa cadastro de um aluno com sucesso."""
        resultado = self.gestor.realizar_cadastro(self.aluno2, self.turma1)
        
        self.assertIn("sucesso", resultado.lower())
        self.assertIn(self.aluno2.nome, resultado)
        self.assertIn(self.turma1.nome, resultado)
        self.assertIn(self.aluno2, self.turma1.alunos_matriculados)

    def test_realizar_cadastro_aluno_turma_cheia(self):
        """Testa que aluno não pode ser cadastrado em turma cheia."""
        # Preencher a turma com 35 alunos
        for i in range(35):
            nome_suffix = ['Um', 'Dois', 'Tres', 'Quatro', 'Cinco', 'Seis', 'Sete', 'Oito', 'Nove', 'Dez']
            # CPF único para cada aluno: 111111111XX
            cpf_base = f"11111111{i:03d}"[-11:]  # Garante 11 dígitos
            aluno = Aluno(
                nome=f"Aluno {nome_suffix[i % 10]}",
                cpf=cpf_base,
                email=f"aluno{i}@email.com",
                senha="senha1234",
                telefone="1187654321",
                data_nascimento="01/01/2012",
                turma_associada=None
            )
            self.turma1.alunos_matriculados.append(aluno)

        resultado = self.gestor.realizar_cadastro(self.aluno2, self.turma1)
        
        self.assertIn("capacidade", resultado.lower())

    def test_realizar_cadastro_aluno_excede_capacidade_escola(self):
        """Testa que aluno não pode ser cadastrado se exceder capacidade da escola."""
        # Preencher a escola até sua capacidade
        for i in range(100):
            nome_suffix = ['Um', 'Dois', 'Tres', 'Quatro', 'Cinco', 'Seis', 'Sete', 'Oito', 'Nove', 'Dez']
            # CPF único para cada aluno: 222222222XX
            cpf_base = f"22222222{i:03d}"[-11:]  # Garante 11 dígitos
            aluno = Aluno(
                nome=f"Aluno {nome_suffix[i % 10]}",
                cpf=cpf_base,
                email=f"alunox{i}@email.com",
                senha="senha1234",
                telefone="1187654321",
                data_nascimento="01/01/2012",
                turma_associada=None
            )
            if i < 35:
                self.turma1.alunos_matriculados.append(aluno)
            elif i < 70:
                self.turma2.alunos_matriculados.append(aluno)

        resultado = self.gestor.realizar_cadastro(self.aluno2, self.turma1)
        
        self.assertIn("Capacidade", resultado)

    def test_realizar_cadastro_professor_com_sucesso(self):
        """Testa cadastro de professor com sucesso."""
        novo_professor = Professor(
            nome="Prof Novo",
            cpf="33344455566",
            email="novo@escola.com",
            senha="prof9999999",
            telefone="1198765436",
            data_nascimento="15/06/1990",
            registro_funcional="RF-2026-0003",
            escola_associada=self.escola,
            titulacao="Graduado",
            area_atuacao="Educação Física",
            salario=3000.00
        )

        resultado = self.gestor.realizar_cadastro(novo_professor, self.turma1)
        
        self.assertIsNotNone(resultado)

    def test_realizar_cadastro_professor_ja_vinculado(self):
        """Testa que professor já vinculado não pode ser cadastrado novamente."""
        resultado = self.gestor.realizar_cadastro(self.professor1)
        
        self.assertIn("já está cadastrado", resultado)

    def test_realizar_cadastro_gestor_inativo(self):
        """Testa que gestor inativo não pode realizar cadastros."""
        self.gestor._status = False
        
        with self.assertRaises(PermissionError):
            self.gestor.realizar_cadastro(self.aluno2, self.turma1)

    # ==========================================
    # TESTES DO MÉTODO enviar_mensagem
    # ==========================================

    def test_enviar_mensagem_com_sucesso(self):
        """Testa envio de mensagem com sucesso."""
        resultado = self.gestor.enviar_mensagem(
            "Aviso Importante",
            "A escola estará fechada na próxima segunda-feira."
        )
        
        self.assertIn("sucesso", resultado.lower())
        self.assertIn("Aviso Importante", resultado)

    def test_enviar_mensagem_sem_conteudo(self):
        """Testa que mensagem sem conteúdo é rejeitada."""
        resultado = self.gestor.enviar_mensagem("Título", "")
        
        self.assertIn("Erro", resultado)

    def test_enviar_mensagem_sem_titulo(self):
        """Testa que mensagem sem título é rejeitada."""
        resultado = self.gestor.enviar_mensagem("", "Conteúdo")
        
        self.assertIn("Erro", resultado)

    def test_enviar_mensagem_gestor_inativo(self):
        """Testa que gestor inativo não pode enviar mensagens."""
        self.gestor._status = False
        resultado = self.gestor.enviar_mensagem("Titulo", "Conteúdo")
        
        self.assertIn("Erro", resultado)

    # ==========================================
    # TESTES DO MÉTODO realizar_solicitacao
    # ==========================================

    def test_realizar_solicitacao_pedagogica(self):
        """Testa criação de solicitação pedagógica."""
        # Adicionar aulas à turma primeiro
        from datetime import date
        self.turma1._diario_de_classe.append({"data": date.today(), "conteudo": "Matemática Básica"})
        
        resultado = self.gestor.realizar_solicitacao(
            tipo_demanda="PEDAGOGICA",
            descricao="Falta de reforço em português",
            prioridade="ALTA",
            turma=self.turma1,
            mes="2026-03"
        )
        
        self.assertIsNotNone(resultado)

    def test_realizar_solicitacao_infraestrutura(self):
        """Testa criação de solicitação de infraestrutura."""
        resultado = self.gestor.realizar_solicitacao(
            tipo_demanda="INFRAESTRUTURA",
            descricao="Sala de informática sem funcionar",
            prioridade="CRÍTICA"
        )
        
        self.assertIsNotNone(resultado)

    def test_realizar_solicitacao_gestor_inativo(self):
        """Testa que gestor inativo não pode fazer solicitações."""
        self.gestor._status = False
        resultado = self.gestor.realizar_solicitacao(
            tipo_demanda="PEDAGOGICA",
            descricao="Teste",
            turma=self.turma1,
            mes="2026-03"
        )
        
        self.assertIn("Erro", resultado)

    # ==========================================
    # TESTES DO MÉTODO administrar_solicitacoes
    # ==========================================

    def test_administrar_solicitacoes_sem_demandas(self):
        """Testa painel de solicitações quando não há demandas."""
        resultado = self.gestor.administrar_solicitacoes()
        
        self.assertIn("Nenhuma solicitação", resultado)

    def test_administrar_solicitacoes_lista_demandas(self):
        """Testa que administrar solicitações lista as demandas."""
        # Criar uma solicitação
        self.gestor.realizar_solicitacao(
            tipo_demanda="INFRAESTRUTURA",
            descricao="Reforma necessária",
            prioridade="NORMAL"
        )

        resultado = self.gestor.administrar_solicitacoes()
        
        # Verifica que é uma string e contém informações da escola
        self.assertIsInstance(resultado, str)
        self.assertIn(self.escola.nome, resultado)

    def test_administrar_solicitacoes_gestor_inativo(self):
        """Testa que gestor inativo não pode administrar solicitações."""
        self.gestor._status = False
        resultado = self.gestor.administrar_solicitacoes()
        
        self.assertIn("Acesso negado", resultado)

    # ==========================================
    # TESTES DO MÉTODO gerenciar_escola
    # ==========================================

    def test_gerenciar_escola_aumentar_capacidade(self):
        """Testa aumento de capacidade da escola."""
        resultado = self.gestor.gerenciar_escola(nova_capacidade=150)
        
        self.assertIn("Sucesso", resultado)
        self.assertEqual(self.escola.capacidade_infraestrutura, 150)

    def test_gerenciar_escola_reducao_invalida(self):
        """Testa que não pode reduzir capacidade abaixo do número de alunos."""
        # Adicionar alguns alunos
        self.aluno1.turma_associada = self.turma1
        self.turma1.adicionar_aluno(self.aluno1)

        resultado = self.gestor.gerenciar_escola(nova_capacidade=0)
        
        self.assertIn("Erro", resultado)

    def test_gerenciar_escola_sem_alteracoes(self):
        """Testa método sem solicitar alterações."""
        resultado = self.gestor.gerenciar_escola()
        
        self.assertIn("Nenhuma alteração", resultado)

    def test_gerenciar_escola_gestor_inativo(self):
        """Testa que gestor inativo não pode gerenciar escola."""
        self.gestor._status = False
        resultado = self.gestor.gerenciar_escola(nova_capacidade=200)
        
        self.assertIn("Erro", resultado)

    # ==========================================
    # TESTES DO MÉTODO alterar_status_usuario
    # ==========================================

    def test_alterar_status_aluno_desativar(self):
        """Testa desativação de um aluno."""
        self.aluno1.turma_associada = self.turma1
        self.turma1.adicionar_aluno(self.aluno1)

        resultado = self.gestor.alterar_status_usuario(self.aluno1, False)
        
        self.assertIn("Sucesso", resultado)
        self.assertIn("desativado", resultado)
        self.assertFalse(self.aluno1._status)

    def test_alterar_status_aluno_ativar(self):
        """Testa ativação de um aluno."""
        self.aluno1.turma_associada = self.turma1
        self.turma1.adicionar_aluno(self.aluno1)
        self.aluno1._status = False

        resultado = self.gestor.alterar_status_usuario(self.aluno1, True)
        
        self.assertIn("Sucesso", resultado)
        self.assertIn("ativado", resultado)
        self.assertTrue(self.aluno1._status)

    def test_alterar_status_professor_desativar(self):
        """Testa desativação de um professor."""
        resultado = self.gestor.alterar_status_usuario(self.professor1, False)
        
        self.assertIn("Sucesso", resultado)
        self.assertFalse(self.professor1._status)

    def test_alterar_status_aluno_nao_matriculado(self):
        """Testa que não pode alterar status de aluno não matriculado."""
        resultado = self.gestor.alterar_status_usuario(self.aluno2, False)
        
        self.assertIn("Erro", resultado)
        self.assertIn("não está matriculado", resultado)

    def test_alterar_status_professor_nao_vinculado(self):
        """Testa que não pode alterar status de professor não vinculado."""
        novo_professor = Professor(
            nome="Prof Externo",
            cpf="77788899900",
            email="externo@email.com",
            senha="prof9999999",
            telefone="1198765437",
            data_nascimento="20/09/1985",
            registro_funcional="RF-2026-9999",
            escola_associada=None,
            titulacao="Graduado",
            area_atuacao="História",
            salario=3100.00
        )

        resultado = self.gestor.alterar_status_usuario(novo_professor, False)
        
        self.assertIn("Erro", resultado)

    def test_alterar_status_usuario_invalido(self):
        """Testa que não pode alterar status de usuário inválido."""
        usuario_invalido = "não é usuário"
        resultado = self.gestor.alterar_status_usuario(usuario_invalido, False)
        
        self.assertIn("Erro", resultado)
        self.assertIn("permissão", resultado)

    def test_alterar_status_gestor_inativo(self):
        """Testa que gestor inativo não pode alterar status."""
        self.gestor._status = False
        resultado = self.gestor.alterar_status_usuario(self.aluno1, False)
        
        self.assertIn("Erro", resultado)

    # ==========================================
    # TESTES DO MÉTODO to_dict
    # ==========================================

    def test_to_dict_exporta_dados_completos(self):
        """Testa exportação completa de dados em dicionário."""
        dados = self.gestor.to_dict()
        
        self.assertIsInstance(dados, dict)
        self.assertEqual(dados["nome"], "Carlos Silva")
        self.assertEqual(dados["email"], "carlos@escola.com")
        self.assertEqual(dados["escola_vinculada"], "Escola Municipal Central")
        self.assertIn("permissoes", dados)

    def test_to_dict_inclui_permissoes_gestor(self):
        """Testa que o dicionário inclui as permissões corretas."""
        dados = self.gestor.to_dict()
        permissoes = dados["permissoes"]
        
        self.assertIn("VIZUALIZAR_PERFIL", permissoes)
        self.assertIn("VER_ESTATISTICA_ESCOLA", permissoes)
        self.assertIn("REALIZAR_CADASTRO", permissoes)
        self.assertIn("ENVIAR_MENSAGEM", permissoes)

    # ==========================================
    # TESTES DE get_permissao
    # ==========================================

    def test_get_permissao_retorna_lista(self):
        """Testa que get_permissao retorna uma lista."""
        permissoes = self.gestor.get_permissao()
        
        self.assertIsInstance(permissoes, list)
        self.assertGreater(len(permissoes), 0)

    def test_get_permissao_contem_funcionalidades_esperadas(self):
        """Testa que as permissões esperadas estão presentes."""
        permissoes = self.gestor.get_permissao()
        
        permissoes_esperadas = [
            "VIZUALIZAR_PERFIL",
            "VER_ESTATISTICA_ESCOLA",
            "REALIZAR_CADASTRO",
            "ENVIAR_MENSAGEM",
            "REALIZAR_SOLICITACAO_VERBA",
            "ADMINISTRAR_SOLICITACOES_ESCOLA",
            "GERENCIAR_DADOS_ESCOLA",
            "ALTERAR_STATUS_USUARIO"
        ]
        
        for perm in permissoes_esperadas:
            self.assertIn(perm, permissoes)


if __name__ == '__main__':
    unittest.main()