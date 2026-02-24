from src.core.configuracoes import Configuracoes
from src.core.demanda_factory import DemandaFactory
class AvaliadorFrequencia:
    """Classe responsável por monitorar a frequência escolar e validar a RN02.

    Esta classe atua como o motor de inteligência que analisa diários de classe 
    e registros de presença, identificando riscos de evasão escolar baseados nos 
    limites definidos nas configurações globais do sistema."""

    def __init__(self):
        """Inicializa o avaliador capturando as regras vigentes no sistema."""

        config = Configuracoes()
        self.frequencia_minima = config.FREQUENCIA_MINIMA

    def aulas_mes_turma(self, turma, mes):
        """Calcula a quantidade de aulas em um mês de uma turma,
        permitindo saber a presença individual e coletiva mensal."""

        total_aulas_mes = 0
        for aula in turma._diario_de_classe:
            if aula["data"].month == mes:
                total_aulas_mes += 1

        return total_aulas_mes
    

    def presencas_mes_aluno(self, aluno, mes):
        """Calcula a quantidade de presenças em determinado mês de um aluno"""

        total_presencas_mes_aluno = 0
        for presenca in aluno.presenca:
            if presenca["data"].month == mes and presenca["presenca"] is True:
                total_presencas_mes_aluno += 1

        return total_presencas_mes_aluno

    def media_presenca_mensal_aluno(self, aluno, turma, mes):
        """Calcula o percentual de frequência individual de um aluno."""

        aulas_mes_turma = self.aulas_mes_turma(turma,mes)
        if aulas_mes_turma != 0:
            return (self.presencas_mes_aluno(aluno, mes)) / aulas_mes_turma
        else:
            raise ValueError ("Não existem aulas registradas")

    def media_presenca_mensal_turma(self, turma, mes):
        """Calcula presença média de todos os alunos de uma turma em um mês"""

        total_alunos = len(turma._alunos_matriculados)
        somatorio_media_alunos = 0
        for aluno in turma._alunos_matriculados:
           somatorio_media_alunos += self.media_presenca_mensal_aluno(aluno, turma, mes)
        
        if total_alunos != 0:
            return somatorio_media_alunos / total_alunos
        else:
            raise ValueError ("Não existem alunos registradas")

    def qtd_alunos_abaixo_media_frequencia(self, turma, mes):
        """Calcula a quantidade de alunos que ficaram com presença abaixo da mínima em um mês"""

        qtd_media_abaixo = 0
        for aluno in turma._alunos_matriculados:
            if self.media_presenca_mensal_aluno(aluno, turma, mes) < self.frequencia_minima:
                qtd_media_abaixo +=1
        return qtd_media_abaixo
            
    
    def verificar_media_frequencia_mensal(self, turma, mes):
        """Valida a RN02, verificando a media de frequencia mensal da turma e 
        gerando uma demanda automaticamente caso esteja abaixo do limite"""

        media_mensal = self.media_presenca_mensal_turma(turma, mes)
        if media_mensal < self.frequencia_minima:
            print(f"Média de presença mensal da turma {media_mensal}\n Gerando demanda pedagógica...")
            alunos_abaixo_media = self.qtd_alunos_abaixo_media_frequencia(turma, mes)
            demanda_evasao = DemandaFactory.criar_demanda("PEDAGOGICA", "SISTEMA", None,turma=turma, 
                                               media_mensal=media_mensal, alunos_abaixo_media=alunos_abaixo_media)
            return demanda_evasao