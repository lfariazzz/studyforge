from src.core.configuracoes import Configuracoes
from src.models.turma import Turma 
from src.models.aluno import Aluno
from src.models.nota import Nota 

class AvaliadorLacuna:
    """
    Classe criada para atender a RN04, analisando o desempenho acadêmico dos alunos 
    e disparando alertas automáticos. 
    """
    def __init__(self):
        self.indice_lacuna = 0.0

    def validar_reforco(self, turma, municipio, disciplina: str):
        
        total_alunos = len(turma._alunos_matriculados)
        if total_alunos == 0:
            return False, 0.0, []
        
        # 1. Filtra as notas da disciplina usando a nota_de_corte do OBJETO municipio
        alunos_em_risco = [n for n in turma.notas 
                        if n.disciplina == disciplina and n.valor < municipio.nota_de_corte]

        # 2. Calcula o índice de lacuna (porcentagem de alunos abaixo da média)
        total_alunos = len(turma._alunos_matriculados)
        self.indice_lacuna = len(alunos_em_risco) / total_alunos if total_alunos > 0 else 0

        # 3. Gera o relatório formatado
        relatorio = [
            {"nome": f"Aluno ID {n.id_aluno}", "media": n.valor, "disciplina": n.disciplina}
            for n in alunos_em_risco
        ]

        # 4. Compara o índice com a tolerância do município
        precisa_reforco = self.indice_lacuna > municipio.lacuna_maxima_permitida

        return precisa_reforco, self.indice_lacuna, relatorio