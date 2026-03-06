import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path para conseguir importar src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importações atualizadas
from src.models.demanda import Demanda
from src.models.demanda_pedagogica import DemandaPedagogica
from src.models.demanda_infraestrutura import DemandaInfraestrutura

# --- MOCKS / SIMULAÇÕES DE CLASSES DEPENDENTES ---
class Municipio:
    def __init__(self, id_municipio, nome, verba, lacuna_max, media_freq):
        self.id_municipio = id_municipio
        self.nome = nome
        self.verba_disponivel_municipio = verba
        self.lacuna_maxima_permitida = lacuna_max
        self.media_frequencia = media_freq

class Escola:
    def __init__(self, nome, municipio):
        self.nome = nome
        self.municipio = municipio

class Turma:
    def __init__(self, nome, alunos):
        self.nome = nome
        self._alunos_matriculados = alunos 
    
    @property
    def quantidade_alunos_sala(self):
        return len(self._alunos_matriculados)

class Gestor:
    def __init__(self, nome, escola):
        self.nome = nome
        self.escola_associada = escola

class Secretario:
    def __init__(self, nome, municipio):
        self.nome = nome
        self.municipio_responsavel = municipio

# --- CÓDIGO DE TESTE ---
def testar_sistema_demandas():
    print("Iniciando testes funcionais...\n")

    # 1. Configuração do Cenário (Juazeiro)
    muni_juazeiro = Municipio("JUA01", "Juazeiro", 50000.0, 0.30, 0.75)
    escola_padre_cicero = Escola("Padre Cicero", muni_juazeiro)
    
    gestor_pedro = Gestor("Pedro", escola_padre_cicero)
    secretario_maria = Secretario("Maria", muni_juazeiro)
    
    # 5 alunos total
    turma_1a = Turma("1º Ano A", ["A1", "A2", "A3", "A4", "A5"])

    # --- Teste 1: Demanda Pedagógica ---
    print("--- Teste 1: Demanda Pedagógica ---")
    
    # Cenário: 2 alunos em risco de 5 (40% de lacuna), freq 70%
    # Passando municipio_responsavel (muni_juazeiro)
    
    # --- AJUSTE: Passando apenas os argumentos necessários ---
    demanda_ped = DemandaPedagogica(
        "PED01", "Reforço Matemática", "MÉDIA", gestor_pedro,
        turma_1a, 2, 0.70, 
        muni_juazeiro # <--- id_municipio não é mais passado explicitamente aqui
    )

    print(f"Lacuna: {demanda_ped.indice_lacuna * 100:.1f}% (Limite: {muni_juazeiro.lacuna_maxima_permitida * 100}%)")
    print(f"Freq: {demanda_ped.frequencia_atual * 100:.1f}% (Meta: {muni_juazeiro.media_frequencia * 100}%)")
    
    # Processa e verifica se o status mudou
    demanda_ped.processar_solicitacao(gestor_pedro)
    print(f"Status Final: {demanda_ped.status}")
    
    assert demanda_ped.status == "REFORÇO NECESSÁRIO"
    print("Teste 1 OK!\n")

    # --- Teste 2: Demanda Infraestrutura ---
    print("--- Teste 2: Demanda Infraestrutura ---")
    
    # Demanda cara (R$ 60.000) mas verba é R$ 50.000
    # Adicionado municipio_responsavel na chamada
    demanda_infra = DemandaInfraestrutura(
        "INF01", "Reforma Telhado", "ALTA", gestor_pedro, 
        60000.0, escola_padre_cicero, 
        muni_juazeiro
    )

    # Tentar solicitar deve falhar por falta de verba
    try:
        demanda_infra.solicitar_demanda(gestor_pedro)
        print("Erro: Deveria ter falhado por falta de verba.")
    except ValueError as e:
        print(f"Sucesso: Erro de verba capturado -> {e}")

    # Demanda barata (R$ 10.000)
    demanda_infra_barata = DemandaInfraestrutura(
        "INF02", "Pintura", "BAIXA", gestor_pedro, 
        10000.0, escola_padre_cicero,
        muni_juazeiro
    )

    # Solicitar
    demanda_infra_barata.solicitar_demanda(gestor_pedro)
    print(f"Status após solicitação: {demanda_infra_barata.status}")
    assert demanda_infra_barata.status == "ABERTO"

    # Aprovar pelo Secretário
    demanda_infra_barata.processar_solicitacao(secretario_maria)
    print(f"Status após aprovação: {demanda_infra_barata.status}")
    assert demanda_infra_barata.status == "APROVADO"
    
    print("Teste 2 OK!\n")

    # --- Teste 3: Validação de Jurisdição ---
    print("--- Teste 3: Validação de Jurisdição ---")
    muni_crato = Municipio("CRA01", "Crato", 100000.0, 0.30, 0.75)
    secretario_crato = Secretario("João", muni_crato)
    
    # O teste utiliza o método validar_usuario que agora está na classe pai
    try:
        # A demanda_infra_barata pertence a Juazeiro, secretário do Crato tenta acessar
        demanda_infra_barata.validar_usuario(secretario_crato)
        print("Erro: Deveria ter falhado por jurisdição diferente.")
    except PermissionError as e:
        print(f"Sucesso: Erro de permissão capturado -> {e}")

    print("Teste 3 OK!\n")
    print("Todos os testes passaram!")

if __name__ == "__main__":
    testar_sistema_demandas()