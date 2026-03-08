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

mun_obj = Municipio(
    nome="Município Central",
    id_municipio="MUN-001",
    estado="SP",
    verba_disponivel_municipio=100000.0,
    media_frequencia=0.9,
    lacuna_maxima_permitida=0.05
)
secretario_municipal = Secretario(
    "João Secretário", 
    "99988877766", 
    "sec@gov.br", 
    "senha123", 
    "11999998888", 
    "01/01/1980", 
    mun_obj, 
    "EDUCAÇÃO"
)

escola = Escola("Escola Municipal StudyForge", "Rua do Conhecimento, 123", "ESC-001", None, 50000.0, "MUN-001", mun_obj)
gestor = Gestor("Ana Gestora", "12345678901", "ana.gestao@email.com", "senhaSegura123", "11911112222", "20/08/1975", escola)
escola._gestor_atual = gestor

turma_9a = Turma(id_turma="T01", nome="9A", ano_letivo=2026, id_escola="ESC-001", turno="MANHÃ")
professor_exemplo = Professor("Carlos Silva", "10987654321", "carlos@email.com", "senha123456", "11988887777", "10/05/1980", "RF-2026-0001", escola, "Mestre", "Matemática", 5000.0)
aluno_teste = Aluno("João", "11122233344", "joao@email.com", "senhaSegura123", "00000000000", "01/01/2010")

turma_9a.adicionar_aluno(aluno_teste)
turma_9a.adicionar_professor(professor_exemplo)
turma_9a.registrar_aula(professor_exemplo, date.today(), "Introdução à Álgebra")

# 2. CONFIGURAÇÃO DO OBSERVER
#notificador = NotificadorCentral()
#canal_prof = NotificadorEmail("Corpo Docente")
#canal_gestao_email = NotificadorEmail("Direção Escolar")
#canal_gestao_sistema = NotificadorSistema()
#canal_secretaria = NotificadorEmail("Gabinete da Secretaria")
#canal_secretaria.historico_auditoria = [] # Inicializa histórico

# Garantindo que o atributo de auditoria exista para o teste
#for canal in [canal_prof, canal_gestao_email, canal_gestao_sistema]:
    #canal.historico_auditoria = []

def resetar_canais(canais):
    for canal in canais:
        canal.historico_auditoria = []

# --- CONFIGURAÇÃO ÚNICA ---
notificador = NotificadorCentral()
canal_prof = NotificadorEmail("Corpo Docente")
canal_gestao_email = NotificadorEmail("Direção Escolar")
canal_gestao_sistema = NotificadorSistema()
canal_secretaria = NotificadorEmail("Gabinete da Secretaria")

notificador.assinar("INFRAESTRUTURA", canal_gestao_email)
notificador.assinar("PEDAGOGICA", canal_prof)
notificador.assinar("INFRAESTRUTURA", canal_gestao_sistema)
notificador.assinar("INFRAESTRUTURA", canal_secretaria)



print(f"DEBUG: Verificando lista de assinantes em INFRAESTRUTURA:")
print(notificador._assinantes["INFRAESTRUTURA"]) 
# Se o canal_secretaria não estiver nessa lista, o erro é aqui!

# 3. TESTE DE INTEGRAÇÃO: Disparando demanda que exige atenção da Secretaria
print("\n--- Teste: Notificação da Secretaria em Infraestrutura ---")

resetar_canais([canal_prof, canal_gestao_email, canal_gestao_sistema, canal_secretaria])

DemandaFactory.criar_demanda(
    tipo_demanda="INFRAESTRUTURA",
    solicitante=gestor,
    notificador=notificador,
    descricao="Reparo telhado",
    custo_estimado=80000.0 # Valor alto para alertar a secretaria
)

# Agora verificamos se o canal da secretaria recebeu a demanda
print(f"DEBUG TESTE: Tamanho do histórico da Secretaria: {len(canal_secretaria.historico_auditoria)}")

assert len(canal_secretaria.historico_auditoria) > 0, "Secretaria deveria ter sido notificada"
assert canal_secretaria.historico_auditoria[0].descricao == "Reparo telhado"

print("Sucesso: Secretaria integrada ao Padrão Observer com sucesso!")

# 3. TESTES DE INTEGRAÇÃO (AGORA RODANDO COM CÓDIGO REAL)
print("--- Teste: Filtro de Relevância Pedagógico ---")

resetar_canais([canal_prof, canal_gestao_email, canal_gestao_sistema, canal_secretaria])

DemandaFactory.criar_demanda(
    "PEDAGOGICA", 
    gestor, 
    descricao="Alerta Evasão", 
    notificador=notificador, 
    turma=turma_9a, 
    mes=3
)


print("Sucesso: Secretaria integrada ao Padrão Observer com sucesso!")
# No seu arquivo de teste
print(f"DEBUG TESTE: O objeto canal_prof está no endereço de memória: {hex(id(canal_prof))}")
print(f"DEBUG TESTE: Tamanho do histórico: {len(canal_prof.historico_auditoria)}")

assert len(canal_prof.historico_auditoria) > 0, "Professor deveria ter sido notificado"
assert len(canal_gestao_email.historico_auditoria) == 0, "Gestão NÃO deveria receber demanda pedagógica"

print("\n--- Teste: Filtro de Relevância Infraestrutura ---")

resetar_canais([canal_prof, canal_gestao_email, canal_gestao_sistema, canal_secretaria])

DemandaFactory.criar_demanda(
    tipo_demanda="INFRAESTRUTURA",
    solicitante=gestor,
    notificador=notificador,       # Nomeado
    descricao="Reparo telhado",    # Nomeado
    custo_estimado=2500.0
)

assert len(canal_gestao_email.historico_auditoria) > 0, "Gestão deveria receber e-mail"
assert len(canal_gestao_sistema.historico_auditoria) > 0, "Gestão deveria receber alerta no sistema"

print("\nSucesso: Padrão Observer validado com sucesso usando as classes reais!")