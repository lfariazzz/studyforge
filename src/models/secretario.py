from src.models.usuario import Usuario

class Secretario(Usuario):
    def __init__(self, nome, cpf, email, senha, telefone, data_nascimento,
                 municipio_responsavel, departamento):
        super().__init__(nome, cpf, email, senha, telefone, data_nascimento, "SECRETÁRIO")

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
        Retorna a lista de permissões da classe Secretário.
        """
        return ["ADMINISTRAR_MUNICIPIO", "GERENCIAR_VERBA_GLOBAL", "CADASTRAR_GESTORES", 
            "MODERAR_DEMANDAS", "VISUALIZAR_ESTATISTICAS_REDE"]
    
    def exibir_perfil(self):
        """
        Implementação do método abstrato da classe Usuario.
        Retorna uma string formatada com os dados principais do secretário.
        """
        nome_municipio = self.municipio_responsavel.nome if hasattr(self.municipio_responsavel, 'nome') else "Não informado"
        status_conta = "Ativa" if self._status else "Inativa/Suspensa"

        return (
            f"\n" + "="*40 + "\n"
            f"          PERFIL DO SECRETÁRIO\n"
            f"="*40 + "\n"
            f"Nome: {self.nome}\n"
            f"ID Identificador: {self.id}\n"
            f"Município: {nome_municipio}\n"
            f"Departamento: {self.departamento}\n"
            f"E-mail: {self.email}\n"
            f"Status: {status_conta}\n"
            f"="*40
        )

    def ver_estatisticas(self, lista_escola):
        from src.models.escola import Escola
        from src.models.municipio import Municipio

        if not self._status:
            return "Conta do Secretário está desativada"
        
        total_escolas_municipio = 0
        verba_total_municipio = self.municipio_responsavel.verba_disponivel_municipio
        total_solicitacoes = 0

        if not all(escola in self.municipio_responsavel.escolas_situadas for escola in lista_escola):
            return "Acesso negado a lista de escolas por elas não serem do município."
        
        for escola in lista_escola:
            total_escolas_municipio += 1
            total_solicitacoes += len(escola._solicitacoes_enviadas)

        return (
            f"Relatório do Município {self.municipio_responsavel.nome}:\n"
            f"- Escolas: {total_escolas_municipio}\n"
            f"- Demandas pendentes: {total_solicitacoes}\n"
            f"- Verba disponível: R$ {verba_total_municipio:,.2f}"
        )
            

    def realizar_cadastro(self, gestor, escola_alvo):
        """Função que recebe uma instância da classe Gestor para colocar na escola desejada"""
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
        Permite ao Secretário ativar ou desativar a conta de um Gestor.
        Regra: O Secretário só pode gerenciar gestores que pertencem ao seu município.
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
            Publica comunicados oficiais. Pode ser para a rede toda ou uma escola alvo.
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
        Realiza a transferência financeira do município para a escola.
        Apenas demandas com status 'APROVADA' podem ser processadas.
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
            f"✅ Sucesso Financeiro!\n"
            f"Valor de R$ {valor_pagamento:,.2f} transferido para a conta da escola {escola.nome}.\n"
            f"Status da Demanda: {demanda.status}"
        )

    def administrar_solicitacoes(self, escola, id_demanda, acao_secretario):
        """
        Analisa a demanda e define se ela segue para pagamento ou é descartada.
        acao_secretario: deve ser 'APROVAR' ou 'REPROVAR'
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
        acao: 'ADICIONAR' ou 'REMOVER'
        escola: instância da classe Escola
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
        
    def to_dict(self):
        """
        Exporta os dados do secretário em formato de dicionário.
        Utiliza a base da classe pai (Usuario) e adiciona o contexto municipal.
        """
        dados = super().to_dict()
        dados.update({
            "municipio_responsavel": self.municipio_responsavel.nome if hasattr(self.municipio_responsavel, 'nome') else "Não definido",
            "departamento": self.departamento,
            "qtd_escolas_sob_gestao": len(self.municipio_responsavel.escolas_situadas) if hasattr(self.municipio_responsavel, 'escolas_situadas') else 0,
            "verba_municipal_atual": self.municipio_responsavel.verba_disponivel_municipio if hasattr(self.municipio_responsavel, 'verba_disponivel_municipio') else 0,
            "permissoes": self.get_permissao()
        })

        return dados