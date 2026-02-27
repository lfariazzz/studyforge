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
        

class Demanda(ABC, AuditMixin):
    """
    Classe base seguindo os nomes definidos no UML.
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante, municipio_responsavel):
        AuditMixin.__init__(self)
        ABC.__init__(self)

        self.__descricao = descricao       
        self.__status = "ABERTO"           
        self.__prioridade = prioridade.upper() 
        self.__solicitante = solicitante   
        self.municipio_responsavel = municipio_responsavel

        @property
        def id_municipio(self):
            """
            Busca o ID do município navegando pelos objetos dos colegas (RN01).
            Isso evita que o código quebre se o atributo não estiver direto no solicitante.
            """
        #1. Se for um secretário
        if hasattr(self.__solicitante, 'municipio_responsavel'):
            # Acessa: Solicitante -> Municipio -> id_municipio
            return self.__solicitante.municipio_responsavel.id_municipio
        
        #2. Se for um Gestor 
        if hasattr(self.__solicitante, 'escola_associada'):
            # Acessa: Solicitante -> Escola -> Municipio -> id_municipio
            return self.__solicitante.escola_associada.municipio.id_municipio

        return None 


    @property 
    def status(self):
        """Permite que o atributo status seja utilizado nas outras classes"""
        return self.__status


    @property
    def solicitante(self):
        """Permite que as filhas acessem o objeto solicitante para auditoria"""
        return self.__solicitante

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