from src.models.usuario import Usuario
from datetime import date
import re

"""
Representa a entidade Professor conforme o diagrama UML.
Herda atributos base de Usuario e adiciona dados funcionais e acadêmicos.
"""
class Professor(Usuario):
    """Construtor da classe Professor."""
    def __init__(self, nome, cpf, email, senha, telefone, data_nascimento,
                 registro_funcional, escola_associada, titulacao, area_atuacao, 
                 salario):
        super().__init__(nome, cpf, email, senha, telefone, data_nascimento)
        
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
        """Função que retorna as permissões da classe Professor"""
        return ["LANCAR_NOTAS", "REGISTRAR_PRESENCA", "POSTAR_CONTEUDO", "ENVIAR_MATERIAL", "VER_TURMAS"]

    def realizar_chamada(self, turma, data, lista_presenca, conteudo_aula):
        """Função para que o professor possa realizar a chamada da turma"""
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
        Implementação do método abstrato da classe Usuario para o Professor.
        Retorna uma string formatada com os dados funcionais e turmas regentes.
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

    def lancar_nota(self, turma, aluno, disciplina, valor):
        """Função para que o professor lance a nota de cada Aluno"""
        if aluno not in turma.alunos_matriculados or turma not in self._turmas_associadas:
            return "Erro de permissão: Vínculo inválido entre professor, turma ou aluno."

        aluno.adicionar_nota(disciplina, valor)
            
    def enviar_material(self, turma, nome_material, link):
        """Função para que o professor envie um material para a turma desejada"""
        if turma not in self.turmas_associadas:
            return "O professor não pertence a esta turma."
        
        else:
            if not hasattr(turma, '_materiais_postados'):
                turma._materiais_postados = []
            turma._materiais_postados.append({"nome": nome_material, "link": link})

        return f"Material '{nome_material}' enviado com sucesso para a turma {turma.nome}!"

    def to_dict(self):
        """
        Exporta os dados do professor em formato de dicionário para persistência.
        Integra os dados da classe base Usuario com os atributos funcionais.
        """
        dados = super().to_dict()

        dados.update({
            "registro_funcional": self.registro_funcional,
            "titulacao": self.titulacao,
            "area_atuacao": self.area_atuacao,
            "salario": self.salario,
            "escola_associada": self.escola_associada,
            "turmas_vinculadas": [turma.nome for turma in self._turmas_associadas]
        })

        return dados