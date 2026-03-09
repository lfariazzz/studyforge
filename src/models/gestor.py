from src.models.usuario import Usuario

class Gestor(Usuario):
    def __init__(self, id_usuario, nome, cpf, email, senha, telefone, data_nascimento, escola_associada):
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

        if not isinstance(valor, Escola):
            raise TypeError("Erro: Escola associada deve ser um objeto da classe Escola!")
        
        self._escola_associada = valor
    #-------
    #METODOS
    #-------
    
    def get_permissao(self):
        """Retorna a lista de funcionalidades permitidas para o Gestor."""
        return ["VIZUALIZAR_PERFIL", "VER_ESTATISTICA_ESCOLA", "REALIZAR_CADASTRO", "ENVIAR_MENSAGEM", 
                "REALIZAR_SOLICITACAO_VERBA", "ADMINISTRAR_SOLICITACOES_ESCOLA", "GERENCIAR_DADOS_ESCOLA", "ALTERAR_STATUS_USUARIO"]
    
    def exibir_perfil(self):
        """
        Implementação do método abstrato da classe Usuario.
        Retorna uma string formatada com os dados principais do gestor.
        """
        nome_escola = self.escola_associada.nome if hasattr(self.escola_associada, 'nome') else "Não informada"
        status_conta = "Ativa" if self._status else "Inativa/Suspensa"

        return (
            f"\n" + "="*40 + "\n"
            f"          PERFIL DO GESTOR\n"
            f"="*40 + "\n"
            f"Nome: {self.nome}\n"
            f"ID Identificador: {self.id}\n"
            f"Escola: {nome_escola}\n"
            f"E-mail: {self.email}\n"
            f"Status: {status_conta}\n"
            f"="*40
        )
    
    def _get_total_alunos(self):
        """Método auxiliar para centralizar o cálculo de alunos."""
        return sum(len(t.alunos_matriculados) for t in self.escola_associada._turmas_existentes)

    def ver_estatisticas(self):
        """
        Gera um relatório estatístico completo da escola associada.
        Consolida dados de pessoas, infraestrutura e finanças diretamente da Escola.
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
        Interface do Gestor com a DemandaFactory.
        O Gestor solicita o TIPO, e a Factory lida com a complexidade da criação.
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
        Permite ao gestor ativar ou desativar usuários da sua unidade.
        O Gestor só pode alterar o status de Alunos ou Professores.
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
    
    def to_dict(self):
        """
        Exporta os dados do gestor em formato de dicionário.
        Utiliza a base da classe pai (Usuario) e adiciona o contexto da escola.
        """
        dados = super().to_dict()

        dados.update({
            "escola_vinculada": self.escola_associada.nome if hasattr(self.escola_associada, 'nome') else "Não definida",
            "id_escola": self.escola_associada.id_escola if hasattr(self.escola_associada, 'id_escola') else None,
            "permissoes": self.get_permissao()
        })

        return dados