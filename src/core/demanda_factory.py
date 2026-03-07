from src.models.demanda_pedagogica import DemandaPedagogica
from src.models.demanda_infraestrutura import DemandaInfraestrutura
from src.core.configuracoes import Configuracoes
from src.services.avaliador_frequencia import AvaliadorFrequencia
from src.services.avaliador_infraestrutura import AvaliadorInfraestrutura
import uuid

class DemandaFactory:
    """
    Padroniza a criação de demandas do sistema (RN02, RN03 e RN04).
    """
    config = Configuracoes()

    @staticmethod
    def criar_demanda(tipo_demanda, solicitante, descricao=None, prioridade="NORMAL", **kwargs):
        id_demanda = str(uuid.uuid4())
        turma_selecionada = kwargs.get("turma")

        # --- BLOCO: DEMANDA PEDAGÓGICA ---
        if tipo_demanda.upper() == "PEDAGOGICA":
            if not turma_selecionada:
                raise ValueError("Contexto Acadêmico Faltando: Informe a turma.")

            # 1. ROTA DE LACUNA (Notas Baixas - RN04)
            relatorio_alunos = kwargs.get("relatorio_alunos")
            if relatorio_alunos is not None:
                # Recupera o índice calculado pelo AvaliadorLacuna
                indice = kwargs.get("indice_lacuna", 0.0)
                
                return DemandaPedagogica(
                    id_demanda, 
                    descricao, 
                    prioridade, 
                    solicitante, 
                    turma_selecionada, 
                    kwargs.get("frequencia_turma", 1.0), 
                    getattr(solicitante, 'municipio_responsavel', None),
                    kwargs.get("disciplina_alvo", "N/A"), 
                    kwargs.get("professor", "N/A"), 
                    relatorio_alunos,
                    indice # <--- Agora passando o 11º argumento
                )

            # 2. ROTA DE FREQUÊNCIA (Original - RN02)
            mes_analisado = kwargs.get("mes")
            if not mes_analisado:
                raise ValueError("Contexto Temporal Faltando: Informe o mês ou o relatório de alunos.")

            avaliacao = AvaliadorFrequencia()
            
            media_mensal = kwargs.get("media_mensal")
            if media_mensal is None:
                media_mensal = avaliacao.media_presenca_mensal_turma(turma_selecionada, mes_analisado)
            
            if not descricao:
                percentual_evasao = (1 - media_mensal) * 100
                descricao = f"Alerta de Evasão: Turma {turma_selecionada.nome} com {percentual_evasao:.1f}% no mês {mes_analisado}."
                prioridade = "ALTA"
                solicitante = "SISTEMA"

            return DemandaPedagogica(
                id_demanda, 
                descricao, 
                prioridade, 
                solicitante, 
                turma_selecionada, 
                media_mensal, 
                getattr(solicitante, 'municipio_responsavel', None),
                "GERAL", 
                "A DEFINIR", 
                [],   # Sem relatório de alunos nesta rota
                0.0   # Índice de lacuna de notas é 0.0 aqui
            )

        # --- BLOCO: DEMANDA INFRAESTRUTURA ---
        elif tipo_demanda.upper() == "INFRAESTRUTURA":
            custo_estimado = kwargs.get("custo_estimado", 0)
            localizacao_demanda = kwargs.get("localizacao_demanda")

            if hasattr(solicitante, 'municipio_responsavel'):
                mun_nome = solicitante.municipio_responsavel.nome
            else:
                mun_nome = solicitante.escola_associada.municipio.nome

            avaliador_infra = AvaliadorInfraestrutura(mun_nome)
            status_sugerido = avaliador_infra.avaliar_status(custo_estimado)

            nova_demanda = DemandaInfraestrutura(
                id_demanda=id_demanda, 
                descricao=descricao, 
                prioridade=prioridade, 
                solicitante=solicitante, 
                custo_estimado=custo_estimado, 
                localizacao_demanda=localizacao_demanda
            )
            
            nova_demanda.atualizar_status(status_sugerido)

            if "LICITAÇÃO" in status_sugerido:
                nova_demanda.registrar_alerta(f"Custo R$ {custo_estimado} exige licitação (RN03)")
            
            return nova_demanda