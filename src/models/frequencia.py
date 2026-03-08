class Frequencia: 
    def __init__(self, id_frequencia, id_aluno, id_diario, status):

        if status.upper() not in ["PRESENTE", "AUSENTE"]:
            raise ValueError(f"O status de um aluno só pode ser presente ou ausente, foi digitado: {status}")

        self.__id_frequencia = id_frequencia
        self.__id_aluno = id_aluno 
        self.__id_diario = id_diario
        self.status = status.upper()

    @property 
    def id_diario(self):
        """retorna o id do diario"""
        return self.__id_diario
    
    @property
    def id_aluno(self):
        """retorna o id do aluno"""
        return self.__id_aluno
    
    @property
    def id_frequencia(self):
        """retorna o id da frequência"""
        return self.__id_frequencia
    
    def to_dict(self):
        return {
            "id_frequencia": self.__id_frequencia,
            "id_aluno": self.__id_aluno,
            "id_diario": self.__id_diario,
            "status": self.status
        }
    