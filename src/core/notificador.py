from abc import ABC, abstractmethod
from src.models.demanda import AuditMixin

class IObservador(ABC):
    """Interface abstrata para definir o comportamento dos observadores do sistema."""

    @abstractmethod
    def atualizar(self, demanda):
        """
        Recebe uma notificação de mudança na demanda.

        Args:
            demanda (Demanda): O objeto de demanda que disparou o evento.
        """
        pass

class NotificadorCentral:
    """Gerencia a inscrição e a notificação de observadores por categoria."""

    def __init__(self):
        """Inicializa o notificador com categorias de demanda vazias."""
        self._assinantes = {"PEDAGOGICA": [], "INFRAESTRUTURA": []}

    def assinar(self, categoria, observador):
        """
        Inscreve um observador em uma categoria específica.

        Args:
            categoria (str): A categoria da demanda (ex: 'PEDAGOGICA').
            observador (IObservador): A instância do observador a ser notificada.
        """
        categoria = categoria.upper()
        if categoria in self._assinantes:
            self._assinantes[categoria].append(observador)

    def notificar(self, demanda, tipo_demanda):
        """
        Dispara o método atualizar() para todos os observadores da categoria.

        Args:
            demanda (Demanda): O objeto de demanda a ser processado.
            tipo_demanda (str): A categoria para filtrar a notificação.
        """
        tipo_demanda = tipo_demanda.upper()
        print(f"DEBUG NOTIFICADOR: Tipo buscado '{tipo_demanda}'. Chaves disponíveis: {list(self._assinantes.keys())}")
        
        if tipo_demanda in self._assinantes:
            observadores = self._assinantes[tipo_demanda]
            print(f"DEBUG NOTIFICADOR: Encontrei {len(observadores)} observadores.")
            for obs in observadores:
                print(f"DEBUG NOTIFICADOR: Disparando atualizar() para o objeto: {hex(id(obs))}")
                obs.atualizar(demanda)
        else:
            print("DEBUG NOTIFICADOR: CHAVE NÃO ENCONTRADA!")

class NotificadorEmail(IObservador, AuditMixin):
    """Responsável por enviar notificações de demanda via e-mail e registrar auditoria."""

    def __init__(self, papel_alvo):
        """
        Inicializa o notificador de e-mail.

        Args:
            papel_alvo (str): Descrição do destinatário (ex: 'Direção Escolar').
        """
        AuditMixin.__init__(self)
        self.papel_alvo = papel_alvo
        self.historico_auditoria = []

    def atualizar(self, demanda):
        """
        Envia o e-mail e registra o marco no histórico de auditoria.

        Args:
            demanda (Demanda): A demanda processada.
        """
        print(f"[E-MAIL] Enviado para {self.papel_alvo} sobre a demanda: {demanda.descricao}")
        
        solicitante_obj = demanda.solicitante() 
        nome_autor = solicitante_obj.nome if hasattr(solicitante_obj, 'nome') else str(solicitante_obj)
        
        self.registrar_marco(nome_autor, f"E-mail enviado para {self.papel_alvo}")
        self.historico_auditoria.append(demanda) 

class NotificadorSistema(IObservador, AuditMixin):
    """Responsável por gerar alertas internos do sistema e registrar auditoria."""

    def __init__(self):
        """Inicializa o notificador de sistema."""
        AuditMixin.__init__(self)
        self.historico_auditoria = []

    def atualizar(self, demanda):
        """
        Gera um alerta de sistema e registra o marco no histórico de auditoria.

        Args:
            demanda (Demanda): A demanda que disparou o alerta.
        """
        print(f"[SISTEMA] Alerta interno gerado para Demanda ID {demanda.id_demanda}")
        self.registrar_marco("SISTEMA", "Alerta interno")
        self.historico_auditoria.append(demanda)