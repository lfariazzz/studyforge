import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from typing import Optional

# Imports do seu projeto
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.secretario import Secretario

from src.models.escola import Escola

# Guardamos o construtor original
_original_init = Escola.__init__

def _novo_init(self, *args, **kwargs):
    # 1. LIMPEZA: Remove o que o SQLite manda e o Python não conhece
    kwargs.pop('id_localizacao', None)
    
    # 2. MAPEAMENTO: Garante que os argumentos que o modelo original exige 
    # (e que causaram o erro anterior) existam, mesmo que vazios.
    campos_obrigatorios = {
        'id_endereco': 0,
        'gestor_atual': None,
        'verba_disponivel_escola': 0.0,
        'id_municipio': None,
        'capacidade_infraestrutura': "Padrão"
    }
    
    for campo, valor_padrao in campos_obrigatorios.items():
        if campo not in kwargs:
            kwargs[campo] = valor_padrao

    # 3. EXECUÇÃO: Chama o construtor original da classe Escola
    _original_init(self, *args, **kwargs)

Escola.__init__ = _novo_init

console = Console()
app = typer.Typer(help="Painel Administrativo do Secretário de Educação")
repo = RepositorioGeral()


def to_int_or_none(valor):
    """Converte string para int de forma segura; retorna None se inválido."""
    try:
        if valor is None:
            return None
        s = str(valor).strip()
        if s == "":
            return None
        return int(s)
    except Exception:
        return None

# --- AUXILIARES ---

def exibir_cabecalho(sec: Secretario):
    """Exibe um painel visual no topo do menu."""
    console.clear()
    # Uso seguro do atributo via property ou getattr
    mun_nome = sec.municipio_responsavel.nome if sec.municipio_responsavel else "N/A"
    
    console.print(Panel(
        f"[bold blue]STUDYFORGE - PAINEL DO SECRETÁRIO[/bold blue]\n"
        f"[cyan]Usuário:[/cyan] {sec.nome} | [cyan]Município:[/cyan] {mun_nome} | [cyan]Depto:[/cyan] {sec.departamento}",
        expand=False,
        border_style="blue"
    ))

def exibir_tabela_escolas(sec: Secretario):
    """Busca e exibe uma tabela com as escolas do município e seus IDs."""
    try:
        # Busca as escolas vinculadas ao ID do município do secretário
        escolas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
        
        if not escolas:
            console.print("[yellow]Nenhuma escola vinculada ao seu município encontrada.[/yellow]")
            return False
        
        table = Table(title=f"Escolas Disponíveis - {sec.municipio_responsavel.nome}", show_lines=True)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Nome da Unidade", style="white")
        table.add_column("Gestor Atual", style="green")

        for esc in escolas:
            # Tentamos pegar o nome do gestor se ele existir, senão 'Vago'
            nome_gestor = "Vago"
            if hasattr(esc, '_gestor_atual') and esc._gestor_atual:
                nome_gestor = esc._gestor_atual.nome
            elif hasattr(esc, 'gestor_atual') and esc.gestor_atual:
                nome_gestor = esc.gestor_atual.nome

            table.add_row(
                str(esc.id_escola), 
                str(esc.nome), 
                nome_gestor
            )
        
        console.print(table)
        return True
    except Exception as e:
        console.print(f"[red]Erro ao listar escolas: {e}[/red]")
        return False

def exibir_tabela_gestores(sec: Secretario):
    """Lista todos os gestores das escolas vinculadas ao município do secretário."""
    try:
        # Busca as escolas para encontrar os gestores vinculados a elas
        escolas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
        
        table = Table(title=f"Gestores da Rede - {sec.municipio_responsavel.nome}", show_lines=True)
        table.add_column("ID Usuário", style="cyan", no_wrap=True)
        table.add_column("Nome", style="white")
        table.add_column("Escola", style="magenta")
        table.add_column("Status", justify="center")

        encontrou = False
        for esc in escolas:
            # Tenta pegar o gestor por diferentes nomes de atributo possíveis
            gestor = getattr(esc, 'gestor_atual', None) or getattr(esc, '_gestor_atual', None)
            
            if gestor:
                encontrou = True
                status = "[green]● Ativo[/green]" if getattr(gestor, '_status', True) else "[red]○ Inativo[/red]"
                table.add_row(
                    str(gestor.id_usuario),
                    gestor.nome,
                    esc.nome,
                    status
                )
        
        if not encontrou:
            console.print("[yellow]Nenhum gestor encontrado nas escolas do seu município.[/yellow]")
            return False
        
        console.print(table)
        return True
    except Exception as e:
        console.print(f"[red]Erro ao carregar lista de gestores: {e}[/red]")
        return False

