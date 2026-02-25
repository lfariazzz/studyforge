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
        
        print(f"---LOG DE AUDITORIA---"
              f"Usuário: {usuario_que_alterou.nome}"
              f"Data e Hora da alteração: {data_formatada}"
              f"--------------------------------------------"
        )


class Demanda(ABC, AuditMixin):
    """
    Classe base seguindo os nomes definidos no UML.
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante):
        AuditMixin.__init__(self)
        ABC.__init__(self)

        self.__id_demanda = id_demanda     
        self.__descricao = descricao       
        self.__status = "ABERTO"           
        self.__prioridade = prioridade.upper() 
        self.__solicitante = solicitante   

    @property
    def id_municipio(self):
        """Busca o id_municipio através do objeto solicitante (RN01)"""
        return self.__solicitante.id_municipio 
    
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
        if self.__prioridade == "CRÍTICO":
            print("ALERTA!: Notificando Gestor e Secretário!"
            f"Problema detectado: {self.__descricao}")

    @abstractmethod
    def processar_solicitacao(self, usuario):
        pass

    def atualizar_status(self, novo_status):
        """Método para alteração do status privado (usado pelas filhas)"""
        self.__status = novo_status
        print(f"Status alterado para: {self.__status}")