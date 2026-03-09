from src.models.usuario import Usuario
from datetime import date
import re

"""
Representa a entidade Professor conforme o diagrama UML.
Herda atributos base de Usuario e adiciona dados funcionais e acadêmicos.
"""
class Professor(Usuario):
    def __init__(self, id_usuario, nome, cpf, email, senha, telefone, data_nascimento,
                 registro_funcional, escola_associada, titulacao, area_atuacao, 
                 salario):
        """
        Inicializa um novo professor no sistema StudyForge.
        
        Args:
            id_usuario (int): Identificador unico do professor.
            nome (str): Nome completo do professor.
            cpf (str): CPF do professor (11 digitos numericos).
            email (str): Endereco de email do professor.
            senha (str): Senha de acesso (minimo 8 caracteres).
            telefone (str): Numero de telefone (10 ou 11 digitos).
            data_nascimento (str): Data de nascimento no formato DD/MM/AAAA.
            registro_funcional (str): Registro funcional no formato RF-AAAA-NNNN.
            escola_associada (Escola): Objeto da escola em que o professor trabalha.
            titulacao (str): Grau academico (Graduado, Especialista, Mestre, Doutor ou Pos-Doutor).
            area_atuacao (str): Area de atuacao/disciplina do professor.
            salario (float): Salario mensaldo professor.
        """
        super().__init__(id_usuario, nome, cpf, email, senha, telefone, data_nascimento, "PROFESSOR")
        
        self.registro_funcional = registro_funcional
        self.escola_associada = escola_associada
        self.titulacao = titulacao
        self.area_atuacao = area_atuacao
        self.salario = salario
        self._turmas_associadas = []

    #-----------------
    #GETTERS E SETTERS
    #-----------------

    @property
    def registro_funcional(self):
        """Retorna o registro funcional (RF) do professor."""
        return self._registro_funcional
    
    @registro_funcional.setter
    def registro_funcional(self, valor):
        """Formata o registro funcional para formato padrão"""
        valor = valor.strip().upper()
        if not re.match(r'^RF-\d{4}-\d{4}$', valor):
            raise ValueError("Erro: RF deve seguir o padrão RF-2026-0001")
        self._registro_funcional = valor
        
    @property
    def titulacao(self):
        """Retorna o grau acadêmico do professor."""
        return self._titulacao
    
    @titulacao.setter
    def titulacao(self, valor):
        """Formata a titulação para formato padrão"""
        validas = ["Graduado", "Especialista", "Mestre", "Doutor", "Pós-Doutor"]
        valor_formatado = valor.strip().title()
        if valor_formatado not in validas:
            raise ValueError(f"Erro: Titulação deve ser uma de: {', '.join(validas)}")
        self._titulacao = valor_formatado

    @property
    def salario(self):
        """Retorna o salário do professor."""
        return self._salario
    
    @salario.setter
    def salario(self, valor):
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("Erro: O salário deve ser um número positivo.")
        self._salario = float(valor)

    @property
    def turmas_associadas(self):
        """Retorna a lista. Não permitimos sobrescrever a lista inteira por fora."""
        return self._turmas_associadas

    #-------
    #MÉTODOS
    #-------

    def get_permissao(self):
        """
        Retorna as permissoes do professor no sistema.
        
        Returns:
            list: Lista contendo as permissoes do professor:
                  - LANCAR_NOTAS: Lancamento de notas para alunos
                  - REGISTRAR_PRESENCA: Registro de frequencia dos alunos
                  - POSTAR_CONTEUDO: Publicacao de conteudo e aulas
                  - ENVIAR_MATERIAL: Envio de materiais didaticos
                  - VER_TURMAS: Visualizacao das turmas associadas
        """
        return ["LANCAR_NOTAS", "REGISTRAR_PRESENCA", "POSTAR_CONTEUDO", "ENVIAR_MATERIAL", "VER_TURMAS"]

    def realizar_chamada(self, turma, data, lista_presenca, conteudo_aula):
        """
        Registra a chamada (frequencia) e a aula para a turma.
        
        Permite que o professor registre a presenca/falta dos alunos em uma aula
        e documente o conteudo apresentado.
        
        Args:
            turma (Turma): Objeto da turma na qual a aula ocorreu.
            data (date): Data da aula.
            lista_presenca (list): Lista de dicionarios com chaves:
                                   - 'aluno': Objeto do aluno
                                   - 'presenca': Booleano (True se presente, False se faltou)
            conteudo_aula (str): Descricao do conteudo ministrado na aula.
        
        Returns:
            str: Mensagem de sucesso ou erro sobre o registro da chamada.
        """
        if turma not in self.turmas_associadas:
            return "Professor não pertence a esta turma."
        
        for registro in lista_presenca:
            aluno_objeto = registro.get("aluno")
            status_vaga = registro.get("presenca")
            
            aluno_objeto.registrar_presenca(data, status_vaga) 

        turma.registrar_aula(self, data, conteudo_aula)
        return "Chamada e aula registradas com sucesso!"

    def exibir_perfil(self):
        """
        Exibe o perfil completo do professor.
        
        Implementacao do metodo abstrato da classe Usuario que retorna uma string
        formatada com os dados funcionais do professor, incluindo registro funcional,
        titulacao, area de atuacao, email e turmas regentes.
        
        Returns:
            str: String formatada contendo informacoes do perfil do professor.
        """
        nomes_turmas = [turma.nome for turma in self._turmas_associadas]
        turmas_str = ", ".join(nomes_turmas) if nomes_turmas else "Nenhuma turma alocada"
        status_conta = "Ativa" if self._status else "Inativa"

        return (
            f"\n" + "="*40 + "\n"
            f"          PERFIL DO PROFESSOR\n"
            f"="*40 + "\n"
            f"Nome: {self.nome}\n"
            f"RF: {self.registro_funcional}\n"
            f"Titulação: {self.titulacao}\n"
            f"Área: {self.area_atuacao}\n"
            f"E-mail: {self.email}\n"
            f"Turmas: {turmas_str}\n"
            f"Status: {status_conta}\n"
            f"="*40
        )

    def lancar_nota(self, turma, aluno, disciplina, valor, tipo, data_prova):
        """
        Lanca uma nota para um aluno em uma disciplina especifica.
        
        Permite que o professor registre notas dos alunos em sua turma,
        atualizando tanto o boletim do aluno quanto o sistema da turma.
        
        Args:
            turma (Turma): Objeto da turma do aluno.
            aluno (Aluno): Objeto do aluno que recebera a nota.
            disciplina (str): Nome da disciplina.
            valor (float): Valor da nota (0 a 10).
            tipo (str): Tipo de avaliacao (ex: Prova, Trabalho, Participacao).
            data_prova (date): Data da avaliacao.
        
        Returns:
            str: Mensagem de sucesso ou erro sobre o lancamento da nota.
        """
        if aluno not in turma.alunos_matriculados or turma not in self._turmas_associadas:
            return "Erro de permissão: Vínculo inválido entre professor, turma ou aluno."

        aluno.adicionar_nota(disciplina, valor)

        turma.registrar_nota_no_sistema(aluno, disciplina, valor, tipo, data_prova)
        
        return f"Nota lançada com sucesso para {aluno.nome}."
            
    def enviar_material(self, turma, nome_material, link):
        """
        Envia um material didatico para uma turma.
        
        Permite que o professor compartilhe materiais (slides, PDFs, videos, etc)
        com os alunos de uma turma especifica.
        
        Args:
            turma (Turma): Objeto da turma que recebera o material.
            nome_material (str): Nome descritivo do material.
            link (str): URL ou caminho para acessar o material.
        
        Returns:
            str: Mensagem de sucesso ou erro sobre o envio do material.
        """
        if turma not in self.turmas_associadas:
            return "O professor não pertence a esta turma."
        
        else:
            if not hasattr(turma, '_materiais_postados'):
                turma._materiais_postados = []
            turma._materiais_postados.append({"nome": nome_material, "link": link})

        return f"Material '{nome_material}' enviado com sucesso para a turma {turma.nome}!"

    def to_dict_especifico(self):
        """
        Exporta os dados especificos do professor em formato de dicionario.
        
        Retorna um dicionario contendo os atributos funcionais e academicos
        do professor para persistencia em banco de dados ou serializacao JSON.
        
        Returns:
            dict: Dicionario com id_usuario, salario, titulacao, area_atuacao,
                  registro_funcional e id_escola.
        """
        return{
            "id_usuario": self.id_usuario,
            "salario": self.salario,
            "titulacao": self.titulacao,
            "area_atuacao": self.area_atuacao,
            "registro_funcional": self.registro_funcional,
            "escola_associada": self.escola_associada.id_escola if self.escola_associada else None 
        }