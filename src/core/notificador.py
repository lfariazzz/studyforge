from abc import ABC, abstractmethod
from src.models.demanda import AuditMixin

class IObservador(ABC):
    """
    Interface abstrata para definir o comportamento dos observadores do sistema.

    Observadores são componentes que reagem a eventos disparados pelo NotificadorCentral,
    como a criação ou atualização de uma demanda. Cada observador deve implementar o
    método `atualizar`, que define a ação a ser tomada quando uma notificação ocorre.
    """

    @abstractmethod
    def atualizar(self, demanda):
        """
        Recebe uma notificação de mudança na demanda.

        Args:
            demanda (Demanda): O objeto de demanda que disparou o evento.
        """
        pass


class NotificadorCentral:
    """
    Gerencia a inscrição e a notificação de observadores por categoria de demanda.

    Essa classe implementa o papel de "Sujeito" no padrão Observer. Ela mantém listas
    de observadores organizadas por categoria (ex.: 'PEDAGOGICA', 'INFRAESTRUTURA') e
    dispara notificações para todos os inscritos quando um evento relevante ocorre.
    """

    def __init__(self):
        """Inicializa o notificador com categorias de demanda pré-definidas e listas vazias de observadores."""
        self._assinantes = {"PEDAGOGICA": [], "INFRAESTRUTURA": []}

    def assinar(self, categoria, observador):
        """
        Inscreve um observador em uma categoria específica.

        Args:
            categoria (str): A categoria da demanda (ex: 'PEDAGOGICA', 'INFRAESTRUTURA').
            observador (IObservador): A instância do observador que será notificada.
        """
        categoria = categoria.upper()
        if categoria in self._assinantes:
            self._assinantes[categoria].append(observador)

    def notificar(self, demanda, tipo_demanda):
        """
        Dispara o método atualizar() para todos os observadores da categoria informada.

        Args:
            demanda (Demanda): O objeto de demanda a ser processado.
            tipo_demanda (str): A categoria usada para filtrar quais observadores serão notificados.
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
    """
    Observador responsável por enviar notificações de demanda via e-mail.

    Além de simular o envio de e-mails, registra cada envio no histórico de auditoria
    para garantir rastreabilidade futura.
    """

    def __init__(self, papel_alvo):
        """
        Inicializa o notificador de e-mail.

        Args:
            papel_alvo (str): Descrição do destinatário (ex: 'Direção Escolar', 'Corpo Docente').
        """
        AuditMixin.__init__(self)
        self.papel_alvo = papel_alvo
        self.historico_auditoria = []

    def atualizar(self, demanda):
        """
        Envia o e-mail e registra o marco no histórico de auditoria.

        Args:
            demanda (Demanda): A demanda processada que disparou a notificação.
        """
        print(f"[E-MAIL] Enviado para {self.papel_alvo} sobre a demanda: {demanda.descricao}")
        
        solicitante_obj = demanda.solicitante() 
        nome_autor = solicitante_obj.nome if hasattr(solicitante_obj, 'nome') else str(solicitante_obj)
        
        self.registrar_marco(nome_autor, f"E-mail enviado para {self.papel_alvo}")
        self.historico_auditoria.append(demanda) 


class NotificadorSistema(IObservador, AuditMixin):
    """
    Observador responsável por gerar alertas internos do sistema.

    Esse observador simula notificações internas (ex.: alertas em painel de gestão)
    e registra cada alerta no histórico de auditoria.
    """

    def __init__(self):
        """Inicializa o notificador de sistema com histórico de auditoria vazio."""
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