# --- FUNÇÕES DE AÇÃO (Baseadas no modelo de Gestor/Aluno) ---

def comando_perfil(sec: Secretario):
    """Exibe o perfil completo do Secretário com a estética de Painel."""
    console.clear()
    try:
        # Pegamos a string formatada que vem do modelo
        dados_perfil = sec.exibir_perfil()
        
        # Exibimos dentro de um Painel, igual ao comando_perfil do Aluno
        console.print(Panel(
            dados_perfil, 
            title="👤 Meus Dados Administrativos", 
            border_style="blue", 
            expand=False
        ))
    except Exception as e:
        console.print(f"[red]Erro ao carregar perfil: {e}[/red]")
    
    # Padronizado com o estilo do Aluno
    input("\nPressione [Enter] para voltar ao menu...")

def comando_estatisticas(sec: Secretario):
    """Relatório da rede municipal."""
    console.clear()
    with console.status("[bold green]Buscando dados da rede..."):
        try:
            # 1. Busca as escolas do município
            escolas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
            
            # 2. CARGA MANUAL DE DEMANDAS (O pulo do gato 🐈)
            for escola in escolas:
                # Busca as demandas no banco vinculadas a esta escola
                demandas_banco = repo.buscar_demandas_por_escola(escola.id_escola)
                # Injeta no atributo que o modelo Secretario usa para contar
                escola._solicitacoes_enviadas = demandas_banco

            # 3. Agora o relatório terá dados para contar!
            relatorio = sec.ver_estatisticas(escolas)
            console.print(Panel(relatorio, title="📊 Relatório de Rede", border_style="cyan"))
            
        except Exception as e:
            console.print(f"[red]Erro ao gerar estatísticas: {e}[/red]")
    
    input("\nPressione [Enter] para voltar ao menu...")

def comando_gerenciar_unidades(sec: Secretario):
    """Adiciona ou remove escolas da rede municipal."""
    console.clear()
    console.print(Panel("[bold]Gestão de Unidades Escolares[/bold]", border_style="blue"))
    
    exibir_tabela_escolas(sec)
    
    acao = Prompt.ask("\nO que deseja fazer?", choices=["ADICIONAR", "REMOVER", "VER_GESTOR", "VOLTAR"], default="VOLTAR").upper()
    
    if acao == "VOLTAR":
        return

    try:
        if acao == "ADICIONAR":
            nome_escola = Prompt.ask("Nome da Nova Escola")
            
            with console.status("[bold green]Cadastrando nova unidade..."):
                # O id_municipio já vai dentro do objeto escola
                nova_escola = Escola(
                    id_escola=None, 
                    nome=nome_escola, 
                    id_municipio=sec.municipio_responsavel.id_municipio
                )
                
                resultado = sec.gerenciar_unidades("ADICIONAR", nova_escola)

                if "Sucesso" in resultado:
                    with console.status("[bold green]Persistindo nova escola no banco..."):
                        try:
                            repo.salvar_escola(nova_escola)
                            # verifica se foi persistida
                            esc_salva = repo.buscar_escola_por_id(nova_escola.id_escola)
                            if esc_salva is None:
                                console.print(f"[bold red]❌ Falha ao persistir unidade '{nome_escola}' no banco.[/bold red]")
                            else:
                                # garante que o objeto tenha referência ao município em runtime
                                try:
                                    nova_escola._municipio = sec.municipio_responsavel
                                    sec.municipio_responsavel.cadastrar_escola(nova_escola)
                                except Exception:
                                    pass
                                console.print(f"[bold green]✅ Unidade '{nome_escola}' cadastrada com sucesso! (ID: {nova_escola.id_escola})[/bold green]")
                        except Exception as e:
                            console.print(f"[bold red]❌ Erro ao salvar escola: {e}[/bold red]")
                else:
                    console.print(f"[bold red]⚠️ {resultado}[/bold red]")

        elif acao == "REMOVER":
            escola_id = Prompt.ask("Digite o ID da Escola para remover")
            escola_id_int = to_int_or_none(escola_id)
            if escola_id_int is None:
                console.print("[red]❌ ID inválido informado.[/red]")
                return

            escola_alvo = repo.buscar_escola_por_id(escola_id_int)
            
            if not escola_alvo:
                console.print("[red]❌ Escola não encontrada.[/red]")
                return
            # Exibe gestor atual da instituição para confirmação
            gestor_atual = getattr(escola_alvo, '_gestor_atual', None) or getattr(escola_alvo, 'gestor_atual', None)
            if gestor_atual:
                console.print(Panel(f"Gestor atual: {gestor_atual.nome} (ID: {getattr(gestor_atual, 'id_usuario', getattr(gestor_atual, '_id', 'N/A'))})\nStatus: {'Ativo' if getattr(gestor_atual, 'status', True) else 'Inativo'}", title="Informação da Escola", border_style="green"))
            else:
                console.print(Panel("Gestor atual: Vago", title="Informação da Escola", border_style="yellow"))

            with console.status("[bold yellow]Removendo unidade..."):
                resultado = sec.gerenciar_unidades("REMOVER", escola_alvo)
                if "Sucesso" in resultado:
                    repo.vincular_escola_municipio(escola_alvo.id_escola, None)
                    console.print(f"[bold green]✅ {resultado}[/bold green]")
                else:
                    console.print(f"[bold red]⚠️ {resultado}[/bold red]")
                
        elif acao == "VER_GESTOR":
            escola_id = Prompt.ask("Digite o ID da Escola para ver o gestor")
            escola_id_int = to_int_or_none(escola_id)
            if escola_id_int is None:
                console.print("[red]❌ ID inválido informado.[/red]")
                input("\nPressione [Enter] para voltar...")
                return

            escola_alvo = repo.buscar_escola_por_id(escola_id_int)
            if not escola_alvo:
                console.print("[red]❌ Escola não encontrada.[/red]")
                return

            gestor_atual = getattr(escola_alvo, '_gestor_atual', None) or getattr(escola_alvo, 'gestor_atual', None)
            if gestor_atual:
                console.print(Panel(
                    f"Nome: {gestor_atual.nome}\nID: {getattr(gestor_atual, 'id_usuario', getattr(gestor_atual, '_id', 'N/A'))}\nCPF: {getattr(gestor_atual, 'cpf', 'N/A')}\nE-mail: {getattr(gestor_atual, 'email', 'N/A')}\nStatus: {'Ativo' if getattr(gestor_atual, 'status', True) else 'Inativo'}",
                    title=f"Gestor da Escola: {escola_alvo.nome}", border_style="cyan"
                ))
            else:
                console.print(Panel("Gestor atual: Vago", title=f"Gestor da Escola: {escola_alvo.nome}", border_style="yellow"))

            input("\nPressione [Enter] para continuar...")
            return
    except Exception as e:
        console.print(f"[red]Erro na operação: {e}[/red]")
    
    input("\nPressione [Enter] para continuar...")

