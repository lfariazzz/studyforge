from src.models.demanda_pedagogica import DemandaPedagogica
from src.models.demanda_infraestrutura import DemandaInfraestrutura
from src.core.configuracoes import Configuracoes
from src.services.avaliador_frequencia import AvaliadorFrequencia
from src.services.avaliador_infraestrutura import AvaliadorInfraestrutura
import uuid

class DemandaFactory:
    """
    Padroniza a criação de demandas do sistema (RN02 e RN03).
    A Factory é 'inteligente': se os dados estatísticos não forem passados via kwargs,
    ela utiliza o AvaliadorFrequencia para calcular os dados em tempo real.
    """
    config = Configuracoes()

    @staticmethod
    def criar_demanda(tipo_demanda, solicitante, descricao=None, prioridade="NORMAL", **kwargs):
        id_demanda = str(uuid.uuid4())
        turma_selecionada = kwargs.get("turma")

        # --- BLOCO: DEMANDA PEDAGÓGICA (Frequência/Evasão) ---
        if tipo_demanda.upper() == "PEDAGOGICA":
            if turma_selecionada:
                # O mês é obrigatório para garantir o determinismo (Lógica do Chamador).
                mes_analisado = kwargs.get("mes")
                
                if mes_analisado:
                    # 1. Captura básica de dados da turma
                    total_alunos = len(turma_selecionada._alunos_matriculados)
                    
                    # 2. Lógica de Contingência: 
                    # Se os dados não vieram no kwargs, a Factory os produz via AvaliadorFrequencia.
                    media_mensal = kwargs.get("media_mensal")
                    alunos_abaixo_media = kwargs.get("alunos_abaixo_media")
                    frequencia_turma = kwargs.get("frequencia_turma")
                    alunos_presentes = kwargs.get("alunos_presentes")

                    avaliacao = AvaliadorFrequencia()

                    # Preenchimento automático de campos faltantes
                    if media_mensal is None:
                        media_mensal = avaliacao.media_presenca_mensal_turma(turma_selecionada, mes_analisado)
                    
                    if alunos_abaixo_media is None:
                        alunos_abaixo_media = avaliacao.qtd_alunos_abaixo_media_frequencia(turma_selecionada, mes_analisado)
                    
                    # frequencia_turma e media_mensal são semanticamente diferentes, mas compartilham o valor do cálculo.
                    if frequencia_turma is None:
                        frequencia_turma = media_mensal

                    if alunos_presentes is None:
                        # NOTA: Henrique, este método precisa ser implementado no AvaliadorFrequencia
                        # para retornar o total absoluto de presenças (assinaturas) no mês.
                        # alunos_presentes = avaliacao.total_presencas_mensais_turma(turma_selecionada, mes_analisado)
                        pass 
                else:
                    raise ValueError("Contexto Temporal Faltando: Informe o mês para análise pedagógica.")

                # 3. Geração Automática de Descrição e Prioridade (Caso gerado pelo Sistema)
                if not descricao:
                    solicitante = "SISTEMA"
                    prioridade = "ALTA"
                    percentual_evasao = (1 - media_mensal) * 100
                    descricao = (f"Alerta de Evasão: Turma {turma_selecionada} com taxa de "
                                f"{percentual_evasao:.1f}% no mês {mes_analisado}.")
                    
                return DemandaPedagogica(id_demanda, descricao, prioridade, solicitante, 
                                        total_alunos, alunos_abaixo_media, frequencia_turma, 
                                        alunos_presentes, turma_selecionada)
            else:
                raise ValueError("Contexto Acadêmico Faltando: Informe a turma para a demanda pedagógica.")
            
            # --- BLOCO: DEMANDA INFRAESTRUTURA (Custos/Manutenção) ---
        elif tipo_demanda.upper() == "INFRAESTRUTURA":
            # 1. Captura os dados específicos enviados via kwargs
            custo_estimado = kwargs.get("custo_estimado", 0)
            localizacao_demanda = kwargs.get("localizacao_demanda")

            # 2. Identifica o município para carregar a regra correta (15k? 50k?)
            # Verificamos se o solicitante tem o atributo direto ou via escola
            if hasattr(solicitante, 'municipio_responsavel'):
                mun_nome = solicitante.municipio_responsavel.nome
            else:
                mun_nome = solicitante.escola_associada.municipio.nome

            # 3. Instancia o "Juiz" (Avaliador) para esse município específico
            avaliador = AvaliadorInfraestrutura(mun_nome)

            # 4. O Coração da RN03: O Avaliador decide o status baseado no custo
            # Se o custo >= LIMITE_CUSTO_DEMANDA, ele retorna "EM LICITAÇÃO"
            status_sugerido = avaliador.avaliar_status(custo_estimado)

            # 5. Criação do objeto Real (Instanciação)
            # Passamos os dados básicos e o "INFRAESTRUTURA" para o super da mãe
            nova_demanda = DemandaInfraestrutura(
                id_demanda=id_demanda, 
                descricao=descricao, 
                prioridade=prioridade, 
                solicitante=solicitante, 
                custo_estimado=custo_estimado, 
                localizacao_demanda=localizacao_demanda
            )
            
            # 6. Aplica o status definido pelo Avaliador
            nova_demanda.atualizar_status(status_sugerido)

            if "LICITAÇÃO" in status_sugerido:
                nova_demanda.registrar_alerta(f"Custo R$ {custo_estimado} exige licitação (RN03)")
            # 7. Entrega o objeto pronto
            return nova_demanda