from src.models.demanda import Demanda 

class DemandaPedagogica(Demanda):
    """
    Representa uma demanda gerada automaticamente ou manualmente para tratar
    problemas de frequência e desempenho escolar (lacunas de aprendizado).
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante, 
                 turma, media_mensal, alunos_abaixo_media):
        # 1. Dados básicos enviados para a classe pai
        super().__init__(id_demanda, descricao, prioridade, solicitante)
        
        # 2. Atributos "Casados" com o AvaliadorFrequencia
        self.__turma_alvo = turma
        self.__media_frequencia = media_mensal  # Recebe o valor (ex: 0.70 para 70%)
        self.__qtd_alunos_em_risco = alunos_abaixo_media
        
        # 3. Pegando o total de alunos direto do objeto turma
        self.__total_alunos = len(turma._alunos_matriculados) if hasattr(turma, '_alunos_matriculados') else 0

    """Os propertys responsáveis por tornar possível a visualização dos atributos do método construtor desta classe"""
    @property
    def indice_lacuna(self):
        """Calcula a proporção de alunos em risco em relação ao total da turma."""
        if self.__total_alunos == 0:
            return 0.0
        return self.__qtd_alunos_em_risco / self.__total_alunos

    @property
    def frequencia_atual(self):
        """Retorna a média de frequência que o Avaliador calculou."""
        return self.__media_frequencia
    
    def validar_reforco(self):
        """
        Aplica a regra de negócio para decidir se a turma precisa de reforço.
        Regra: Lacuna >= 40% dos alunos OU Frequência < 75%
        """
        # Se 40% ou mais da turma está abaixo da média de notas
        regra_nota = self.indice_lacuna >= 0.4 
        
        # Se a frequência da turma for menor que 75% (0.75)
        # Nota: Ajustei para '<' pois frequência baixa é o que gera reforço
        regra_presenca = self.__media_frequencia < 0.75 

        return regra_nota or regra_presenca

    def processar_solicitacao(self, usuario):
        """
        Analisa os dados vindos do Avaliador e define o status final da demanda.
        """
        # Verifica permissões (Município/Perfil)
        self.validar_usuario(usuario)
        
        if self.validar_reforco(): 
            print(f"--- ANÁLISE PEDAGÓGICA: {self.__turma_alvo.nome} ---")
            print(f"Frequência Mensal: {self.__media_frequencia * 100:.1f}%")
            print(f"Alunos em Risco: {self.__qtd_alunos_em_risco} ({self.indice_lacuna * 100:.1f}%)")

            self.status = "REFORÇO NECESSÁRIO"
            self.atualizar(usuario)
        else: 
            self.status = "REGULAR"
            self.atualizar(usuario)
            
        return True
