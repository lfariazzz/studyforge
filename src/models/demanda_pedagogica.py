from src.models.demanda import Demanda 
from src.models.aluno import Aluno
from src.models.turma import Turma
from src.services.avaliador_lacuna import AvaliadorLacuna

class DemandaPedagogica(Demanda):
    """
    Representa uma demanda gerada automaticamente ou manualmente para tratar
    problemas de frequência e desempenho escolar (lacunas de aprendizado).
    """

    def __init__(self, id_demanda, descricao, prioridade, solicitante, 
                 turma, frequencia_apurada, municipio_responsavel, disciplina_alvo, professor, relatorio_alunos, indice_lacuna):
        
        super().__init__(id_demanda, descricao, prioridade, solicitante, municipio_responsavel, "PEDAGÓGICA")

        # 2. Atributos da Demanda
        self.__turma_alvo = turma
        self.__qtd_alunos_em_risco = len(relatorio_alunos)
        self.__professor_responsavel = professor    
        self.__relatorio_alunos = relatorio_alunos
        self.__disciplina_alvo = disciplina_alvo
        self.__indice_lacuna = indice_lacuna
        self.prioridade = prioridade

        # --- MUDANÇA AQUI ---
        # Recebemos a frequência que o AvaliadorFrequencia calculou
        self.__media_frequencia_apurada = frequencia_apurada
        
        # 3. Pegando o total de alunos direto do objeto turma
        self.__total_alunos = len(turma._alunos_matriculados) if hasattr(turma, '_alunos_matriculados') else 0

    @property
    def indice_lacuna(self):
        """Retorna o indice lacuna calculado em AvaliadorLacuna"""
        return self.__indice_lacuna

    @property
    def frequencia_atual(self):
        """Retorna a média de frequência que o Avaliador calculou."""
        return self.__media_frequencia_apurada
    
    @property 
    def disciplina_alvo(self):
        """Retorna a disciplina alvo"""
        return self.__disciplina_alvo


    def validar_reforco(self):
        """
        Aplica a regra de negócio para decidir se a turma precisa de reforço.
        Regra: Lacuna >= 40% dos alunos OU Frequência < Meta do Município
        """
        solicitante_obj = self._solicitante

        # 1. Navega até o objeto Município para buscar as metas
        if hasattr(solicitante_obj, 'municipio_responsavel'):
            municipio = solicitante_obj.municipio_responsavel
        else:
            municipio = solicitante_obj.escola_associada.municipio

        precisa_de_reforço_nota = self.indice_lacuna > municipio.lacuna_maxima_permitida

        precisa_de_reforco_frequencia = self.frequencia_atual < municipio.media_frequencia

        return precisa_de_reforço_nota or precisa_de_reforco_frequencia

    def processar_solicitacao(self, usuario):
        """
        Analisa os dados vindos do Avaliador e define o status final da demanda.
        """
        
        if self.validar_reforco(): 

            lista_formatada = "\n".join([f"  • {aluno['nome']} (Média: {aluno['media']:.1f})" for aluno in self.__relatorio_alunos])

            relatorio = (
            f"\n"
            f"--- RELATÓRIO DE MONITORAMENTO PEDAGÓGICO ---\n"
            f"DATA: {self.registrar_data_demanda_pedagogica()}\n"
            f"PROFESSOR(A): {self.__professor_responsavel}\n"
            f"DISCIPLINA: {self.__disciplina_alvo}\n"
            f"TURMA: {self.__turma_alvo.nome}\n"
            f"----------------------------------------------\n"
            f"STATUS: REFORÇO NECESSÁRIO\n"
            f"FREQUÊNCIA APURADA: {self.__media_frequencia_apurada * 100:.1f}%\n"
            f"ALUNOS EM RISCO: {self.__qtd_alunos_em_risco} de {self.__total_alunos}\n"
            f"ÍNDICE DE LACUNA: {self.indice_lacuna * 100:.1f}%\n"
            f"----------------------------------------------\n"
            f"LISTA DE ESTUDANTES:\n"
            f"{lista_formatada}"    
            f"----------------------------------------------\n"
        )
            
            #Salva o texto no objeto ao invés de dar print. 
            self.alerta_gerado = relatorio

            self.atualizar_status("REFORÇO NECESSÁRIO")
            self.atualizar(usuario)
        else: 
            self.alerta_gerado = "RELATÓRIO: O desempenho e a frequência da turma estão dentro da normalidade"
            self.atualizar_status("REGULAR")
            self.atualizar(usuario)
            
        return True