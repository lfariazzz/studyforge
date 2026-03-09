from abc import ABC, abstractmethod
from datetime import datetime 

class AuditMixin: 
    """
    Mixin criado para o rastreamento de dados de criação e alteração
    """
    def __init__(self, criado_em=None, alterado_por=None, data_alteracao=None, alerta=None):
        #Nascimento do registro
        self._criado_em = criado_em if criado_em else datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        #Alteração do registro
        self._alterado_por = alterado_por
        self._data_alteracao = data_alteracao
        #Notas de auditoria
        self._alerta_auditoria = alerta
        self.historico_marcos = []

    def atualizar(self, usuario_que_alterou):
        """Método que serve para registrar quem mexeu por último"""
        self._alterado_por = usuario_que_alterou
        self._data_alteracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
    def registrar_alerta(self, mensagem):
        """
        Guarda uma nota fiscal/jurídica sobre a demanda 
        sem precisar mudar o nome do 'usuario_que_alterou'.
        """
        self._alerta_auditoria = mensagem

    def registrar_data_demanda(self):
        momento_exato = datetime.now()
        #Data formatada
        data = momento_exato.strftime("%d/%m/%Y %H:%M:%S")

        return f"Data: {data} "

class Demanda(ABC, AuditMixin):
    """
    Classe base seguindo os nomes definidos no UML.
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante, municipio_responsavel, tipo, status="PENDENTE",
                 criado_em=None, editor=None, data_alteracao=None, alerta=None):
        AuditMixin.__init__(self,criado_em=criado_em, alterado_por=editor, data_alteracao=data_alteracao, alerta=alerta)
        ABC.__init__(self)

        self._id_demanda = id_demanda
        self._descricao = descricao       
        self._prioridade = prioridade.upper()  
        self.municipio_responsavel = municipio_responsavel
        self._solicitante = solicitante  
        self._tipo = tipo 
        self._status = status
        
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
        return self._status

    def solicitante(self):
        """Permite que as filhas acessem o objeto solicitante para auditoria"""
        return self.solicitante

    @property 
    def id_demanda(self):
        """Acesso apenas para leitura do ID conforme UML"""
        return self._id_demanda

    @property 
    def descricao(self):
        """Acesso apenas para leitura da descrição conforme UML"""
        return self._descricao
    
    def emitir_notificacao_critica(self):
        """Gatilho para urgência baseado no nome do atributo do UML (prioridade)"""
        mensagem = ""
        if self._prioridade == "CRÍTICO":
            mensagem = (
                f"ALERTA!: Notificando Gestor e Secretário! "
                f"Problema detectado: {self._descricao}")
               
        return mensagem

    @abstractmethod
    def processar_solicitacao(self, usuario):
        pass

    def atualizar_status(self, novo_status):
        """Método para alteração do status privado (usado pelas filhas)"""
        self._status = novo_status
        return self._status 
    
    def to_dict(self):
        """Converte os dados da demanda para um dicionário."""
        return {
            "id_demanda": self._id_demanda,
            "descricao": self._descricao,
            "status": self._status.upper(),
            "prioridade": self._prioridade.upper(),
            "id_solicitante": self._solicitante.id_usuario if self._solicitante else None,
            "id_municipio": self.municipio_responsavel.id_municipio if self.municipio_responsavel else None,
            "tipo": self._tipo.upper(),
            "data_criacao": self._criado_em,
            "ultimo_editor": self._alterado_por,
            "data_alteracao": self._data_alteracao,
            "alerta_auditoria": self._alerta_auditoria
        }