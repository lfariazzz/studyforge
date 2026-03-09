from datetime import datetime
from src.models.aluno import Aluno
from src.models.frequencia import Frequencia
from src.models.diario import Diario
from src.services.avaliador_frequencia import AvaliadorFrequencia

# 1. SETUP: Simulação da Classe Turma (para o Avaliador conseguir ler os dados)
class MockTurma:
    def __init__(self, nome):
        self.nome = nome
        self._alunos_matriculados = []
        self._diario_de_classe = [] # Lista de objetos Diario

# 2. INÍCIO DO TESTE
print("--- Iniciando Teste de Regras de Negócio (RN02) ---")

# Criando a Turma
turma_9a = MockTurma("9º Ano A")

# 3. CRIANDO ALUNOS (Com dados que passam nas validações do Usuario)
# CPF: 11 dígitos | Senha: 8+ caracteres
# 3. CRIANDO ALUNOS (Ajustado para o formato DD/MM/AAAA)
try:
    aluno1 = Aluno(
        nome="João Silva", 
        cpf="12345678901", 
        email="joao@email.com", 
        senha="senhaSegura123", 
        telefone="88999999999", 
        data_nascimento="01/01/2010" # <--- Formato corrigido
    )
    
    aluno2 = Aluno(
        nome="Maria Souza", 
        cpf="98765432100", 
        email="maria@email.com", 
        senha="outraSenha888", 
        telefone="88888888888", 
        data_nascimento="05/05/2010" # <--- Formato corrigido
    )
    
    turma_9a._alunos_matriculados.extend([aluno1, aluno2])
    print("✅ Alunos criados com sucesso (Passaram em TODAS as validações).")

except ValueError as e:
    print(f"❌ Erro de validação na criação do Aluno: {e}")
    exit()

# 4. CRIANDO O CALENDÁRIO (Diários)
# Criaremos 4 aulas no mês de Março (Mês 3)
aulas_marco = [
    Diario(id_diario=101, id_turma="9A", disciplina="Matemática", data="2026-03-05"),
    Diario(id_diario=102, id_turma="9A", disciplina="Matemática", data="2026-03-12"),
    Diario(id_diario=103, id_turma="9A", disciplina="Matemática", data="2026-03-19"),
    Diario(id_diario=104, id_turma="9A", disciplina="Matemática", data="2026-03-26"),
]
turma_9a._diario_de_classe.extend(aulas_marco)

# 5. LANÇANDO AS FREQUÊNCIAS (Simulando 50% de presença para a turma)
# João veio em 2 aulas e faltou em 2
aluno1.presencas.append(Frequencia(1, aluno1.id, 101, "PRESENTE"))
aluno1.presencas.append(Frequencia(2, aluno1.id, 102, "AUSENTE"))
aluno1.presencas.append(Frequencia(3, aluno1.id, 103, "PRESENTE"))
aluno1.presencas.append(Frequencia(4, aluno1.id, 104, "AUSENTE"))

# Maria também veio em 2 e faltou em 2
aluno2.presencas.append(Frequencia(5, aluno2.id, 101, "AUSENTE"))
aluno2.presencas.append(Frequencia(6, aluno2.id, 102, "PRESENTE"))
aluno2.presencas.append(Frequencia(7, aluno2.id, 103, "AUSENTE"))
aluno2.presencas.append(Frequencia(8, aluno2.id, 104, "PRESENTE"))

# 6. EXECUTANDO O AVALIADOR
avaliador = AvaliadorFrequencia()

# Testando média individual do João
media_joao = avaliador.media_presenca_mensal_aluno(aluno1, turma_9a, 3)
print(f"📊 Frequência do {aluno1.nome} em Março: {media_joao * 100:.1f}%")

# Testando a RN02 (Média da Turma e geração de demanda)
print("\n--- Verificando RN02 (Média Global da Turma) ---")
demanda = avaliador.verificar_media_frequencia_mensal(turma_9a, 3)

if demanda:
    print(f"🚨 DEMANDA GERADA: {demanda.descricao}")
    print(f"Prioridade: {demanda.prioridade}")
    print(f"Solicitante: {demanda._solicitante}")
else:
    print("👍 Frequência dentro do limite. Nenhuma demanda gerada.")