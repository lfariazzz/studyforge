import sys
import os
from datetime import datetime

# Garante que o Python encontre as pastas do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Imports das bibliotecas (Rich e Typer)
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live

# --- CONFIGURAÇÃO GLOBAL (Resolve os sublinhados do console) ---
console = Console()

def menu_interativo_gestor(usuario, repo=None):
    """
    Interface CLI completa para o Gestor com gatilhos de RN.
    """
    while True:
        console.clear()
        
        # 1. Tratamento seguro para exibir a Unidade
        try:
            if usuario.escola_associada and hasattr(usuario.escola_associada, 'nome'):
                nome_unidade = usuario.escola_associada.nome
            else:
                nome_unidade = "Não vinculada"
        except Exception:
            nome_unidade = "Erro ao carregar unidade"

        # 2. Cabeçalho
        console.print(Panel(
            f"[bold blue]SISTEMA STUDYFORGE - PAINEL DO GESTOR[/]\n"
            f"[white]Bem-vindo(a), [bold]{usuario.nome}[/] | Unidade: [yellow]{nome_unidade}[/][/]",
            border_style="blue",
            expand=False
        ))

        # --- GATILHO AUTOMÁTICO DE ALERTAS (RN02 / RN06) ---
        exibir_notificacoes_urgentes(usuario, repo)
        
        # 3. Menu de Opções
        menu_text = (
            "[bold cyan][1][/] Ver Meu Perfil Completo\n"
            "[bold cyan][2][/] Ver Estatísticas da Escola (Dashboard)\n"
            "[bold cyan][3][/] Gerenciar Turmas\n"
            "[bold cyan][4][/] Gerenciar Professores\n"
            "[bold cyan][5][/] Gerenciar Alunos\n"
            "[bold cyan][6][/] Publicar Comunicado no Mural\n"
            "[bold cyan][7][/] Administrar Solicitações/Demandas [bold red](Alertas)[/]\n"
            "[bold red][0][/] Sair (Logout)"
        )
        console.print(Panel(menu_text, title="Menu de Ações", border_style="white"))
        
        opcao = Prompt.ask("\nEscolha uma ação", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default="2")

        if opcao == "1":
            exibir_perfil_gestor(usuario)
        elif opcao == "2":
            exibir_dashboard_estatisticas(usuario)
        elif opcao == "3":
            gerenciar_turmas(usuario, repo)
        elif opcao == "4":
            gerenciar_professores(usuario, repo)
        elif opcao == "5":
            gerenciar_alunos(usuario, repo)
        elif opcao == "6":
            publicar_comunicado(usuario)
        elif opcao == "7":
            administrar_demandas(usuario, repo)
        elif opcao == "0":
            console.print("[yellow]Efetuando logout... Até logo![/]")
            break

# --- FUNÇÕES DE APOIO (AÇÕES DO GESTOR) ---

def exibir_notificacoes_urgentes(usuario, repo):
    """ RN06 - Notifica automaticamente demandas Críticas ou de Evasão (RN02) """
    if not repo or not usuario.escola_associada:
        return
    
    try:
        # Busca no repo as demandas vinculadas a esta escola
        id_escola = usuario.escola_associada.id_escola
        demandas = repo.buscar_demandas_por_escola(id_escola)
        
        # Filtra o que é urgente ou aguarda licitação (RN03)
        alertas = [d for d in demandas if d.prioridade.upper() == "ALTA" or "LICITAÇÃO" in d.status.upper()]
        
        if alertas:
            msg = ""
            for d in alertas[:3]: # Mostra os 3 primeiros
                msg += f"• [bold red]URGENTE:[/] {d.descricao[:70]}...\n"
            
            console.print(Panel(msg.strip(), title="🚨 ALERTAS DO SISTEMA", border_style="red"))
    except Exception:
        pass # Não trava o menu se o banco falhar

def exibir_perfil_gestor(usuario):
    console.clear()
    console.print("[bold cyan]🔍 BUSCANDO DADOS DO PERFIL...[/]")
    try:
        perfil_data = usuario.exibir_perfil()
        console.print(Panel(str(perfil_data), title="Meu Perfil", border_style="green"))
    except Exception as e:
        console.print(f"[red]Erro ao processar perfil: {e}[/]")
    input("\nPressione [Enter] para voltar...")

def exibir_dashboard_estatisticas(usuario):
    """ RN09 - Monitora a lotação das salas """
    console.clear()
    try:
        stats = usuario.ver_estatisticas()
        
        if isinstance(stats, str): 
            console.print(f"[bold red]⚠️ {stats}[/]")
        else:
            table = Table(title=f"📊 Dashboard: {stats.get('escola', 'Unidade')}")
            table.add_column("Indicador", style="cyan")
            table.add_column("Valor", style="white", justify="right")
            
            table.add_row("Total de Alunos", str(stats.get('total_alunos', 0)))
            table.add_row("Total de Professores", str(stats.get('total_professores', 0)))
            
            # RN09 - Lógica de Cores para Lotação
            uso = stats.get('capacidade_utilizada_pct', 0)
            cor_uso = "red" if uso >= 90 else "green"
            table.add_row("Capacidade Utilizada", f"[{cor_uso}]{uso}%[/{cor_uso}]")
            
            verba = stats.get('verba_disponivel', 0.0)
            table.add_row("Verba Disponível", f"[bold green]R$ {verba:,.2f}[/]")
            
            console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao gerar dashboard: {e}[/]")
    input("\nPressione [Enter] para voltar...")

def administrar_demandas(usuario, repo):
    """ Exibe e gerencia as demandas da Factory (RN02, RN03, RN04) """
    console.clear()
    console.print(Panel("[bold yellow]CENTRAL DE DEMANDAS E LICITAÇÕES[/]", border_style="yellow"))
    
    if not repo:
        console.print("[red]Erro: Repositório não conectado.[/red]")
        return

    try:
        demandas = repo.buscar_demandas_por_escola(usuario.escola_associada.id_escola)
        
        if not demandas:
            console.print("[green]Nenhuma demanda pendente para esta unidade.[/green]")
        else:
            table = Table(title="Lista de Solicitações")
            table.add_column("Título/Descrição", style="white")
            table.add_column("Prioridade", justify="center")
            table.add_column("Status", style="yellow")
            
            for d in demandas:
                cor = "red" if d.prioridade.upper() == "ALTA" else "white"
                table.add_row(d.descricao[:60], f"[{cor}]{d.prioridade}[/]", d.status)
            
            console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao carregar demandas: {e}[/]")
    
    input("\nPressione [Enter] para voltar...")

def gerenciar_turmas(usuario, repo):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE TURMAS[/]", border_style="cyan"))
    print("1. Listar Turmas Existentes")
    print("2. Criar Nova Turma")
    print("0. Voltar")
    
    sub_op = Prompt.ask("Escolha", choices=["0", "1", "2"])
    if sub_op == "1":
        # ... lógica de listagem ...
        pass
    input("\nEm desenvolvimento... Enter para voltar.")

def gerenciar_professores(usuario, repo):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE PROFESSORES[/]", border_style="yellow"))
    input("\nEm desenvolvimento... Enter para voltar.")

def gerenciar_alunos(usuario, repo):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE ALUNOS[/]", border_style="magenta"))
    input("\nEm desenvolvimento... Enter para voltar.")

def publicar_comunicado(usuario):
    titulo = Prompt.ask("Título")
    conteudo = Prompt.ask("Mensagem")
    console.print(f"\n[green]✅ Comunicado '{titulo}' publicado![/]")
    typer.pause()