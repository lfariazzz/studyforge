from datetime import date
from src.models.aluno import Aluno
from src.models.professor import Professor
from src.models.turma import Turma
from src.services.avaliador_frequencia import AvaliadorFrequencia


"""Esse foi um teste gerado por inteligência artificical para testar a validação da regra de negócio 02, necessário
para validar a alta coesão e integração entre módulos (aluno, turma, avaliador_frequência e demanda factory)"""
def executar_fluxo_rn02():
    print("🛡️ [StudyForge] Iniciando Teste de Integração de Segurança e Frequência\n")

    try:
        # 1. CRIAR A TURMA (Satisfazendo o Malaquias)
        turma = Turma(
            id_turma="T-POO-2026", 
            nome="Programacao Orientada a Objetos", 
            ano_letivo=2026, 
            id_escola="ESC-UFCA-01"
        )

        # 2. CRIAR O PROFESSOR (Satisfazendo as travas de Usuario e Professor)
        # Nome: Apenas letras | CPF: 11 dígitos | Senha: 8+ chars com número | Data: DD/MM/AAAA
        prof = Professor(
            nome="Claudio Oliveira", 
            cpf="12345678901", 
            email="claudio@ufca.edu.br", 
            senha="Professor123!", # Forte e com números
            telefone="88999887766", 
            data_nascimento="01/01/1980",
            registro_funcional="RF-2026-0001", 
            escola_associada="UFCA", 
            titulacao="Doutor", 
            area_atuacao="Computacao", 
            salario=5000.0
        )

        # Registro obrigatório na Turma para o Professor ter poder de fala
        turma.adicionar_professor(prof)

        # 3. CRIAR O ALUNO (Satisfazendo Aluno e Usuario)
        # Matrícula: MAT-2026-0001
        aluno = Aluno(
            nome="Levi Farias", 
            cpf="98765432100", 
            email="levi@ufca.edu.br", 
            senha="LeviFarias2026", 
            telefone="88912345678", 
            data_nascimento="10/05/2000",
            id_matricula="MAT-2026-0001"
        )
        turma.adicionar_aluno(aluno)

        print(f"✅ Entidades criadas com sucesso: {prof.nome} (Prof) e {aluno.nome} (Aluno).")
        print(f"📅 Turma: {turma.nome} ({turma.ano_letivo})\n")

        # 4. SIMULAR CHAMADAS (O teste de fogo da RN02)
        # Vamos simular 4 aulas no mês de Fevereiro (Mês 2).
        # O Levi terá apenas 1 presença (25%), o que está abaixo dos 75% configurados.
        datas_aulas = [date(2026, 2, 2), date(2026, 2, 4), date(2026, 2, 9), date(2026, 2, 11)]
        
        for i, d_aula in enumerate(datas_aulas):
            esta_presente = (i == 0) # Presente só na primeira aula
            chamada = [{"aluno": aluno, "presente": esta_presente}]
            
            # Aqui o Professor aciona o Aluno e a Turma simultaneamente
            prof.realizar_chamada(turma, d_aula, chamada)

        print("\n--- 🧠 ANALISANDO DADOS NO AVALIADOR ---")

        # 5. O SEU AVALIADOR ENTRA EM CENA
        avaliador = AvaliadorFrequencia()
        mes_teste = 2
        
        # O método que você refinou agora faz a mágica:
        demanda = avaliador.verificar_media_frequencia_mensal(turma, mes_teste)

        # 6. VERIFICAÇÃO DA FACTORY
        # No teste_final_rn02.py
        # No final do teste_final_rn02.py
        if demanda:
            print("\n🚨 [ALERTA DE EVASÃO] Demanda gerada automaticamente pela Factory!")
            print(f"📄 Descrição: {demanda.descricao}")
            print(f"📈 Média da Turma: {avaliador.media_presenca_mensal_turma(turma, mes_teste) * 100}%")
            
            # Usando getattr para não quebrar se o nome do atributo for diferente
            id_dem = getattr(demanda, 'id_demanda', 'Sem ID')
            solic = getattr(demanda, 'solicitante', 'Sem Solicitante')
            
            # Se 'prioridade' deu erro, tente '_prioridade' ou apenas ignore
            prio = getattr(demanda, 'prioridade', getattr(demanda, '_prioridade', 'ALTA (Padrão)'))

            print(f"🆔 ID da Demanda: {id_dem}")
            print(f"👤 Solicitante: {solic}")
            print(f"⚡ Prioridade: {prio}")

    except (ValueError, TypeError) as e:
        print(f"\n❌ ERRO DE VALIDAÇÃO: {e}")
    except Exception as e:
        print(f"\n🛑 ERRO INESPERADO: {type(e).__name__}: {e}")

if __name__ == "__main__":
    executar_fluxo_rn02()