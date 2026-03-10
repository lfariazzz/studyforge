"""
Classe criada para fazer receber os dados do Banco de Dados e se conectar com AvaliadorFrequencia, que por sua vez
vai se conecta com DemandaPedagogica 
"""

class Nota: 
    def __init__(self, id_nota, id_aluno, id_turma, disciplina, valor, data, tipo, aluno=None):
        if not ( 0 <= valor <= 10):
            raise ValueError("Somente valores de 0 a 10 são permitidos para notas.")
        
        self._id_nota = id_nota
        self._id_aluno = id_aluno
        self._id_turma = id_turma 
        self.disciplina = disciplina
        self.valor = float(valor) 
        self.data = data 
        self.tipo = tipo 
        self._aluno = aluno

    
        
    def to_dict(self):
        """
        Método para transformar as informações em dicionário para o Banco de Dados 
        """
        return {
            "id_nota": self._id_nota,
            "id_aluno": self._id_aluno,
            "id_turma": self._id_turma,
            "disciplina": self.disciplina,
            "valor": self.valor,
            "data": self.data, 
            "tipo": self.tipo
        }
    
    def __repr__(self):
        """
        Facilita a leitura para testes
        """
        return f"Nota(Aluno:{self._id_aluno} | {self.disciplina}: {self.valor})"


    @property
    def id_nota(self):
        return self._id_nota
    
    @property
    def id_aluno(self):
        return self._id_aluno
    
    @property
    def id_turma(self):
        return self._id_turma
    