def comando_cadastrar_gestor(sec: Secretario):
    """Cadastra um novo gestor e o vincula a uma escola."""
    console.clear()
    console.print(Panel("[bold]Cadastro de Novo Gestor[/bold]", border_style="blue"))
    
    # 1. Mostra as escolas e já captura o ID nela para evitar repetição
    if not exibir_tabela_escolas(sec):
        input("\nPressione [Enter] para voltar...")
        return

    escola_id = Prompt.ask("\nDigite o ID da Escola que este gestor irá administrar")
    
    # Pergunta se deseja criar novo gestor ou selecionar existente
    escolha = Prompt.ask("Deseja criar um novo gestor ou selecionar um existente?", choices=["NOVO", "SELECIONAR"], default="NOVO")

    try:
        escola_alvo = repo.buscar_escola_por_id(int(escola_id))
        if not escola_alvo:
            console.print("[red]❌ Erro: Escola não encontrada.[/red]")
            input("\nPressione [Enter] para voltar...")
            return

        if escolha == "SELECIONAR":
            # lista gestores disponíveis e permite escolher um
            if not exibir_tabela_gestores(sec):
                console.print("[yellow]Nenhum gestor disponível para seleção.[/yellow]")
                input("\nPressione [Enter] para voltar...")
                return

            gestor_id = Prompt.ask("Digite o ID do Gestor a ser vinculado")
            gestor_obj = repo.buscar_usuario_por_id(to_int_or_none(gestor_id))
            from src.models.gestor import Gestor
            if not gestor_obj or not isinstance(gestor_obj, Gestor):
                console.print("[red]❌ Gestor inválido ou não encontrado.[/red]")
                input("\nPressione [Enter] para voltar...")
                return

            # só permite vincular se gestor não tiver escola associada
            if getattr(gestor_obj, 'escola_associada', None) is not None or getattr(gestor_obj, '_escola_associada', None) is not None:
                console.print("[red]❌ Este gestor já está vinculado a uma escola.[/red]")
                input("\nPressione [Enter] para voltar...")
                return

            resultado_modelo = sec.realizar_cadastro(gestor_obj, escola_alvo)
            if "Sucesso" in resultado_modelo:
                try:
                    # vincula no repositório
                    repo.vincular_gestor_escola(gestor_obj.id_usuario, escola_alvo.id_escola)
                    console.print(f"\n[bold green]✅ {resultado_modelo} (ID: {gestor_obj.id_usuario})[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]❌ Erro ao vincular gestor: {e}[/bold red]")
            else:
                console.print(f"\n[bold red]⚠️ {resultado_modelo}[/bold red]")

        else:
            # coleta dados para criar novo gestor
            nome = Prompt.ask("Nome Completo")
            cpf = Prompt.ask("CPF (xxx.xxx.xxx-xx)")
            email = Prompt.ask("E-mail Institucional")
            senha = Prompt.ask("Senha (mín. 8 caracteres)", password=True, show_default=False)
            telefone = Prompt.ask("Telefone (11 dígitos)")
            data_nasc = Prompt.ask("Data de Nascimento (DD/MM/AAAA)")

            from src.models.gestor import Gestor
            novo_gestor = Gestor(None, nome, cpf, email, senha, telefone, data_nasc, None)

            resultado_modelo = sec.realizar_cadastro(novo_gestor, escola_alvo)
            if "Sucesso" in resultado_modelo:
                try:
                    repo.salvar_usuario(novo_gestor)
                    g_salvo = repo.buscar_usuario_por_id(novo_gestor.id_usuario)
                    if g_salvo is None:
                        console.print(f"[bold red]❌ Gestor salvo, mas não encontrado no repositório (ID: {novo_gestor.id_usuario}).[/bold red]")
                    else:
                        repo.vincular_gestor_escola(novo_gestor.id_usuario, escola_alvo.id_escola)
                        console.print(f"\n[bold green]✅ {resultado_modelo} (ID: {novo_gestor.id_usuario})[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]❌ Erro ao salvar gestor: {e}[/bold red]")
            else:
                console.print(f"\n[bold red]⚠️ {resultado_modelo}[/bold red]")

    except Exception as e:
        console.print(f"[red]Erro ao realizar cadastro: {e}[/red]")

    input("\nPressione [Enter] para continuar...")

