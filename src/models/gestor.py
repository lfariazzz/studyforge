from src.models.usuario import Usuario

class Gestor(Usuario):
    def __init__(self, id_usuario, nome, cpf, email, senha, telefone, data_nascimento, escola_associada):
        """
        Inicializa um novo gestor no sistema StudyForge.
        
        Args:
            id_usuario (int): Identificador unico do gestor.
            nome (str): Nome completo do gestor.
            cpf (str): CPF do gestor (11 digitos numericos).
            email (str): Endereco de email do gestor.
            senha (str): Senha de acesso (minimo 8 caracteres).
            telefone (str): Numero de telefone (10 ou 11 digitos).
            data_nascimento (str): Data de nascimento no formato DD/MM/AAAA.
            escola_associada (Escola): Objeto da escola que o gestor administra.
                                       Nao pode ser alterado apos a inicializacao.
        """
        super().__init__(id_usuario, nome, cpf, email, senha, telefone, data_nascimento, "GESTOR")

        self.escola_associada = escola_associada

    # -----------------
    # GETTERS E SETTERS
    # -----------------

    @property
    def escola_associada(self):
        return self._escola_associada

    @escola_associada.setter
    def escola_associada(self, valor):
        from src.models.escola import Escola
        if hasattr(self, '_escola_associada') and self._escola_associada is not None:
            raise PermissionError("Erro: A escola associada não pode ser alterada diretamente.")

        if valor is not None and not isinstance(valor, Escola):
            raise TypeError("Erro: Escola associada deve ser um objeto da classe Escola!")
        
        self._escola_associada = valor
    #-------
    #METODOS
    #-------
    
    def get_permissao(self):
        """
        Retorna as permissoes do gestor no sistema.
        
        Returns:
            list: Lista contendo as permissoes do gestor:
                  - VISUALIZAR_PERFIL: Acessar seu proprio perfil
                  - VER_ESTATISTICA_ESCOLA: Consultar relatorios da escola
                  - REALIZAR_CADASTRO: Registrar alunos e professores
                  - ENVIAR_MENSAGEM: Publicar comunicados no mural
                  - REALIZAR_SOLICITACAO_VERBA: Solicitar recursos para a escola
                  - ADMINISTRAR_SOLICITACOES_ESCOLA: Gerenciar demandas enviadas
                  - GERENCIAR_DADOS_ESCOLA: Atualizar dados estruturais
                  - ALTERAR_STATUS_USUARIO: Ativar/desativar usuarios
        """
        return ["VISUALIZAR_PERFIL", "VER_ESTATISTICA_ESCOLA", "REALIZAR_CADASTRO", "ENVIAR_MENSAGEM", 
                "REALIZAR_SOLICITACAO_VERBA", "ADMINISTRAR_SOLICITACOES_ESCOLA", "GERENCIAR_DADOS_ESCOLA", "ALTERAR_STATUS_USUARIO"]
    
    def exibir_perfil(self):
        """
        Exibe o perfil completo do gestor.
        
        Implementacao do metodo abstrato da classe Usuario que retorna uma string
        formatada com os dados principais do gestor, incluindo identificador,
        escola associada, email e status da conta.
        
        Returns:
            str: String formatada contendo informacoes do perfil do gestor.
        """
        nome_escola = self.escola_associada.nome if hasattr(self.escola_associada, 'nome') else "Não informada"
        status_conta = "Ativa" if self._status else "Inativa/Suspensa"

        return (
            f"\n" + "="*40 + "\n"
            f"          PERFIL DO GESTOR\n"
            f"="*40 + "\n"
            f"Nome: {self.nome}\n"
            f"ID Identificador: {self.id_usuario}\n"
            f"Escola: {nome_escola}\n"
            f"E-mail: {self.email}\n"
            f"Status: {status_conta}\n"
            f"="*40
        )
    
    def _get_total_alunos(self):
        """
        Calcula o total de alunos matriculados em todas as turmas da escola.
        
        Metodo auxiliar interno que centraliza o calculo do numero total de alunos
        da escola associada, somando alunos de todas as turmas.
        
        Returns:
            int: Total de alunos matriculados na escola.
        """
        return sum(len(t.alunos_matriculados) for t in self.escola_associada._turmas_existentes)

    def ver_estatisticas(self):
        """
        Gera um relatorio estatistico completo da escola associada.
        
        Consolida dados de pessoas (alunos e professores), turmas, infraestrutura
        e financas, fornecendo uma visao geral da situacao da unidade escolar.
        
        Returns:
            dict: Dicionario contendo:
                  - escola: Nome da escola
                  - total_alunos: Numero total de alunos matriculados
                  - total_professores: Numero total de professores empregados
                  - total_turmas: Numero total de turmas
                  - media_frequencia_geral: Media de frequencia de toda a escola
                  - capacidade_utilizada_pct: Percentual de utilizacao da capacidade
                  - verba_disponivel: Recurso financeiro disponivel
        """
        if not self._status:
            return "Erro: Gestor inativo não tem acesso aos dados da unidade."

        escola = self.escola_associada
        total_alunos = self._get_total_alunos()

        capacidade = escola.capacidade_infraestrutura
        ocupacao = (total_alunos / capacidade) * 100 if capacidade > 0 else 0

        return {
            "escola": escola.nome,
            "total_alunos": total_alunos,
            "total_professores": len(escola._professores_empregados),
            "total_turmas": len(escola._turmas_existentes),
            "media_frequencia_geral": escola.gerar_relatorio_frequencia(),
            "capacidade_utilizada_pct": round(ocupacao, 2),
            "verba_disponivel": escola.verba_disponivel_escola
        }

    def realizar_cadastro(self, usuario, turma=None):
        """
        Registra um novo usuario (aluno ou professor) na unidade escolar.
        
        Permite que o gestor cadastre alunos em turmas especificas ou vincule
        professores a escola e, opcionalmente, a turmas.
        
        Args:
            usuario (Aluno|Professor): Objeto do usuario a ser cadastrado.
            turma (Turma, optional): Turma para vincular. Para alunos e necessaria,
                                     para professores e opcional. Defaults to None.
        
        Returns:
            str: Mensagem de sucesso ou descricao do erro ocorrido.
        
        Raises (implicitamente via retorno):
            - Capacidade da escola atingida para alunos
            - Turma invalida ou nao informada para alunos
            - Professor ja cadastrado na unidade
        """
        from src.models.aluno import Aluno
        from src.models.professor import Professor
        
        if not self._status:
            raise PermissionError("Erro: Gestor inativo não pode realizar cadastros.")
        
        if isinstance(usuario, Aluno):
            if self._get_total_alunos() >= self.escola_associada.capacidade_infraestrutura:
                return "Erro: Capacidade física total da escola atingida!"
            
            if turma and turma in self.escola_associada._turmas_existentes:
                if turma.adicionar_aluno(usuario):
                    return f"Aluno {usuario.nome} cadastrado com sucesso na turma {turma.nome}."
                return "Erro: A capacidade da turma específica foi atingida."
            return "Erro: Turma inválida ou não informada."
        
        elif isinstance(usuario, Professor):
            if usuario not in self.escola_associada._professores_empregados:
                self.escola_associada._professores_empregados.append(usuario)
                
                if turma and turma in self.escola_associada._turmas_existentes:
                    turma.adicionar_professor(usuario)
                    return f"Professor {usuario.nome} vinculado à escola e à turma {turma.nome}."
                
                return f"Professor {usuario.nome} vinculado à escola (sem turma atribuída)."
            return "Erro: Professor já está cadastrado nesta unidade."

    def enviar_mensagem(self, titulo, conteudo):
        """
        Publica um comunicado oficial no mural da escola associada.
        
        Permite que o gestor compartilhe noticias, avisos e comunicados importantes
        no mural oficial da escola, tornando acessiveis a todos os usuarios.
        
        Args:
            titulo (str): Titulo do comunicado (obrigatorio).
            conteudo (str): Conteudo da mensagem (obrigatorio).
        
        Returns:
            str: Mensagem indicando sucesso ou erro da operacao.
        """
        if not self._status:
            return "Erro: Gestor inativo não pode enviar comunicados."
        
        if not titulo or not conteudo:
            return "Erro: A mensagem deve conter título e conteúdo."
        sucesso = self.escola_associada.adicionar_noticia(titulo, conteudo, self.nome)
        
        if sucesso:
            return f"Comunicado '{titulo}' publicado com sucesso no mural da escola!"
        return "Erro ao publicar mensagem."
    
    def realizar_solicitacao(self, tipo_demanda, descricao=None, prioridade="NORMAL", **kwargs):
        """
        Interface do gestor com a DemandaFactory para criar solicitacoes.
        
        O gestor especifica o tipo de demanda desejada (pedagogica ou infraestrutura)
        e a Factory lida com a complexidade da criacao da demanda apropriada.
        
        Args:
            tipo_demanda (str): Tipo de demanda (ex: 'INFRAESTRUTURA', 'PEDAGOGICA').
            descricao (str, optional): Descricao detalhada da solicitacao. Defaults to None.
            prioridade (str, optional): Nivel de prioridade (NORMAL, ALTA, CRITICA). 
                                        Defaults to "NORMAL".
            **kwargs: Argumentos adicionais especificos do tipo de demanda.
        
        Returns:
            str: Mensagem com status da criacao da demanda ou descricao do erro.
        """
        from src.core.demanda_factory import DemandaFactory

        if not self._status:
            return "Erro: Gestor inativo não pode realizar solicitações."

        try:
            nova_demanda = DemandaFactory.criar_demanda(
                tipo_demanda=tipo_demanda,
                solicitante=self,
                descricao=descricao,
                prioridade=prioridade,
                **kwargs
        )

            if nova_demanda:

                self.escola_associada._solicitacoes_enviadas.append(nova_demanda)
            
                tipo_formatado = tipo_demanda.replace("_", " ").title()
                return f"Sucesso: {tipo_formatado} registrada (ID: {nova_demanda.id_demanda[:8]}). Status: {nova_demanda.status}"

        except (ValueError, Exception) as e:
            return f"Falha na solicitação: {str(e)}"

        return "Erro: Não foi possível processar a demanda."

    
    def administrar_solicitacoes(self):
        """
        Lista e detalha o status de todas as demandas enviadas pela unidade escolar.
        
        Fornece um painel com resumo de todas as solicitacoes (infraestrutura e pedagogicas)
        enviadas pela escola, permitindo monitoramento do status e acompanhamento.
        
        Returns:
            str: Relatorio formatado com lista de demandas ou mensagem indicando
                 que nenhuma solicitacao foi registrada.
        """
        if not self._status:
            return "Acesso negado: Gestor inativo."
        
        demandas = getattr(self.escola_associada, '_solicitacoes_enviadas', [])

        if not demandas:
            return f"Nenhuma solicitação registrada para a escola {self.escola_associada.nome}."

        relatorio = [f"=== PAINEL DE SOLICITAÇÕES: {self.escola_associada.nome} ==="]
        
        for d in demandas:
            tipo = "🏗️ INFRA" if "Infraestrutura" in str(type(d)) else "📚 PEDAG"

            item = (f"[{tipo}] ID: {d.id_demanda[:8]}... | "
                    f"Status: {d.status} | "
                    f"Prioridade: {getattr(d, '_Demanda__prioridade', 'N/A')}")
            
            relatorio.append(item)
            relatorio.append(f"   Descrição: {d.descricao[:50]}...")
            relatorio.append("-" * 40)

        return "\n".join(relatorio)
            
    def gerenciar_escola(self, nova_capacidade=None):
        """
        Permite ao gestor atualizar dados estruturais da escola associada.
        
        Autoriza mudancas importantes na configuracao da unidade escolar, como
        atualizacao da capacidade fisica de alunos que a escola pode receber.
        
        Args:
            nova_capacidade (int, optional): Nova capacidade maxima de alunos.
                                             Deve ser >= ao numero de alunos atuais.
                                             Defaults to None.
        
        Returns:
            str: Mensagem confirmando a alteracao ou descrevendo o erro ocorrido.
        """
        if not self._status:
            return "Erro: Gestor inativo não pode gerenciar a unidade."

        escola = self.escola_associada

        if nova_capacidade is not None:
            total_alunos = self._get_total_alunos()
            
            if nova_capacidade < total_alunos:
                return (f"Erro: A nova capacidade ({nova_capacidade}) é menor que "
                        f"o número de alunos matriculados ({total_alunos}).")
            
            escola.capacidade_infraestrutura = nova_capacidade
            return f"Sucesso: Capacidade da escola {escola.nome} atualizada para {nova_capacidade}."

        return "Nenhuma alteração solicitada para a escola."
    
    def alterar_status_usuario(self, usuario, novo_status: bool):
        """
        Permite ao gestor ativar ou desativar usuarios da sua unidade escolar.
        
        O gestor pode alterar o status de alunos e professores vinculados a sua escola,
        habilitando ou suspendendo suas contas de acesso ao sistema.
        
        Args:
            usuario (Aluno|Professor): Objeto do usuario cuja conta sera alterada.
            novo_status (bool): True para ativar, False para desativar a conta.
        
        Returns:
            str: Mensagem confirmando a alteracao ou descrevendo o erro/falta de permissao.
        
        Note:
            - Apenas alunos e professores podem ter status alterado
            - O usuario deve estar vinculado a escola do gestor
        """
        from src.models.aluno import Aluno
        from src.models.professor import Professor

        if not self._status:
            return "Erro: Gestor inativo não pode realizar alterações de status."

        if not isinstance(usuario, (Aluno, Professor)):
            return "Erro: O gestor só possui permissão para alterar status de Alunos e Professores."

        if isinstance(usuario, Professor) and usuario not in self.escola_associada._professores_empregados:
            return "Erro: Este professor não está vinculado à sua unidade escolar."
        
        if isinstance(usuario, Aluno):
            aluno_na_escola = any(usuario in t.alunos_matriculados for t in self.escola_associada._turmas_existentes)
            if not aluno_na_escola:
                return "Erro: Este aluno não está matriculado em nenhuma turma desta unidade."

        usuario.status = novo_status
        acao = "ativado" if novo_status else "desativado"
        
        return f"Sucesso: O usuário {usuario.nome} foi {acao} com sucesso."
    
    def to_dict_especifico(self):
        """
        Exporta os dados especificos do gestor em formato de dicionario.
        
        Retorna um dicionario contendo os atributos especificos da classe Gestor,
        utilizando como base os dados da classe pai (Usuario) e adicionando o contexto
        da escola administrada.
        
        Returns:
            dict: Dicionario com id_usuario e id_escola do gestor.
        """
        return {
            "id_usuario": self._id_usuario,
            "id_escola": self._escola_associada.id_escola 
        }