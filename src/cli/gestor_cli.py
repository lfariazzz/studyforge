import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
import os

console = Console()

def menu_interativo_gestor(usuario, repo=None):
    """
    Interface CLI completa para o Gestor. 
    Recebe o objeto 'usuario' (Gestor) e opcionalmente o 'repo' para persistência.
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

        # 2. Cabeçalho Elegante
        console.print(Panel(
            f"[bold blue]SISTEMA STUDYFORGE - PAINEL DO GESTOR[/]\n"
            f"[white]Bem-vindo(a), [bold]{usuario.nome}[/] | Unidade: [yellow]{nome_unidade}[/][/]",
            border_style="blue",
            expand=False
        ))
        
        # 3. Menu de Opções formatado
        menu_text = (
            "[bold cyan][1][/] Ver Meu Perfil Completo\n"
            "[bold cyan][2][/] Ver Estatísticas da Escola (Dashboard)\n"
            "[bold cyan][3][/] Gerenciar Turmas\n"
            "[bold cyan][4][/] Gerenciar Professores\n"
            "[bold cyan][5][/] Gerenciar Alunos\n"
            "[bold cyan][6][/] Publicar Comunicado no Mural\n"
            "[bold cyan][7][/] Administrar Solicitações/Demandas\n"
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
            administrar_demandas(usuario)
        elif opcao == "0":
            console.print("[yellow]Efetuando logout... Até logo![/]")
            break

# --- FUNÇÕES DE APOIO (AÇÕES DO GESTOR) ---

def exibir_perfil_gestor(usuario):
    console.clear()
    console.print("[bold cyan]🔍 BUSCANDO DADOS DO PERFIL...[/]")
    try:
        perfil_data = usuario.exibir_perfil()
        console.print(Panel(str(perfil_data), title="Meu Perfil", border_style="green"))
    except Exception as e:
        console.print(f"[red]Erro ao processar perfil no modelo: {e}[/]")
    input("\nPressione [Enter] para voltar ao menu...")

def exibir_dashboard_estatisticas(usuario):
    console.clear()
    try:
        stats = usuario.ver_estatisticas()
        
        if isinstance(stats, str): 
            console.print(f"[bold red]⚠️ {stats}[/]")
        else:
            table = Table(title=f"📊 Dashboard: {stats.get('escola', 'Unidade')}", show_header=True, header_style="bold magenta")
            table.add_column("Indicador", style="cyan")
            table.add_column("Valor", style="white", justify="right")
            
            table.add_row("Total de Alunos", str(stats.get('total_alunos', 0)))
            table.add_row("Total de Professores", str(stats.get('total_professores', 0)))
            table.add_row("Total de Turmas", str(stats.get('total_turmas', 0)))
            table.add_row("Capacidade Utilizada", f"{stats.get('capacidade_utilizada_pct', 0)}%")
            
            verba = stats.get('verba_disponivel', 0.0)
            table.add_row("Verba Disponível", f"[green]R$ {verba:,.2f}[/]")
            
            console.print(table)
    except Exception as e:
        console.print(f"[red]Erro ao gerar dashboard: {e}[/]")
    input("\nPressione [Enter] para voltar...")

def gerenciar_turmas(usuario, repo):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE TURMAS[/]", border_style="cyan"))
    print("1. Listar Turmas Existentes")
    print("2. Criar Nova Turma")
    print("0. Voltar")
    
    sub_op = Prompt.ask("Escolha", choices=["0", "1", "2"])
    
    if sub_op == "1":
        turmas = usuario.escola_associada._turmas_existentes
        table = Table(title="Turmas da Unidade")
        table.add_column("Nome", style="yellow")
        table.add_column("Turno", style="cyan")
        table.add_column("Alunos", justify="center")
        
        for t in turmas:
            table.add_row(t.nome, t.turno, str(len(t.alunos_matriculados)))
        console.print(table)
        input("\nEnter para continuar...")
    
    elif sub_op == "2":
        nome = Prompt.ask("Nome da Turma (ex: 9º Ano B)")
        turno = Prompt.ask("Turno", choices=["MANHÃ", "TARDE", "NOITE"])
        capacidade = int(Prompt.ask("Capacidade Máxima"))
        # Aqui chamaria o método do gestor: usuario.criar_turma(nome, turno, capacidade, repo)
        console.print("[green]✅ Turma em processo de criação (aguardando Repo)...[/]")
        typer.pause()

def gerenciar_professores(usuario, repo):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE PROFESSORES[/]", border_style="yellow"))
    # Lógica de listagem e alocação...
    console.print("[yellow]Em desenvolvimento: Listando corpo docente...[/]")
    typer.pause()

def gerenciar_alunos(usuario, repo):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE ALUNOS[/]", border_style="magenta"))
    print("1. Matricular Aluno")
    print("2. Pesquisar Aluno por CPF")
    print("0. Voltar")
    
    sub_op = Prompt.ask("Escolha", choices=["0", "1", "2"])
    if sub_op == "1":
        nome = Prompt.ask("Nome Completo")
        cpf = Prompt.ask("CPF")
        # usuario.matricular_aluno(nome, cpf, ...)
        console.print(f"[green]✅ Processando matrícula de {nome}...[/]")
        typer.pause()

def publicar_comunicado(usuario):
    titulo = Prompt.ask("Título do Comunicado")
    conteudo = Prompt.ask("Conteúdo da Mensagem")
    try:
        resultado = usuario.enviar_mensagem(titulo, conteudo)
        console.print(f"\n[green]✅ {resultado}[/]")
    except Exception as e:
        console.print(f"[red]Erro: {e}[/]")
    typer.pause()

def administrar_demandas(usuario):
    console.clear()
    try:
        demandas = usuario.administrar_solicitacoes()
        console.print(Panel(str(demandas), title="[bold yellow]Demandas da Unidade[/]", border_style="yellow"))
    except Exception as e:
        console.print(f"[red]Erro ao carregar demandas: {e}[/]")
    input("\nPressione [Enter] para continuar...")