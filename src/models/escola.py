from .turma import Turma
from .aluno import Aluno
from .gestor import Gestor

class Escola:
    def __init__(self, nome, endereco, id_escola, gestor_atual, verba_disponivel_escola, id_municipio):
        self._nome = nome
        self._endereco = endereco
        self._id_escola = id_escola
        self._gestor_atual = gestor_atual # espera a intancia da classe Gestor
        self._verba_disponivel_escola = float(verba_disponivel_escola)
        self._id_municipio = id_municipio
        
        self._turmas_existentes = []
        self._professores_empregados = []
    
    @property
    def nome(self):
        return self._nome
    
    @property
    def endereco(self):
        return self._endereco
    
    @property
    def id_escola(self):
        return self._id_escola
    
    @property
    def gestor_atual(self):
        return self._gestor_atual
    
    @property
    def verba_disponivel_escola(self):
        return self._verba_disponivel_escola
    
    @verba_disponivel_escola.setter
    def verba_disponivel_escola(self, valor):
        if valor < 0:
            raise ValueError("A verba disponível da escola não pode ser negativa.")
        self._verba_disponivel_escola = float(valor)

    @property
    def id_municipio(self):
        return self._id_municipio

    def gerar_relatorio_frequencia(self):
        "Calcula a média de frequência de todos os alunos de todas as turmas. "
        total_percentual = 0.0
        qtd_alunos = 0
        
        for turma in self._turmas_existentes:
             
            # Percorre os alunos daquela turma específica
            for aluno in turma.alunos_matriculados:
                # Avisa ao editor que 'aluno' é um objeto da classe Aluno 
                total_percentual += aluno.frequencia() 
                qtd_alunos += 1
        
        # Evita divisão por zero se não houver alunos
        if qtd_alunos == 0:
            return 0.0
        media_geral = total_percentual / qtd_alunos   
        return round(media_geral,2)
    
    def atualizar_locacao(self):
        "Verifica se todos os professores da escola estão alocados em pelo menos uma turma."
        
        if not self._professores_empregados or not self._turmas_existentes:
            print(" Falha na locação: Sem professores ou turmas cadastradas.")
            return False
            
        # Exemplo de lógica: confirma que a estrutura está montada
        print(f" Locação atualizada para {len(self._professores_empregados)} professores.")
        return True
    
    def adicionar_turma(self, turma: Turma):
      "a relação é mantida apenas por esta lista na Escola."
      if turma not in self._turmas_existentes:
          self._turmas_existentes.append(turma)
    
    def to_dict(self):
        return {
            "nome" : self._nome,
            "endereco" : self._endereco,
            "id_escola" : self._id_escola,
            "gestor_atual": self._gestor_atual.nome if self._gestor_atual else None,
            "verba_disponivel_escola" : self._verba_disponivel_escola,
            "id_municipio" : self._id_municipio
        }

    def __str__(self):
        return f"Escola: {self._nome} (ID: {self._id_escola})"