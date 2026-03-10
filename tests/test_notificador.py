from datetime import date
from src.core.notificador import NotificadorCentral, NotificadorEmail, NotificadorSistema
from src.core.demanda_factory import DemandaFactory
from src.models.professor import Professor
from src.models.gestor import Gestor
from src.models.escola import Escola
from src.models.turma import Turma
from src.models.aluno import Aluno
from src.models.municipio import Municipio
from src.models.secretario import Secretario

# --- MUNICÍPIO ---
mun_obj = Municipio(
    nome="Município Central",
    id_municipio="MUN-001",
    estado="SP",
    verba_disponivel_municipio=100000.0,
    nota_de_corte=7.0
)

# --- SECRETÁRIO ---
secretario_municipal = Secretario(
    "SEC-001", "João Secretário", "99988877766", "sec@gov.br",
    "senha123", "11999998888", "01/01/1980", mun_obj, "EDUCAÇÃO"
)

# --- ESCOLA E GESTOR ---
escola = Escola("Escola Municipal StudyForge", "Rua do Conhecimento, 123",
                "ESC-001", None, 50000.0, "MUN-001", mun_obj)
escola.municipio = mun_obj
escola.municipi = mun_obj 

gestor = Gestor(
    "GEST-001", "Ana Gestora", "12345678901", "ana.gestao@email.com",
    "senhaSegura123", "11911112222", "20/08/1975", escola
)
escola._gestor_atual = gestor

# --- PROFESSOR ---
professor_exemplo = Professor(
    "PROF-001", "Carlos Silva", "10987654321", "carlos@email.com",
    "senha123456", "11988887777", "10/05/1980", "RF-2026-0001",
    escola, "Mestre", "Matemática", 5000.0
)

turma_9a = Turma("T01", "9º Ano A", 2026, "ESC-001", "MANHÃ")

aluno_teste = Aluno(
    "ALUNO-001", "João", "11122233344", "joao@email.com",
    "senhaSegura123", "00000000000", "01/01/2010",
    turma_associada="9º Ano A", matricula="2026-ALUNO-001"
)

# Associação
turma_9a.adicionar_aluno(aluno_teste)
turma_9a.adicionar_professor(professor_exemplo)
turma_9a.registrar_aula(professor_exemplo, date.today(), "Introdução à Álgebra")

# --- OBSERVER ---
def resetar_canais(canais):
    for canal in canais:
        canal.historico_auditoria = []

notificador = NotificadorCentral()

# Professores recebem apenas demandas pedagógicas
canal_docente_email = NotificadorEmail("Corpo Docente")
notificador.assinar("PEDAGOGICA", canal_docente_email)

# Gestão e secretaria recebem apenas demandas de infraestrutura
canal_gestao_email = NotificadorEmail("Direção Escolar")
canal_secretaria_email = NotificadorEmail("Gabinete da Secretaria")
canal_sistema = NotificadorSistema()

notificador.assinar("INFRAESTRUTURA", canal_gestao_email)
notificador.assinar("INFRAESTRUTURA", canal_secretaria_email)
notificador.assinar("INFRAESTRUTURA", canal_sistema)

# --- TESTES ---
print("\n--- Teste: Notificação da Secretaria em Infraestrutura ---")
resetar_canais([canal_docente_email, canal_gestao_email, canal_secretaria_email, canal_sistema])

DemandaFactory.criar_demanda(
    tipo_demanda="INFRAESTRUTURA",
    solicitante=gestor,
    notificador=notificador,
    descricao="Reparo telhado",
    custo_estimado=80000.0
)

print("Sucesso: Secretaria integrada ao Padrão Observer com sucesso!")

print("\n--- Teste: Filtro de Relevância Pedagógico ---")

resetar_canais([canal_docente_email, canal_gestao_email, canal_secretaria_email, canal_sistema])

# Wrapper para transformar os dicionários do diário em objetos com atributos
class AulaWrapper:
    def __init__(self, registro):
        self.professor = registro.get("professor") or registro.get("docente")
        self.data = registro.get("data")
        self.conteudo = registro.get("conteudo")

turma_9a._diario_de_classe = [AulaWrapper(registro) for registro in turma_9a._diario_de_classe]

DemandaFactory.criar_demanda(
    "PEDAGOGICA",
    solicitante=professor_exemplo,
    turma=turma_9a,
    notificador=notificador,
    mes=3
)

# Pedagógica
assert len(canal_docente_email.historico_auditoria) > 0, "Professor deveria ter sido notificado"
assert len(canal_gestao_email.historico_auditoria) == 0, "Gestão NÃO deveria receber demanda pedagógica"
assert len(canal_secretaria_email.historico_auditoria) == 0, "Secretaria NÃO deveria receber demanda pedagógica"

print("Sucesso: Filtro pedagógico validado!")

print("\n--- Teste: Filtro de Relevância Infraestrutura ---")
resetar_canais([canal_docente_email, canal_gestao_email, canal_secretaria_email, canal_sistema])

DemandaFactory.criar_demanda(
    tipo_demanda="INFRAESTRUTURA",
    solicitante=gestor,
    notificador=notificador,
    descricao="Troca de lâmpadas",
    custo_estimado=2500.0
)

# Infraestrutura
assert len(canal_docente_email.historico_auditoria) == 0
assert len(canal_gestao_email.historico_auditoria) > 0
assert len(canal_secretaria_email.historico_auditoria) > 0
assert len(canal_sistema.historico_auditoria) > 0

print("Sucesso: Filtro de relevância infraestrutura validado!")
