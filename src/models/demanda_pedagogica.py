from src.models.demanda import Demanda 

class DemandaPedagogica(Demanda):
    """
    Essa classe tem a função de calcular as demandas pedagógicas como a necessidade de realizar
    mais aulas pela lacuna de conteúdo
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante, 
                 total_alunos, alunos_abaixo_media, frequencia_turma, alunos_presentes, turma_alvo):
        super().__init__(id_demanda, descricao, prioridade, solicitante)
        
        self.__total_alunos = total_alunos
        self.__alunos_abaixo_media = alunos_abaixo_media
        self.__frequencia_turma = frequencia_turma
        self.__indice_lacuna = 0.0
        self.__alunos_presentes = alunos_presentes
        self.__turma_alvo = turma_alvo

    """Os propertys responsáveis por tornar possível a visualização dos atributos do método construtor desta classe"""
    @property
    def indice_lacuna(self):
        return self.__indice_lacuna

    @property
    def frequencia_atual(self):
        return self.__frequencia_turma
    
    

    def validar_reforco(self):
        """
    Método que cálcula a média de alunos abaixo da média e frequência da turma para validar o reforço.
    Nele, o índice lacuna tem que ser maior que 40% para validar o reforço de aulas e a frequência
    menor que 75% para chamar a atenção da direção da escola.
        """

        if self.__total_alunos == 0: 
            return False 
      
        self.__indice_lacuna = self.__alunos_abaixo_media / self.__total_alunos
        self.__frequencia_turma = self.__alunos_presentes / self.__total_alunos
        
        regra_nota = self.__indice_lacuna >= 0.4 
        regra_presenca = self.__frequencia_turma >= 0.75 

        return regra_nota or regra_presenca


    def processar_solicitacao(self, usuario):
        """
        Processa a solicitação de reforço pedagógico baseada em indicadores de desempenho.
        """
        if self.id_municipio != usuario.id_municipio: 
            print("Acesso negado")
            return
        
        if self.validar_reforco(): 
            print(f"STATUS DA SALA: {self.__turma_alvo.nome}  ")
            print(f"Frequência: {self.__frequencia_turma*100:.1f}%")
            print(f"Porcentagem lacuna de aprendizado: {self.__indice_lacuna*100:.1f}%")

            self.atualizar_status("REFORÇO APROVADO")

        else: 
            self.atualizar_status("REGULAR")