def comando_status_gestor(sec: Secretario):
    """Ativa ou desativa gestores da rede com auxílio de tabela."""
    console.clear()
    console.print(Panel("[bold]Controle de Acesso de Gestores[/bold]", border_style="blue"))
    
    # Exibe a tabela antes de pedir o ID
    if not exibir_tabela_gestores(sec):
        input("\nPressione [Enter] para voltar...")
        return

    gestor_id = Prompt.ask("\nDigite o ID do Gestor que deseja alterar")
    
    try:
        # Busca o usuário e verifica se é um Gestor
        gestor = repo.buscar_usuario_por_id(int(gestor_id))
        from src.models.gestor import Gestor
        
        if not gestor or not isinstance(gestor, Gestor):
            console.print("[red]❌ Erro: O ID informado não pertence a um Gestor válido.[/red]")
        else:
            status_atual = "Ativo" if getattr(gestor, '_status', True) else "Inativo"
            console.print(f"\nSelecionado: [cyan]{gestor.nome}[/cyan] | Status Atual: [bold]{status_atual}[/bold]")
            
            novo_status_str = Prompt.ask("Deseja alterar para", choices=["ATIVAR", "DESATIVAR", "CANCELAR"], default="CANCELAR").upper()
            
            if novo_status_str != "CANCELAR":
                novo_status_bool = True if novo_status_str == "ATIVAR" else False
                
                # Regra de negócio no modelo
                resultado = sec.gerenciar_status_gestor(gestor, novo_status_bool)
                
                if "Sucesso" in resultado:
                    # Persistência
                    repo.atualizar_status_usuario(gestor.id_usuario, novo_status_bool)
                    console.print(f"[bold green]✅ {resultado}[/bold green]")
                else:
                    console.print(f"[bold red]⚠️ {resultado}[/bold red]")
                    
    except ValueError:
        console.print("[red]❌ Por favor, digite um número de ID válido.[/red]")
    except Exception as e:
        console.print(f"[red]Erro ao processar status: {e}[/red]")
    
    input("\nPressione [Enter] para continuar...")

