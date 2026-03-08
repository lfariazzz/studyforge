from src.core.configuracoes import Configuracoes

class AvaliadorInfraestrutura:
    """
    Classe para instanciar o objeto municipio
    """
    def __init__(self, municipio):
    
        self.config = Configuracoes(municipio)


    def avaliar_custo(self, custo):
        """
        Método para avaliar se o custo é maior do que o pré-definido e mudar o status da demanda.
        """
        if custo > self.config.LIMITE_CUSTO_DEMANDA: 
            return "AGUARDANDO LICITAÇÃO"
        else: 
            return "ABERTO"