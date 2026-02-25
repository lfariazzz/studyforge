from src.models.usuario import Usuario
from src.models.municipio import Municipio
from src.models.escola import Escola
from src.models.demanda_infraestrutura import DemandaInfraestrutura
from src.models.demanda_pedagogica import DemandaPedagogica

class Secretario(Usuario):
    def __init__(self, nome, cpf, email, senha, telefone, data_nascimento,
                 municipio_responsavel, verba_municipal_total, departamento, status=True):
        super().__init__(nome, cpf, email, senha, telefone, data_nascimento, status)

        self._municipio_responsavel = municipio_responsavel
        self._verba_municipal_total = verba_municipal_total
        self.departamento = departamento

    #-----------------
    #GETTERS E SETTERS
    #-----------------


    @property
    def municipio_responsavel(self):
        return self._municipio_responsavel
    
    @property
    def verba_municipal_total(self):
        return self._verba_municipal_total
    
    @property
    def departamento(self):
        return self._departamento
    
    @departamento.setter
    def departamento(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: O departamento deve ser uma string!")
        
        if not valor.isalpha():
            raise ValueError("Erro: No tipo de departamento não pode conter dígitos numéricos")

        padrao_departamento = valor.strip().upper()

        if len(padrao_departamento) < 2:
            raise ValueError("Erro: Departamento inválido!")
        
        else:
            self._departamento = padrao_departamento

    #-------
    #METODOS
    #-------

    def get_permissao(self):
        """Retorna as permissões de alto nível do Secretário no Sistema"""
        return (f"Secretário ({self.departamento}): Acesso total às unidades de {self.municipio_responsavel.nome}. "
                "Permissão para gerenciar verba municipal, aprovar licitações e administrar solicitações globais.")
    
    def exibir_perfil(self):
        
        print("\n" + "◈" * 45)
        print(f"  PAINEL DO SECRETÁRIO: {self.nome}")
        print("◈" * 45)
        print(f"  Município:      {self.municipio_responsavel.nome}")
        print(f"  Departamento:   {self.departamento}")
        print(f"  E-mail:         {self.email}")
        print(f"  Status:         {'ATIVO' if self.status else 'INATIVO'}")
        print("◈" * 45 + "\n")

    def ver_estatisticas(self):
        pass

    def realizar_cadastro(self, dados_gestor, escola_alvo):
        from src.models.gestor import Gestor
        novo_gestor = None

        if escola_alvo.municipio != self.municipio_responsavel:

            raise PermissionError(f"Erro: O secretário não tem permissão para cadastrar gestores "
                                 f"fora do município de {self.municipio_responsavel.nome}.")
        
        dados_gestor['escola_associada'] = escola_alvo
        novo_gestor = Gestor(**dados_gestor)

        return novo_gestor
    
    def enviar_mensagem(self):
        pass

    def gerenciar_verba(self, demanda):
        if not isinstance(demanda, DemandaInfraestrutura):
            return self.verba_municipal_total
        
        custo = getattr(demanda, '_DemandaInfraestrutura__custo_estimado', 0)

        if custo > 100000 or custo > self._verba_municipal_total:
            demanda.atualizar_status("EM LICITAÇÃO")

        else:
            self._verba_municipal_total -= custo
            demanda.atualizar_status("EM ANDAMENTO")

        return self.verba_municipal_total

    def administrar_solicitacoes(self, lista_demandas):
        demandas_municipais = [
            dados for dados in lista_demandas
            if dados.solicitante.escola_associada.municipio == self.municipio_responsavel
        ]       

        if not demandas_municipais:
            return []
        
        for demanda in demandas_municipais:
            demanda.processar_solicitacoes(self)
            
        return demandas_municipais
    
    def gerenciar_unidades(self, lista_escolas):
        pass