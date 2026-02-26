from .turma import Turma
from .aluno import Aluno
from .gestor import Gestor

class Escola:
    """Representa uma unidade escolar pertencente a um município.

    Responsabilidades:
        - Gerenciar turmas vinculadas
        - Controlar professores empregados
        - Administrar verba disponível
        - Monitorar capacidade de infraestrutura
        - Gerar relatórios acadêmicos

    Atributos:
        _nome (str): Nome da escola.
        _endereco (str): Endereço da escola.
        _id_escola (int): Identificador único da escola.
        _gestor_atual (Gestor): Gestor responsável pela escola.
        _verba_disponivel_escola (float): Verba atualmente disponível.
        _id_municipio (int): Identificador do município ao qual pertence.
        _capacidade_infraestrutura (int): Capacidade máxima de alunos da unidade.
        _turmas_existentes (list[Turma]): Lista de turmas cadastradas.
        _professores_empregados (list): Lista de professores vinculados."""
    
    def __init__(self, nome, endereco, id_escola, gestor_atual, verba_disponivel_escola, id_municipio, capacidade_infraestrutura=500):
        self._nome = nome
        self._endereco = endereco
        self._id_escola = id_escola
        self._gestor_atual = gestor_atual # espera a intancia da classe Gestor
        self._verba_disponivel_escola = float(verba_disponivel_escola)
        self._id_municipio = id_municipio
        self._capacidade_infraestrutura = capacidade_infraestrutura # Define o limite físico da unidade

        self._turmas_existentes = []
        self._professores_empregados = []
    
    @property
    def nome(self):
        """Retorna o nome da escola."""
        return self._nome
    
    @property
    def endereco(self):
        """Retorna o endereço da escola."""
        return self._endereco
    
    @property
    def id_escola(self):
        """Retorna o identificador da escola."""
        return self._id_escola
    
    @property
    def gestor_atual(self):
        """Retorna o gestor atual da escola."""
        return self._gestor_atual
    
    @property
    def verba_disponivel_escola(self):
        """Retorna a verba disponível da escola."""
        return self._verba_disponivel_escola
    
    @verba_disponivel_escola.setter
    def verba_disponivel_escola(self, valor):
        """Atualiza a verba disponível.

        Raises:
            ValueError: Se o valor for negativo."""
        if valor < 0:
            raise ValueError("A verba disponível da escola não pode ser negativa.")
        self._verba_disponivel_escola = float(valor)

    @property
    def id_municipio(self):
        """Retorna o identificador do município."""
        return self._id_municipio
    
    @property
    def capacidade_infraestrutura(self):
        """Retorna a capacidade máxima de alunos da unidade."""
        return self._capacidade_infraestrutura
    
    @capacidade_infraestrutura.setter
    def capacidade_infraestrutura(self, valor):
        """Atualiza a capacidade, validando contra o total de alunos atuais."""
        if valor < 0:
            raise ValueError("A capacidade da infraestrutura não pode ser negativa.")
        
        # Cálculo de quantos alunos a escola já possui em todas as turmas
        total_alunos_atuais = sum(len(t.alunos_matriculados) for t in self._turmas_existentes)
        
        if valor < total_alunos_atuais:
            raise ValueError(
                f"Não é possível reduzir a capacidade para {valor}. "
                f"A escola já possui {total_alunos_atuais} alunos matriculados."
            )
            
        self._capacidade_infraestrutura = int(valor)
    
    def gerar_relatorio_frequencia(self):
      """Calcula a média de frequência de todos os alunos de todas as turmas
        
       Returns:
        float: Média geral de frequência (0.0 se não houver alunos)."""
      total_percentual = 0.0
      qtd_alunos = 0
    
      for turma in self._turmas_existentes:
         
        # Percorre os alunos daquela turma específica
        for aluno in turma.alunos_matriculados:
            total_percentual += aluno.frequencia 
            qtd_alunos += 1
    
      # Evita divisão por zero se não houver alunos
      if qtd_alunos == 0:
          return 0.0
        
      media_geral = total_percentual / qtd_alunos   
      return round(media_geral, 2)

    
    def atualizar_locacao(self):
        """Verifica se há professores e turmas cadastradas.

        Simula atualização da alocação de professores.

        Returns:
            bool: True se estrutura válida, False caso contrário."""
        if not self._professores_empregados or not self._turmas_existentes:
            print(" Falha na locação: Sem professores ou turmas cadastradas.")
            return False
            
        print(f" Locação atualizada para {len(self._professores_empregados)} professores.")
        return True
    
    def adicionar_turma(self, turma: Turma):
        """Adiciona uma nova turma à escola.

        Valida se a capacidade total da infraestrutura não será excedida.

        Args:
            turma (Turma): Instância da classe Turma.

        Returns:
            bool: True se adicionada com sucesso, False caso contrário."""
        total_alunos_atuais = sum(len(t.alunos_matriculados) for t in self._turmas_existentes)
        novos_alunos = len(turma.alunos_matriculados)

        # Verifica se a unidade comporta a nova estrutura (soma de alunos vs capacidade total)
        if (total_alunos_atuais + novos_alunos) > self._capacidade_infraestrutura:
            print(f"Erro: A infraestrutura da escola atingiu o limite de {self._capacidade_infraestrutura} alunos.")
            return False

        if turma not in self._turmas_existentes:
            self._turmas_existentes.append(turma)
            return True
        return False
    
    def to_dict(self):
        """Converte os dados da escola em dicionário."""
        return {
            "nome" : self._nome,
            "endereco" : self._endereco,
            "id_escola" : self._id_escola,
            "gestor_atual": self._gestor_atual.nome if self._gestor_atual else None,
            "verba_disponivel_escola" : self._verba_disponivel_escola,
            "id_municipio" : self._id_municipio,
            "capacidade_infraestrutura": self._capacidade_infraestrutura
        }

    def __str__(self):
        """Retorna representação textual da escola."""
        return f"Escola: {self._nome} (ID: {self._id_escola})"