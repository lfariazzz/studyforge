from src.models.demanda import Demanda 

class DemandaPedagogica(Demanda):
    """
    Representa uma demanda gerada automaticamente ou manualmente para tratar
    problemas de frequência e desempenho escolar (lacunas de aprendizado).
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante, 
                 turma, alunos_abaixo_media, frequencia_apurada):
        # 1. Dados básicos enviados para a classe pai
        super().__init__(id_demanda, descricao, prioridade, solicitante)

        
        # 2. Atributos da Demanda
        self.__turma_alvo = turma
        self.__qtd_alunos_em_risco = alunos_abaixo_media
        
        # --- MUDANÇA AQUI ---
        # Recebemos a frequência que o AvaliadorFrequencia calculou
        self.__media_frequencia_apurada = frequencia_apurada
        
        # 3. Pegando o total de alunos direto do objeto turma
        self.__total_alunos = len(turma._alunos_matriculados) if hasattr(turma, '_alunos_matriculados') else 0

    @property
    def indice_lacuna(self):
        """Calcula a proporção de alunos em risco em relação ao total da turma."""
        if self.__total_alunos == 0:
            return 0.0
        return self.__qtd_alunos_em_risco / self.__total_alunos

    @property
    def frequencia_atual(self):
        """Retorna a média de frequência que o Avaliador calculou."""
        return self.__media_frequencia_apurada
    
    def validar_reforco(self):
        """
        Aplica a regra de negócio para decidir se a turma precisa de reforço.
        Regra: Lacuna >= 40% dos alunos OU Frequência < Meta do Município
        """
        solicitante_obj = self.solicitante

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
        # Verifica permissões (Município/Perfil)
        self.validar_usuario(usuario)
        
        if self.validar_reforco(): 
            relatorio = (
                f"--- ANÁLISE PEDAGÓGICA: {self.__turma_alvo.nome} ---\n"
                f"Status: REFORÇO NECESSÁRIO\n"
                f"Frequência Apurada: {self.frequencia_atual * 100:.1f}%\n"
                f"Alunos em Risco: {self.__qtd_alunos_em_risco} ({self.indice_lacuna * 100:.1f}%)"
            )

            self.atualizar_status("REFORÇO NECESSÁRIO")
            self.atualizar(usuario)
        else: 
            self.atualizar_status("REGULAR")
            self.atualizar(usuario)
            
        return True