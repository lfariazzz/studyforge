from src.models.demanda import Demanda 
from src.models.aluno import Aluno
from src.models.turma import Turma
from src.services.avaliador_lacuna import AvaliadorLacuna

class DemandaPedagogica(Demanda):
    """
    Representa uma demanda gerada automaticamente ou manualmente para tratar
    problemas de frequência e desempenho escolar (lacunas de aprendizado).
    """

    def __init__(self, id_demanda, descricao, prioridade, solicitante,  municipio_responsavel,
                 turma, frequencia_apurada, disciplina_alvo, professor, relatorio_alunos, indice_lacuna,
                 criado_em=None, editor=None, data_alteracao=None, alerta=None):
        
        super().__init__(id_demanda, descricao, prioridade, solicitante, municipio_responsavel, "PEDAGÓGICA", "PENDENTE", criado_em, editor, data_alteracao, alerta)

        # 2. Atributos da Demanda
        self._turma_alvo = turma
        self._qtd_alunos_em_risco = len(relatorio_alunos)
        self._professor_responsavel = professor    
        self._relatorio_alunos = relatorio_alunos
        self._disciplina_alvo = disciplina_alvo
        self._indice_lacuna = indice_lacuna

        # --- MUDANÇA AQUI ---
        # Recebemos a frequência que o AvaliadorFrequencia calculou
        self._media_frequencia_apurada = frequencia_apurada
        
        # 3. Pegando o total de alunos direto do objeto turma
        self._total_alunos = len(turma._alunos_matriculados) if hasattr(turma, '_alunos_matriculados') else 0

    @property
    def indice_lacuna(self):
        """Retorna o indice lacuna calculado em AvaliadorLacuna"""
        return self._indice_lacuna

    @property
    def frequencia_atual(self):
        """Retorna a média de frequência que o Avaliador calculou."""
        return self._media_frequencia_apurada
    
    @property 
    def disciplina_alvo(self):
        """Retorna a disciplina alvo"""
        return self._disciplina_alvo


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

            lista_formatada = "\n".join([f"  • {aluno['nome']} (Média: {aluno['media']:.1f})" for aluno in self._relatorio_alunos])

            relatorio = (
            f"\n"
            f"--- RELATÓRIO DE MONITORAMENTO PEDAGÓGICO ---\n"
            f"DATA: {self.registrar_data_demanda()}\n"
            f"PROFESSOR(A): {self._professor_responsavel}\n"
            f"DISCIPLINA: {self._disciplina_alvo}\n"
            f"TURMA: {self._turma_alvo.nome}\n"
            f"----------------------------------------------\n"
            f"STATUS: REFORÇO NECESSÁRIO\n"
            f"FREQUÊNCIA APURADA: {self._media_frequencia_apurada * 100:.1f}%\n"
            f"ALUNOS EM RISCO: {self._qtd_alunos_em_risco} de {self._total_alunos}\n"
            f"ÍNDICE DE LACUNA: {self.indice_lacuna * 100:.1f}%\n"
            f"----------------------------------------------\n"
            f"LISTA DE ESTUDANTES:\n"
            f"{lista_formatada}"    
            f"----------------------------------------------\n"
        )
            
            #Salva o texto no objeto ao invés de dar print. 
            self._alerta_auditoria = relatorio

            self.atualizar_status("REFORÇO NECESSÁRIO")
            self.atualizar(usuario)
        else: 
            self._alerta_auditoria = "RELATÓRIO: O desempenho e a frequência da turma estão dentro da normalidade"
            self.atualizar_status("REGULAR")
            self.atualizar(usuario)
            
        return True
    
    def to_dict_especifico(self):
        return{
            "id_demanda": self._id_demanda,
            "id_turma": self._turma_alvo.id_turma if self._turma_alvo else None,
            "frequencia_apurada": self._media_frequencia_apurada,
            "disciplina_alvo": self._disciplina_alvo,
            "id_professor": self._professor_responsavel.id_usuario if self._professor_responsavel else None,
            "relatorio_alunos": self._relatorio_alunos,
            "indice_lacuna": self._indice_lacuna,
        }