def comando_comunicado(sec: Secretario):
    """Envia comunicado para todas as escolas."""
    console.print("\n[bold]Novo Comunicado Global[/bold]")
    titulo = Prompt.ask("Título")
    conteudo = Prompt.ask("Conteúdo")

    with console.status("[bold blue]Enviando..."):
        try:
            # Sincroniza escolas antes de enviar (atribui ao campo interno, não à property somente-leitura)
            escolas_do_repo = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
            try:
                sec.municipio_responsavel._escolas_situadas = escolas_do_repo
            except Exception:
                # fallback: atualiza lista existente de forma segura
                current = getattr(sec.municipio_responsavel, '_escolas_situadas', None)
                if current is None:
                    sec.municipio_responsavel._escolas_situadas = list(escolas_do_repo)
                else:
                    current.clear()
                    current.extend(escolas_do_repo)

            resultado = sec.enviar_mensagem(titulo, conteudo)
            console.print(f"\n[bold green]✅ {resultado}[/bold green]")
        except Exception as e:
            console.print(f"[red]Erro ao enviar: {e}[/red]")
    
    input("\nPressione [Enter] para continuar...")

def comando_pagamento(sec: Secretario):
    """Aprova e paga demandas."""
    console.clear()
    # Antes de pedir inputs, mostra as escolas do município e IDs de demandas
    try:
        escolas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
        if not escolas:
            console.print("[yellow]Nenhuma escola vinculada ao seu município encontrada.[/yellow]")
        else:
            table = Table(title=f"Escolas e Demandas - {sec.municipio_responsavel.nome}", show_lines=True)
            table.add_column("ID Escola", style="cyan", no_wrap=True)
            table.add_column("Nome da Escola", style="white")
            table.add_column("Demandas (IDs)", style="magenta")

            for esc in escolas:
                demandas = repo.buscar_demandas_por_escola(esc.id_escola) or []
                ids = ", ".join([getattr(d, 'id_demanda', str(d)) for d in demandas]) if demandas else "-"
                table.add_row(str(esc.id_escola), str(esc.nome), ids)

            console.print(table)

    except Exception as e:
        console.print(f"[red]Erro ao listar escolas/demandas: {e}[/red]")

    escola_id = Prompt.ask("Digite o ID da Escola")
    demanda_id = Prompt.ask("Digite o ID da Demanda")

    escola_id_int = to_int_or_none(escola_id)

    try:
        escola = repo.buscar_escola_por_id(escola_id_int)
        if not escola:
            console.print("[red]❌ Escola não encontrada.[/red]")
            input("\nPressione [Enter] para continuar...")

        # Processa a aprovação/pagamento da demanda normalmente

        console.print(f"\n[yellow]Analisando demanda...[/yellow]")
        aviso = sec.administrar_solicitacoes(escola, demanda_id, "APROVAR")
        console.print(f"[blue]{aviso}[/blue]")

        if "aprovada" in aviso.lower():
            confirmacao = sec.gerenciar_verba(escola, demanda_id)
            # Persistência no Banco
            repo.atualizar_saldos(sec.municipio_responsavel, escola)
            # tenta converter id de demanda para int quando possível
            demanda_id_limpa = to_int_or_none(demanda_id) or demanda_id
            repo.atualizar_status_demanda(demanda_id_limpa, "CONCLUIDA / PAGA")
            console.print(f"[bold yellow]💰 {confirmacao}[/bold yellow]")
    except Exception as e:
        console.print(f"[red]Erro no processamento: {e}[/red]")
    
    input("\nPressione [Enter] para continuar...")

# --- MENU INTERATIVO ---

def menu_interativo_secretario(sec: Secretario):
    while True:
        exibir_cabecalho(sec)
        
        table = Table(show_header=False, box=None)
        table.add_row("[1]", "👤 Ver Meu Perfil")
        table.add_row("[2]", "📊 Estatísticas da Rede")
        table.add_row("[3]", "📢 Enviar Comunicado Global")
        table.add_row("[4]", "💸 Gerenciar Pagamentos")
        table.add_row("[5]", "🏫 Gerenciar Unidades Escolares")
        table.add_row("[6]", "🔑 Ativar/Desativar Gestores")
        table.add_row("[7]", "👨‍💼 Cadastrar Novo Gestor") # <-- Nova linha
        table.add_row("[0]", "🚪 Logout e Sair")
        
        console.print(table)
        
        opcao = Prompt.ask("\nEscolha uma opção", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default="0")

        if opcao == "1":
            comando_perfil(sec)
        elif opcao == "2":
            comando_estatisticas(sec)
        elif opcao == "3":
            comando_comunicado(sec)
        elif opcao == "4":
            comando_pagamento(sec)
        elif opcao == "5":
            comando_gerenciar_unidades(sec)
        elif opcao == "6":
            comando_status_gestor(sec)
        elif opcao == "7":
            comando_cadastrar_gestor(sec)
        elif opcao == "0":
            break