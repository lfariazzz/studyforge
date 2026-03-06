from src.core.configuracoes import Configuracoes
from src.models.turma import Turma 
from src.models.aluno import Aluno


class AvaliadorLacuna:
    """
    Classe criada para atender a RN04, analisando o desempenho acadêmico dos alunos 
    e disparando alertas automáticos. 
    """
    def identificar_alunos_com_lacuna(self, turma):
        alunos_identificados = []

        for aluno in turma.alunos_matriculados:
            notas_do_aluno = aluno._notas 
            
            if notas_do_aluno:
                for disciplina, lista_notas in notas_do_aluno.items():
                    if lista_notas:
                        # Calcula a média daquela matéria específica
                        media_disciplina = sum(lista_notas) / len(lista_notas)
                        
                        if media_disciplina < 7.0:
                            detalhe_lacuna = {
                                "Aluno": aluno.nome,
                                "Disciplina": disciplina,
                                "Media": round(media_disciplina, 2)
                            }
                            alunos_identificados.append(detalhe_lacuna)
                        