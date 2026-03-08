from datetime import datetime

class Diario:
    def __init__(self, id_diario, id_turma, disciplina, data):
        """
        Representa uma aula realizada.
        :param id_diario: (int) Identificador único da aula.
        :param id_turma: (str) ID da turma que recebeu a aula.
        :param disciplina: (str) Nome da disciplina (ex: Matemática).
        :param data: (datetime) Objeto de data e hora da aula.
        """
        self.__id_diario = id_diario
        self.__id_turma = id_turma
        self.disciplina = disciplina
        
        # Garante que a data seja um objeto datetime
        if isinstance(data, str):
            self.data = datetime.strptime(data, "%Y-%m-%d")
        else:
            self.data = data

    @property
    def id_diario(self):
        return self.__id_diario

    @property
    def id_turma(self):
        return self.__id_turma

    def to_dict(self):
        """Útil para salvar o registro da aula no banco SQL"""
        return {
            "id_diario": self.__id_diario,
            "id_turma": self.__id_turma,
            "disciplina": self.disciplina,
            "data": self.data.strftime("%Y-%m-%d")
        }