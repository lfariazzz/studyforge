from src.models.usuario import Usuario

class Secretario(Usuario):
    def __init__(self, id_usuario,  nome, cpf, email, senha, telefone, data_nascimento,
                 municipio_responsavel, departamento):
        """
        Inicializa um novo secretario no sistema StudyForge.
        
        Args:
            id_usuario (int): Identificador unico do secretario.
            nome (str): Nome completo do secretario.
            cpf (str): CPF do secretario (11 digitos numericos).
            email (str): Endereco de email do secretario.
            senha (str): Senha de acesso (minimo 8 caracteres).
            telefone (str): Numero de telefone (10 ou 11 digitos).
            data_nascimento (str): Data de nascimento no formato DD/MM/AAAA.
            municipio_responsavel (Municipio): Objeto do municipio administrado pelo secretario.
            departamento (str): Departamento de atuacao (ex: EDUCAÇÃO, FINANÇAS).
        """
        super().__init__(id_usuario, nome, cpf, email, senha, telefone, data_nascimento, "SECRETARIO")

        self.municipio_responsavel = municipio_responsavel
        self.departamento = departamento

    #-----------------
    #GETTERS E SETTERS
    #-----------------

    @property
    def municipio_responsavel(self):
        """Retorna o objeto Municipio ao qual o secretário está vinculado."""
        return self._municipio_responsavel
    
    @municipio_responsavel.setter
    def municipio_responsavel(self, valor):
        """
        Garante que o secretário só seja vinculado a uma instância válida de Municipio.
        Isso impede que um ID solto ou string seja atribuído por erro.
        """
        from src.models.municipio import Municipio

        if not isinstance(valor, Municipio):
            raise TypeError("Erro: O município responsável deve ser uma instância da classe Município!")
        self._municipio_responsavel = valor

    @property
    def departamento(self):
        """Retorna o departamento (ex: EDUCAÇÃO, FINANÇAS)."""
        return self._departamento
    
    @departamento.setter
    def departamento(self, valor):
        """
        Valida o departamento:
        - Deve ser string.
        - Deve ter pelo menos 2 caracteres.
        - Não deve conter números (usando Regex para permitir espaços).
        """
        if not isinstance(valor, str):
            raise TypeError("Erro: O departamento deve ser uma string!")
        
        if not valor.replace(" ", "").isalpha():
            raise ValueError("Erro: No tipo de departamento não pode conter dígitos numéricos")

        padrao_departamento = valor.strip().upper()

        if len(padrao_departamento) < 2:
            raise ValueError("Erro: Departamento inválido!")
        
        else:
            self._departamento = padrao_departamento

    #-------
    #METODOS
    #-------

    def get_permissao(self):
        """
        Retorna as permissoes do secretario no sistema.
        
        Returns:
            list: Lista contendo as permissoes do secretario:
                  - ADMINISTRAR_MUNICIPIO: Gerenciar unidades e recursos municipais
                  - GERENCIAR_VERBA_GLOBAL: Controlar verbas entre escolas
                  - CADASTRAR_GESTORES: Atribuir gestores as escolas
                  - MODERAR_DEMANDAS: Aprovar/reprovar solicitacoes
                  - VISUALIZAR_ESTATISTICAS_REDE: Consultar dados consolidados
        """
        return ["ADMINISTRAR_MUNICIPIO", "GERENCIAR_VERBA_GLOBAL", "CADASTRAR_GESTORES", 
            "MODERAR_DEMANDAS", "VISUALIZAR_ESTATISTICAS_REDE"]
    
    def exibir_perfil(self):
        """
        Exibe o perfil completo do secretario.
        
        Implementacao do metodo abstrato da classe Usuario que retorna uma string
        formatada com os dados administrativos do secretario, incluindo municipio,
        departamento, email e status da conta.
        
        Returns:
            str: String formatada contendo informacoes do perfil do secretario.
        """
        nome_municipio = self.municipio_responsavel.nome if hasattr(self.municipio_responsavel, 'nome') else "Não informado"
        
        return (
            f"Nome: {self.nome}\n"
            f"CPF: {self.cpf}\n"
            f"ID Usuário: {self.id_usuario}\n"
            f"E-mail: {self.email}\n"
            f"Município: {nome_municipio}\n"
            f"Departamento: {self.departamento}\n"
            f"Status: {'Ativo' if self._status else 'Inativo'}"
        )

    def ver_estatisticas(self, lista_escola):
        """
        Gera um relatorio estatistico consolidado da rede municipal.
        
        Exibe informacoes agregadas sobre escolas, demandas e recursos financeiros
        da rede municipal, permitindo acompanhamento de toda a rede de educacao.
        
        Args:
            lista_escola (list): Lista de objetos Escola para analise.
                                 Todas devem pertencer ao municipio do secretario.
        
        Returns:
            str: Relatorio formatado com numero de escolas, demandas pendentes
                 e verba disponivel, ou mensagem de erro se acesso negado.
        """
        from src.models.escola import Escola
        from src.models.municipio import Municipio

        if not self._status:
            return "Conta do Secretário está desativada"
        
        # Se a lista vier vazia do repositório por causa do erro de ID, 
        # o relatório sempre será zero. 
        if not lista_escola:
            return (
                f"Relatório do Município {self.municipio_responsavel.nome}:\n"
                f"[yellow]Nenhuma escola carregada ou erro no processamento.[/yellow]"
            )

        total_escolas_municipio = 0
        verba_total_municipio = self.municipio_responsavel.verba_disponivel_municipio
        total_solicitacoes = 0

        # Loop para processar as estatísticas
        for escola in lista_escola:
            # Verificação simplificada: checa se o ID do município da escola bate com o do secretário
            # Isso é mais seguro que comparar o objeto inteiro na lista 'escolas_situadas'
            id_mun_escola = getattr(escola, 'id_municipio', None)
            id_mun_sec = getattr(self.municipio_responsavel, 'id_municipio', None)

            if id_mun_escola == id_mun_sec:
                total_escolas_municipio += 1
                
                # Acessa as solicitações com segurança
                solicitacoes = getattr(escola, '_solicitacoes_enviadas', [])
                total_solicitacoes += len(solicitacoes)

        return (
            f"Relatório do Município {self.municipio_responsavel.nome}:\n"
            f"- Escolas: {total_escolas_municipio}\n"
            f"- Demandas pendentes: {total_solicitacoes}\n"
            f"- Verba disponível: R$ {verba_total_municipio:,.2f}"
        )
            

    def realizar_cadastro(self, gestor, escola_alvo):
        """
        Atribui um gestor a uma escola dentro do municipio.
        
        Permite que o secretario vincule um gestor a uma unidade escolar especifica,
        estabelecendo a relacao de administracao entre gestor e escola.
        
        Args:
            gestor (Gestor): Objeto do gestor a ser atribuido.
            escola_alvo (Escola): Objeto da escola que sera administrada pelo gestor.
                                  Deve pertencer ao municipio do secretario.
        
        Returns:
            str: Mensagem confirmando a atribuicao ou descrevendo o erro ocorrido.
        
        Raises (implicitamente via retorno):
            - Acesso negado se a escola nao pertencer ao municipio
            - TypeError se gestor nao for uma instancia valida de Gestor
        """
        from src.models.escola import Escola
        from src.models.gestor import Gestor

        if not self._status:
            return "Conta do Secretário está desativada"
        
        if escola_alvo not in self.municipio_responsavel.escolas_situadas:
            return "Acesso negado: Esta escola não pertence à sua jurisdição municipal."
        
        if not isinstance(gestor, Gestor):
            raise TypeError("Erro: O objeto fornecido não é um Gestor válido.")
        
        escola_alvo._gestor_atual = gestor

        gestor.escola_associada = escola_alvo

        return f"Sucesso: {gestor.nome} agora é o gestor da escola {escola_alvo.nome}."
    
    def gerenciar_status_gestor(self, gestor, novo_status: bool):
        """
        Ativa ou desativa a conta de um gestor dentro da rede municipal.
        
        Permite que o secretario suspenda ou reative gestores sob sua jurisdicao,
        controlando o acesso deles ao sistema.
        
        Args:
            gestor (Gestor): Objeto do gestor cuja conta sera alterada.
            novo_status (bool): True para ativar, False para desativar a conta.
        
        Returns:
            str: Mensagem confirmando a alteracao ou descrevendo o erro de permissao.
        
        Note:
            - O gestor deve estar vinculado a uma escola do municipio do secretario
        """
        from src.models.gestor import Gestor
        
        if not isinstance(gestor, Gestor):
            return "Erro: O objeto fornecido não é um Gestor válido."

        if gestor.escola_associada.id_municipio != self.municipio_responsavel.id_municipio:
            return f"Erro: O gestor {gestor.nome} não pertence à rede municipal de {self.municipio_responsavel.nome}."

        gestor.status = novo_status
        acao = "ativado" if novo_status else "desativado"

        if hasattr(gestor, 'atualizar'):
            gestor.atualizar(self.nome)

        return f"Sucesso: O Gestor {gestor.nome} foi {acao} pelo Gabinete da Secretaria."

    
    def enviar_mensagem(self, titulo, conteudo, escola_especifica=None):
        """
        Publica comunicados oficiais para a rede municipal ou escola especifica.
        
        Permite que o secretario distribua noticias e avisos importantes,
        seja para toda a rede de escolas ou para uma unidade especifica.
        
        Args:
            titulo (str): Titulo do comunicado (obrigatorio).
            conteudo (str): Conteudo da mensagem (obrigatorio).
            escola_especifica (Escola, optional): Escola alvo especifica.
                                                  Se None, envia para toda a rede.
                                                  Defaults to None.
        
        Returns:
            str: Mensagem indicando sucesso ou error do envio.
        
        Note:
            - Quando sem escola especifica, tenta enviar para todas as escolas
            - Retorna contagem de escolas que receberam com sucesso
        """
        from src.models.escola import Escola

        if not self._status:
            return "Erro: Secretário inativo não pode enviar comunicados."

        if not titulo or not conteudo:
            return "Erro: Título e conteúdo são obrigatórios."

        remetente = f"GABINETE: {self.nome} ({self.departamento})"

        if escola_especifica:
            if not isinstance(escola_especifica, Escola):
                return "Erro: O alvo fornecido não é uma instância de Escola."
            
            if escola_especifica not in self.municipio_responsavel.escolas_situadas:
                return "Acesso negado: A escola alvo não pertence a este município."
            
            if escola_especifica.adicionar_noticia(titulo, conteudo, remetente):
                return f"Mensagem enviada com sucesso para {escola_especifica.nome}."
            return f"Erro: A escola {escola_especifica.nome} não pôde processar o comunicado."

        else:
            escolas = self.municipio_responsavel.escolas_situadas
            if not escolas:
                return "Erro: O município não possui escolas cadastradas."

            sucessos = 0
            for escola in escolas:
                if escola.adicionar_noticia(titulo, conteudo, remetente):
                    sucessos += 1
            
            return f"Comunicado global finalizado. Enviado para {sucessos} de {len(escolas)} escolas."

    def gerenciar_verba(self, escola, id_demanda):
        """
        Realiza a transferencia financeira do municipio para a escola.
        
        Processa o pagamento de demandas aprovadas, transferindo recursos
        municipais para a conta financeira da escola solicitante.
        
        Args:
            escola (Escola): Objeto da escola que recebera a transferencia.
            id_demanda (str): ID unico da demanda a ser processada.
                             Deve ter status 'APROVADA' para pagar.
        
        Returns:
            str: Mensagem confirmando a transferencia, detalhando o valor e novo status,
                 ou mensagem de erro se algo impedir o processamento.
        
        Note:
            - Apenas demandas com status 'APROVADA' podem ser pagas
            - Valida se ha verba municipal suficiente antes de processar
            - Atualiza o status da demanda para 'CONCLUIDA / PAGA' ao finalizar
        """
        demanda = next((d for d in escola.solicitacoes_enviadas if d.id_demanda == id_demanda), None)

        if not demanda:
            return "Erro: Demanda não encontrada para processamento financeiro."

        if demanda.status != "APROVADA":
            return f"Pagamento Negado: A demanda está com status '{demanda.status}'. " \
                   f"Aprove-a primeiro em 'administrar_solicitacoes'."

        valor_pagamento = getattr(demanda, 'custo_estimado', 0)

        if valor_pagamento <= 0:
            return "Informação: Esta demanda não possui custos financeiros para transferência."

        if self.municipio_responsavel.verba_disponivel_municipio < valor_pagamento:
            return "Erro Crítico: Saldo municipal insuficiente para realizar a transferência agora."

        self.municipio_responsavel.verba_disponivel_municipio -= valor_pagamento
        escola.verba_disponivel_escola += valor_pagamento

        demanda.atualizar_status("CONCLUIDA / PAGA")
        demanda.atualizar(self.nome)

        return (
            f"Sucesso Financeiro!\n"
            f"Valor de R$ {valor_pagamento:,.2f} transferido para a conta da escola {escola.nome}.\n"
            f"Status da Demanda: {demanda.status}"
        )

    def administrar_solicitacoes(self, escola, id_demanda, acao_secretario):
        """
        Avalia e aprova ou reprova demandas enviadas pelas escolas.
        
        Permite que o secretario analise solicitacoes de recursos e infraestrutura,
        definindo se serao aprovadas para processamento financeiro ou rejeitadas.
        
        Args:
            escola (Escola): Objeto da escola que enviou a demanda.
            id_demanda (str): ID unico da demanda a ser avaliada.
            acao_secretario (str): Acao a realizar: 'APROVAR' ou 'REPROVAR'.
        
        Returns:
            str: Mensagem confirmando a acao realizada ou error se comando invalido.
        
        Note:
            - Demandas aprovadas passam para etapa de 'gerenciar_verba'
            - Demandas reprovadas sao definitivamente rejeitadas
            - Valida disponibilidade de verba ao aprovar demandas
        """
        demanda = next((d for d in escola.solicitacoes_enviadas if d.id_demanda == id_demanda), None)
        
        if not demanda:
            return "Erro: Demanda não localizada."
        if acao_secretario.upper() == "APROVAR":
            custo = getattr(demanda, 'custo_estimado', 0)
            if custo > self.municipio_responsavel.verba_disponivel_municipio:
                return "Aprovação negada: O valor excede o saldo do município."
            
            demanda.atualizar_status("APROVADA")
            demanda.atualizar(self.nome)
            return f"Demanda {id_demanda[:8]} aprovada. Pronta para pagamento no Gerenciar Verba."

        elif acao_secretario.upper() == "REPROVAR":
            demanda.atualizar_status("REPROVADA")
            demanda.atualizar(self.nome)
            return f"Demanda {id_demanda[:8]} foi oficialmente rejeitada."
        
        else:
            return "Comando inválido. Use 'APROVAR' ou 'REPROVAR'."
    
    def gerenciar_unidades(self, acao, escola):
        """
        Adiciona ou remove uma unidade escolar da rede municipal.
        
        Permite que o secretario controle o portfolio de escolas do municipio,
        expandindo ou contraindo a rede conforme necessario.
        
        Args:
            acao (str): Acao a realizar: 'ADICIONAR' ou 'REMOVER'.
            escola (Escola): Objeto da escola a ser adicionada ou removida.
        
        Returns:
            str: Mensagem confirmando a operacao ou descrevendo o motivo da falha.
        
        Note:
            - Nao permite remover escola que ainda tenha alunos matriculados
            - Ao remover, verifica automaticamente se ha alunos na escola
        """
        from src.models.escola import Escola

        if not self._status:
            return "Erro: Conta do Secretário está desativada."

        if not isinstance(escola, Escola):
            return "Erro: O objeto fornecido não é uma Escola válida."

        if acao.upper() == "ADICIONAR":
            if escola in self.municipio_responsavel.escolas_situadas:
                return f"Aviso: A escola {escola.nome} já faz parte da rede."
            
            self.municipio_responsavel.escolas_situadas.append(escola)
            return f"Sucesso: Escola {escola.nome} adicionada ao município {self.municipio_responsavel.nome}."
        
        elif acao.upper() == "REMOVER":
            if escola not in self.municipio_responsavel.escolas_situadas:
                return "Erro: Esta escola não pertence a este município ou já foi removida."

            total_alunos = sum(len(t.alunos_matriculados) for t in escola._turmas_existentes)
            if total_alunos > 0:
                return f"Erro: Não é possível remover a escola {escola.nome} pois ainda existem alunos matriculados."

            self.municipio_responsavel.escolas_situadas.remove(escola)
            return f"Sucesso: Escola {escola.nome} removida da rede municipal."

        else:
            return "Comando inválido. Escolha 'ADICIONAR' ou 'REMOVER'."
        
    def to_dict_especifico(self):
        """
        Exporta os dados especificos do secretario em formato de dicionario.
        
        Retorna um dicionario contendo os atributos especificos da classe Secretario,
        utilizando como base os dados da classe pai (Usuario) e adicionando o contexto
        municipal de atuacao.
        
        Returns:
            dict: Dicionario com id_usuario, departamento e id_municipio do secretario.
        """
        return{
            "id_usuario": self._id_usuario,
            "id_municipio": self.municipio_responsavel.id_municipio if self.municipio_responsavel else None,
            "departamento": self.departamento,
            
        }