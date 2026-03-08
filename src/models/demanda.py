from abc import ABC, abstractmethod
from datetime import datetime 

class AuditMixin: 
    """
    Mixin criado para o rastreamento de dados de criação e alteração
    """
    def __init__(self):
        self._criado_em = datetime.now()
        self._alterado_por = None 

    def atualizar(self, usuario_que_alterou):
        """Método que serve para registrar quem mexeu por último"""
        self._alterado_por = usuario_que_alterou

        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")
        
    def registrar_alerta(self, mensagem):
        """
        Guarda uma nota fiscal/jurídica sobre a demanda 
        sem precisar mudar o nome do 'usuario_que_alterou'.
        """
        #O nome é genérico para esse método do mixin servir tanto para demanda pedagógica quando para 
        # demanda de infraestrutura.
        self._alerta_auditoria = mensagem

    def registrar_data_demanda_pedagogica(self):
        momento_exato = datetime.now()
        #Data formatada
        data = momento_exato.strftime("%d/%m/%Y %H:%M:%S")

        return f"Data: {data} "

class Demanda(ABC, AuditMixin):
    """
    Classe base seguindo os nomes definidos no UML.
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante, municipio_responsavel, tipo):
        AuditMixin.__init__(self)
        ABC.__init__(self)

        self.__id_demanda = id_demanda
        self.__descricao = descricao       
        self.__status = "PENDENTE"           
        self.__prioridade = prioridade.upper()  
        self.municipio_responsavel = municipio_responsavel
        self._solicitante = solicitante  
        self._tipo = tipo 
        
    @property
    def id_municipio(self):
        #1. Se for um secretário
        if hasattr(self._solicitante, 'municipio_responsavel'):
            return self._solicitante.municipio_responsavel.id_municipio
        
        #2. Se for um Gestor 
        if hasattr(self._solicitante, 'escola_associada'):
            return self._solicitante.escola_associada.municipio.id_municipio

        return None

    @property 
    def status(self):
        """Permite que o atributo status seja utilizado nas outras classes"""
        return self.__status

    def solicitante(self):
        """Permite que as filhas acessem o objeto solicitante para auditoria"""
        return self.solicitante

    @property 
    def id_demanda(self):
        """Acesso apenas para leitura do ID conforme UML"""
        return self.__id_demanda

    @property 
    def descricao(self):
        """Acesso apenas para leitura da descrição conforme UML"""
        return self.__descricao
    
    def emitir_notificacao_critica(self):
        """Gatilho para urgência baseado no nome do atributo do UML (prioridade)"""
        mensagem = ""
        if self.__prioridade == "CRÍTICO":
            mensagem = (
                f"ALERTA!: Notificando Gestor e Secretário! "
                f"Problema detectado: {self.__descricao}")
               
        return mensagem

    @abstractmethod
    def processar_solicitacao(self, usuario):
        pass

    def atualizar_status(self, novo_status):
        """Método para alteração do status privado (usado pelas filhas)"""
        self.__status = novo_status
        return self.__status 