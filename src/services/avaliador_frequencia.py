from src.core.configuracoes import Configuracoes

class AvaliadorFrequencia:
    def __init__(self):
        config = Configuracoes()
        self.frequencia_minima = config.FREQUENCIA_MINIMA

    def aulas_mes_turma(self, turma, mes):
        """Busca no diário de classe da turma (Objetos Diario)"""
        total_aulas_mes = 0
        for aula in turma._diario_de_classe:
            if aula.data.month == mes:
                total_aulas_mes += 1
        return total_aulas_mes

    def presencas_mes_aluno(self, aluno, mes, turma):
        """Calcula presenças usando os novos objetos Frequencia."""
        total_presencas = 0
        
        for freq in aluno.presencas:
            # Cruzamento pelo id_diario para pegar a data da aula
            aula = next((a for a in turma._diario_de_classe if a.id_diario == freq.id_diario), None)
            
            if aula and aula.data.month == mes and freq.status == 'PRESENTE':
                total_presencas += 1
        
        return total_presencas

    def media_presenca_mensal_aluno(self, aluno, turma, mes):
        """Calcula o percentual de frequência individual de um aluno."""
        aulas_mes_turma = self.aulas_mes_turma(turma, mes)
        
        if aulas_mes_turma != 0:
            return self.presencas_mes_aluno(aluno, mes, turma) / aulas_mes_turma
        else:
            return 1.0

    def media_presenca_mensal_turma(self, turma, mes):
        """Calcula presença média de todos os alunos de uma turma em um mês"""
        total_alunos = len(turma._alunos_matriculados)
        somatorio_media_alunos = 0
        
        for aluno in turma._alunos_matriculados:
           somatorio_media_alunos += self.media_presenca_mensal_aluno(aluno, turma, mes)
        
        if total_alunos != 0:
            return somatorio_media_alunos / total_alunos
        else:
            raise ValueError("Não existem alunos registrados nesta turma")

    def qtd_alunos_abaixo_media_frequencia(self, turma, mes):
        """Calcula a quantidade de alunos abaixo da mínima"""
        qtd_media_abaixo = 0
        for aluno in turma._alunos_matriculados:
            if self.media_presenca_mensal_aluno(aluno, turma, mes) < self.frequencia_minima:
                qtd_media_abaixo += 1
        return qtd_media_abaixo
    
    def verificar_media_frequencia_mensal(self, turma, mes):
        """Valida a RN02 e gera demanda via Factory"""
        from src.core.demanda_factory import DemandaFactory

        media_mensal = self.media_presenca_mensal_turma(turma, mes)
        
        if media_mensal < self.frequencia_minima:
            print(f"Média ({media_mensal*100:.1f}%) abaixo do limite ({self.frequencia_minima*100:.1f}%)")
            
            alunos_abaixo_media = self.qtd_alunos_abaixo_media_frequencia(turma, mes)
            
            return DemandaFactory.criar_demanda(
                tipo_demanda="PEDAGOGICA", 
                solicitante="SISTEMA", 
                descricao=None,
                turma=turma, 
                media_mensal=media_mensal, 
                mes=mes,
                alunos_abaixo_media=alunos_abaixo_media
            )
        return None