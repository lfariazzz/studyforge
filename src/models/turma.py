from datetime import date
from .professor import Professor
from .aluno import Aluno

class Turma:
    """Representa uma turma escolar.

    Atributos:
        _nome (str): Nome da turma.
        _id_turma (int): Identificador único da turma.
        _capacidade_maxima (int): Limite máximo de alunos.
        _alunos_matriculados (list): Lista de alunos matriculados."""
    
    TURNOS_PERMITIDOS = ["MANHÃ", "TARDE", "NOITE", "INTEGRAL"]

    def __init__(self, id_turma, nome, ano_letivo, id_escola, turno, capacidade_maxima=35):
        self._id_turma = id_turma
        self._nome = nome
        self.ano_letivo = ano_letivo  # Usa o setter para validar no momento da criação
        self._id_escola = id_escola
        self._capacidade_maxima = capacidade_maxima
        self.turno = turno
    
        
        self._professores_regentes = []
        self._alunos_matriculados = []
        self._diario_de_classe = []

    @property
    def nome(self):
        """Retorna o nome da turma."""
        return self._nome

    @nome.setter
    def nome(self, valor):
        """Define o nome da turma.

        Raises:
            ValueError: Se o nome estiver vazio."""
        if not valor or len(valor.strip()) == 0:
            raise ValueError("O nome da turma não pode estar vazio.")
        self._nome = valor

    @property
    def id_turma(self):
        """Retorna o identificador da turma."""
        return self._id_turma

    @property
    def ano_letivo(self):
        """Retorna o ano letivo da turma."""
        return self._ano_letivo

    @ano_letivo.setter
    def ano_letivo(self, valor):
        """Define o ano letivo da turma.

        O valor deve ser um número entre 2000 e 2100.

        Raises:
            ValueError: Se o ano não for válido."""
        try:
            valor_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("Ano letivo deve ser um número válido.")
            
        if valor_int < 2000 or valor_int > 2100:
            raise ValueError("Ano letivo inválido. Deve estar entre 2000 e 2100.")
        self._ano_letivo = valor_int
    
    @property
    def id_escola(self):
        """Retorna o identificador da escola vinculada."""
        return self._id_escola
    
    @property
    def capacidade_maxima(self):
        """Retorna a capacidade máxima da turma."""
        return self._capacidade_maxima
    
    @property
    def alunos_matriculados(self):
        """Retorna a lista de alunos matriculados."""
        return self._alunos_matriculados
    
    @property
    def turno(self):
        """Retorna a turno da turma."""
        return self._turno

    @turno.setter
    def turno(self, valor):
        """Tratamento: Remove espaços e coloca em maiúsculo para evitar erros de digitação"""
        valor_limpo = str(valor).upper().strip()
        
        """Se o usuário digitou "Manhã" com acento, vai padronizar ou validar"""
        
        if valor_limpo not in self.TURNOS_PERMITIDOS:
            raise ValueError(f"Turno '{valor}' inválido. Escolha entre: {self.TURNOS_PERMITIDOS}")
        
        self._turno = valor_limpo

    def adicionar_aluno(self, aluno: Aluno):
        """Adiciona um aluno à turma.

        Bloqueia novas matrículas caso a capacidade máxima seja atingida.

        Args:
            aluno (Aluno): Instância da classe Aluno.

        Returns:
            bool: True se matrícula realizada com sucesso, False caso contrário."""
        if len(self._alunos_matriculados) >= self._capacidade_maxima:
            print(f"Erro: Capacidade máxima de {self._capacidade_maxima} alunos atingida.")
            return False
            
        if aluno not in self._alunos_matriculados:
            self._alunos_matriculados.append(aluno)
            aluno.turma_associada = self
            return True
        return False

    def adicionar_professor(self, professor: Professor):
        """Associa um professor à turma.

        Verifica se o professor já possui alocação no mesmo ano letivo.

        Args:
            professor (Professor): Instância da classe Professor."""
        for t in professor.turmas_associadas:
            if t.ano_letivo == self.ano_letivo and t.id_turma != self._id_turma:
                print(f"Aviso: Professor {professor.nome} já possui alocação no ano {self.ano_letivo}.")
    
        if professor not in self._professores_regentes:
            self._professores_regentes.append(professor)
            if self not in professor.turmas_associadas:
                professor.turmas_associadas.append(self)

    def obter_quadro_horario(self):
        """Retorna um resumo dos professores alocados na turma.

        Returns:
            dict: Nome da turma e lista de professores."""
        nomes = [p.nome for p in self._professores_regentes]
        return {
            "Turma": self._nome,
            "Turno": self.turno,
            "Professores": nomes if nomes else "Nenhum alocado"
        }
    
    def registrar_aula(self, professor, data, conteudo: str):
        """Registra uma aula no diário de classe.

        Valida:
            - Se o professor pertence à turma
            - Se a data é do tipo date
            - Se o conteúdo possui tamanho mínimo

        Args:
            professor (Professor): Professor responsável pela aula.
            data (date): Data da aula.
            conteudo (str): Conteúdo ministrado.

        Returns:
            bool: True se registrada com sucesso, False caso contrário."""
        if professor not in self._professores_regentes:
            print(f"Erro: O professor {professor.nome} não leciona nesta turma.")
            return False
        
        if not isinstance(data, date):
            print("Erro: O campo data deve ser um objeto do tipo date (ex: date.today()).")
            return False

        if not conteudo or len(conteudo.strip()) < 5:
            print("Erro: Conteúdo insuficiente para registro.")
            return False
        
        nova_aula = {
            "data": data,
            "conteudo": conteudo.strip(),
            "id_turma": self._id_turma
        }
        
        self._diario_de_classe.append(nova_aula)
        print(f"Aula registrada com sucesso na Turma {self._id_turma} ({data}).")
        return True
    
    def to_dict(self):
        "Converte os dados da turma para um dicionário."
        return {
            "id_turma": self._id_turma,
            "nome_turma": self._nome,
            "ano_letivo": self._ano_letivo,
            "capacidade_maxima": self._capacidade_maxima,
            "total_alunos": len(self._alunos_matriculados),
            "total_professores": len(self._professores_regentes),
            "id_escola": self._id_escola,
            "turno": self.turno
        }

    def __str__(self):
        """Retorna representação textual da turma."""
        return f"Turma: {self._nome} - {self._ano_letivo} (ID: {self._id_turma})"