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
                status = "[green]● Ativo[/green]" if gestor.status else "[red]○ Inativo[/red]"
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
    
    acao = Prompt.ask("\nO que deseja fazer?", choices=["ADICIONAR", "REMOVER", "VOLTAR"], default="VOLTAR").upper()
    
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
                    # AJUSTE AQUI: Remova o segundo argumento (sec.municipio_responsavel.id_municipio)
                    # O repositório provavelmente extrai o ID do próprio objeto 'nova_escola'
                    repo.salvar_escola(nova_escola) 
                    
                    console.print(f"[bold green]✅ Unidade '{nome_escola}' cadastrada com sucesso![/bold green]")
                else:
                    console.print(f"[bold red]⚠️ {resultado}[/bold red]")

        elif acao == "REMOVER":
            escola_id = Prompt.ask("Digite o ID da Escola para remover")
            escola_alvo = repo.buscar_escola_por_id(int(escola_id))
            
            if not escola_alvo:
                console.print("[red]❌ Escola não encontrada.[/red]")
                return

            with console.status("[bold yellow]Removendo unidade..."):
                resultado = sec.gerenciar_unidades("REMOVER", escola_alvo)
                if "Sucesso" in resultado:
                    repo.vincular_escola_municipio(escola_alvo.id_escola, None)
                    console.print(f"[bold green]✅ {resultado}[/bold green]")
                else:
                    console.print(f"[bold red]⚠️ {resultado}[/bold red]")
                
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
    
    # 2. Coleta de dados pessoais (Removida a repetição do escola_id aqui)
    nome = Prompt.ask("Nome Completo")
    cpf = Prompt.ask("CPF (xxx.xxx.xxx-xx)")
    email = Prompt.ask("E-mail Institucional")
    senha = Prompt.ask("Senha (mín. 8 caracteres)", password=True, show_default=False)
    telefone = Prompt.ask("Telefone (11 dígitos)")
    data_nasc = Prompt.ask("Data de Nascimento (DD/MM/AAAA)")
    
    try:
        with console.status("[bold green]Processando cadastro..."):
            escola_alvo = repo.buscar_escola_por_id(int(escola_id))
            
            if not escola_alvo:
                console.print("[red]❌ Erro: Escola não encontrada.[/red]")
                input("\nPressione [Enter] para voltar...")
                return

            from src.models.gestor import Gestor
            novo_gestor = Gestor(
                None, nome, cpf, email, senha, telefone, data_nasc, escola_alvo
            )

            resultado_modelo = sec.realizar_cadastro(novo_gestor, escola_alvo)

            if "Sucesso" in resultado_modelo:
                repo.salvar_usuario(novo_gestor) 
                repo.vincular_gestor_escola(novo_gestor.id_usuario, escola_alvo.id_escola)
                console.print(f"\n[bold green]✅ {resultado_modelo}[/bold green]")
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
            status_atual = "Ativo" if gestor.status else "Inativo"
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
            # Sincroniza escolas antes de enviar
            sec.municipio_responsavel.escolas_situadas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
            resultado = sec.enviar_mensagem(titulo, conteudo)
            console.print(f"\n[bold green]✅ {resultado}[/bold green]")
        except Exception as e:
            console.print(f"[red]Erro ao enviar: {e}[/red]")
    
    input("\nPressione [Enter] para continuar...")

def comando_pagamento(sec: Secretario):
    """Aprova e paga demandas."""
    console.clear()
    escola_id = Prompt.ask("Digite o ID da Escola")
    demanda_id = Prompt.ask("Digite o ID da Demanda")

    try:
        escola = repo.buscar_escola_por_id(int(escola_id))
        if not escola:
            console.print("[red]❌ Escola não encontrada.[/red]")
        else:
            console.print(f"\n[yellow]Analisando demanda...[/yellow]")
            aviso = sec.administrar_solicitacoes(escola, demanda_id, "APROVAR")
            console.print(f"[blue]{aviso}[/blue]")

            if "aprovada" in aviso.lower():
                confirmacao = sec.gerenciar_verba(escola, demanda_id)
                # Persistência no Banco
                repo.atualizar_saldos(sec.municipio_responsavel, escola)
                repo.atualizar_status_demanda(demanda_id, "CONCLUIDA / PAGA")
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