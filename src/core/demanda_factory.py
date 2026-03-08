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
    def criar_demanda(tipo_demanda, solicitante, descricao=None, prioridade="NORMAL", notificador=None,**kwargs):
        id_demanda = str(uuid.uuid4())
        turma_selecionada = kwargs.get("turma")
        nova_demanda = None  # Variável para segurar o objeto antes do return

       # --- BLOCO: DEMANDA PEDAGÓGICA ---
        if tipo_demanda.upper() == "PEDAGOGICA":
            if not turma_selecionada:
                raise ValueError("Contexto Acadêmico Faltando: Informe a turma.")

            # 1. ROTA DE LACUNA (Notas Baixas - RN04)
            # ... (Seu código de lacuna parece ok) ...

            # 2. ROTA DE FREQUÊNCIA (RN02)
            mes_analisado = kwargs.get("mes")
            media_mensal = kwargs.get("media_mensal")

            # Se não mandaram a média pronta, a Factory calcula
            if media_mensal is None:
                if not mes_analisado:
                    raise ValueError("Para calcular frequência, informe o 'mes'.")
                avaliacao = AvaliadorFrequencia()
                media_mensal = avaliacao.media_presenca_mensal_turma(turma_selecionada, mes_analisado)

            # Se a média for baixa, forçamos os parâmetros de Alerta Automático
            if media_mensal < DemandaFactory.config.FREQUENCIA_MINIMA:
                prioridade = "ALTA"
                solicitante_final = "SISTEMA"
                if not descricao:
                    # Calculamos a porcentagem real de faltas (Evasão)
                    percentual_falta = (1 - media_mensal) * 100
                    descricao = f"ALERTA RN02: Turma {turma_selecionada.nome} com {percentual_falta:.1f}% de faltas no mês {mes_analisado}."
            else:
                solicitante_final = solicitante

            # Proteção para o atributo municipio_responsavel
            # Se for "SISTEMA", tentamos pegar o município da própria turma/escola
            municipio = getattr(solicitante_final, 'municipio_responsavel', None)
            if not municipio and hasattr(turma_selecionada, 'escola'):
                municipio = turma_selecionada.escola.municipio

            nova_demanda = DemandaPedagogica(
                id_demanda, 
                descricao, 
                prioridade, 
                solicitante_final, 
                turma_selecionada, 
                media_mensal, 
                municipio,
                "GERAL", 
                "A DEFINIR", 
                [],    # Sem relatório de alunos detalhado aqui
                0.0    # Índice de lacuna é zero para frequência
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
            status_sugerido = avaliador_infra.avaliar_custo(custo_estimado) # existia avaliar_status mudei pq nao ixistia esse metodo no valiadorinflaestrutura

            nova_demanda = DemandaInfraestrutura(
                id_demanda=id_demanda, 
                descricao=descricao, 
                prioridade=prioridade, 
                solicitante=solicitante, 
                custo_estimado=custo_estimado, 
                localizacao_demanda=localizacao_demanda,
                escola=solicitante.escola_associada,
                municipio_responsavel=solicitante.escola_associada.municipio,

            )
            
            nova_demanda.atualizar_status(status_sugerido)

            if "LICITAÇÃO" in status_sugerido:
                nova_demanda.registrar_alerta(f"Custo R$ {custo_estimado} exige licitação (RN03)")
        
        # ---GATILHO DO OBSERVER---
        if nova_demanda and notificador:
            notificador.notificar(nova_demanda, tipo_demanda.upper())

        # --- FINALMENTE O RETURN ---
        if nova_demanda is None:
            raise ValueError(f"Tipo de demanda '{tipo_demanda}' não reconhecido.") 
           
        return nova_demanda