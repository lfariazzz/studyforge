class Frequencia: 
    def __init__(self, id_frequencia, status, id_aluno, id_diario):

        if status.upper() not in ["PRESENTE", "AUSENTE"]:
            raise ValueError(f"O status de um aluno só pode ser presente ou ausente, foi digitado: {status}")

        self._id_frequencia = id_frequencia
        self._id_aluno = id_aluno 
        self._aluno = aluno
        self._id_diario = id_diario
        self.status = status.upper()

    @property 
    def id_diario(self):
        """retorna o id do diario"""
        return self._id_diario
    
    @property
    def id_aluno(self):
        """retorna o id do aluno"""
        return self._id_aluno
    
    @property
    def id_frequencia(self):
        """retorna o id da frequência"""
        return self._id_frequencia
    
    def to_dict(self):
        return {
            "id_frequencia": self._id_frequencia,
            "status": self.status.upper(),
            "id_aluno": self._id_aluno,
            "id_diario": self._id_diario,
        }
    