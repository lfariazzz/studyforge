from src.models.escola import Escola
from src.models.usuario import Usuario
from src.models.demanda import Demanda
from src.models.demanda_infraestrutura import DemandaInfraestrutura
from src.models.demanda_pedagogica import DemandaPedagogica

class Gestor(Usuario):
    def __init__(self, nome, cpf, email, senha, telefone, data_nascimento,
                 escola_associada, verba_escolar_total, status=True):
        super().__init__(nome, cpf, email, senha, telefone, data_nascimento, status)

        self.escola_associada = escola_associada
        self.verba_escolar_total = verba_escolar_total

    #-----------------
    #GETTERS E SETTERS
    #-----------------

    @property
    def escola_associada(self):
        return self._escola_associada

    @escola_associada.setter
    def escola_associada(self, valor):
        if not isinstance(valor, Escola):
            raise TypeError("Erro: Escola associada deve ser um objeto da classe Escola!")
        else:
            self._escola_associada = valor
    
    @property
    def verba_escolar_total(self):
        return self.__verba_escolar_total
    
    @verba_escolar_total.setter
    def verba_escolar_total(self, valor):
        if not isinstance(valor, (float, int)):
            raise TypeError("Erro: Verba Escolar Total deve ser um float ou inteiro!")
        
        padrao = round(float(valor), 2)

        if padrao <= 0:
            raise ValueError("Erro: A Verba Escolar Total não pode ser negativa ou igual a zero!")
        else:
            self.__verba_escolar_total = padrao

    #-------
    #METODOS
    #-------
    
    def get_permissao(self):
         """Retorna permisões que o Gestor tem no Sistema"""
         return "Gestor: Acesso a estatísticas, realizar cadastro, enviar mensagens, " \
                "solicitar demandas, administrar demandas, gerenciar escola"
    
    def exibir_perfil(self):
        print("\n" + "="*40)
        print(f"PERFIL DO GESTOR: {self.nome}")
        print("="*40)
        print(f"Email:               {self.email}")
        print(f"Telefone:            {self.telefone}")
        print(f"Escola Associada:    {Escola.nome}")
        print(f"Status:              {'ATIVO' if self.status else 'INATIVO'}")
        print("="*40 + "\n")

    def ver_estatisticas(self):
        pass

    def realizar_cadastro(self, tipo_usuario, dados_cadastro):
        from src.models.aluno import Aluno
        from src.models.professor import Professor
        novo_usuario = None

        if tipo_usuario == Aluno:
            novo_usuario = Aluno(**dados_cadastro)
        elif tipo_usuario ==Professor:
            dados_cadastro['escola_associada'] = self.escola_associada
            novo_usuario = Professor(**dados_cadastro)
        return novo_usuario
    
    def enviar_mensagem(self):
        pass
    
    def realizar_solicitacao(self, tipo_demanda, dados_solicitacao):

        nova_demanda = None
        dados_solicitacao['solicitante'] = self

        if tipo_demanda == DemandaInfraestrutura:
            valor_estimado = dados_solicitacao.get('custo_estimado')
            if valor_estimado is None or valor_estimado <= 0:
                raise ValueError("Erro: O valor não pode ser vazio ou menor/igual a 0")
            nova_demanda = DemandaInfraestrutura(**dados_solicitacao)
            valor_estimado = dados_solicitacao.get('custo_estimado')
            if valor_estimado > self.verba_escolar_total:
                nova_demanda.atualizar_status("EM LICITAÇÃO")
        elif tipo_demanda == DemandaPedagogica:
            nova_demanda = DemandaPedagogica(**dados_solicitacao)

        return nova_demanda
        
    def administrar_solicitacoes(self, lista_demandas):

        if lista_demandas is None:
            raise ValueError("Erro: A lista de demandas não pode ser None!")
        elif lista_demandas == []:
            print("Nenhuma demanda pendente.")

        for dado in lista_demandas:
            dado.processar_solicitacao(self)
            
    def gerenciar_escola(self):
        pass