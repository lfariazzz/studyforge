from src.models.demanda import Demanda
from core.configuracoes import Configuracoes

class DemandaInfraestrutura(Demanda):
    """
    Essa classe tem a função de ordenar as demandas de estruturas, passando por um 
    processo de solicitação que validam as informações, nível de importância e coleta os 
    dados dos envolvidos. 
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante, custo_estimado, localizacao_demanda):
        super().__init__(id_demanda, descricao, prioridade, solicitante)
        self.__custo_estimado = custo_estimado
        self.__localizacao_demanda = localizacao_demanda
        self.config = Configuracoes

    def processar_solicitacao(self, usuario):
        """
        Esse método primeiro passa pela primeira validação, para conferir o acesso, e depois passa pela segunda validação:
        calcular o custo estimado e, caso ele seja maior que o definido nas configs, atualizar o status para licitação,
        em prol de solicitar o aumento da verba.
        """
        if self.id_municipio != usuario.id_municipio: 
            print(f"Acesso negado! o usuário {usuario.nome} não pertence a esse município") 
            return 
        if self.__custo_estimado > self.config.LIMITE_CUSTO_DEMANDA: 
            print(f"O custo estimado é maior do que o disponível, a obra entrará em processo de licitação")
            self.atualizar_status ("EM LICITAÇÃO")
        else: 
            print(f"O custo para esta obra foi aprovado, entrando em execução")
            self.atualizar_status("EM ANDAMENTO")

        self.emitir_notificacao_critica()
        """Gatilho para urgência (se a prioridade for crítica, emitir chamado)"""

        self.atualizar(usuario)
        """Atualiza quem foi a última pessoa a mexer na demanda"""

