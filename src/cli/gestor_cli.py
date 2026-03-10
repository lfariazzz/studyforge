import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def menu_interativo_gestor(usuario):
    """
    Interface CLI para o Gestor. 
    Recebe o objeto 'usuario' (que é uma instância de Gestor).
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
        
        # 3. Menu de Opções (Usando Rich para ficar bonito)
        print("\n[1] Ver Meu Perfil Completo")
        print("[2] Ver Estatísticas da Escola")
        print("[3] Publicar Comunicado no Mural")
        print("[4] Administrar Solicitações/Demandas")
        print("[0] Sair (Logout)")
        
        # Usamos Prompt do Rich que é mais integrado que o input padrão
        opcao = Prompt.ask("\nEscolha uma ação", choices=["0", "1", "2", "3", "4"], default="1")

        if opcao == "1":
            console.clear()
            console.print("[bold cyan] BUSCANDO DADOS DO PERFIL...[/]")
            
            # PROTEÇÃO: Se o spam continuar, o problema é dentro deste método abaixo:
            try:
                perfil_data = usuario.exibir_perfil()
                console.print(Panel(perfil_data, title="Meu Perfil", border_style="green"))
            except Exception as e:
                console.print(f"[red]Erro ao processar perfil no modelo: {e}[/]")
            
            input("\nPressione [Enter] para voltar ao menu...")

        elif opcao == "2":
            console.clear()
            exibir_dashboard_estatisticas(usuario)
            
        elif opcao == "3":
            titulo = Prompt.ask("Título do Comunicado")
            conteudo = Prompt.ask("Conteúdo da Mensagem")
            resultado = usuario.enviar_mensagem(titulo, conteudo)
            console.print(f"\n[green]✅ {resultado}[/]")
            typer.pause()
            
        elif opcao == "4":
            console.clear()
            # Mostra as demandas dentro de um painel formatado
            demandas = usuario.administrar_solicitacoes()
            console.print(Panel(str(demandas), title="[bold yellow]Demandas da Unidade[/]", border_style="yellow"))
            input("\nPressione [Enter] para continuar...")
            
        elif opcao == "0":
            console.print("[yellow]Efetuando logout...[/]")
            break

def exibir_dashboard_estatisticas(usuario):
    """Gera uma tabela visual usando o método ver_estatisticas() do seu modelo."""
    try:
        stats = usuario.ver_estatisticas()
        
        if isinstance(stats, str): 
            console.print(f"[bold red]⚠️ {stats}[/]")
            input("\nPressione [Enter] para voltar...")
            return

        table = Table(title=f"📊 Estatísticas: {stats.get('escola', 'Unidade')}", show_header=True, header_style="bold magenta")
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
    
    input("\nPressione [Enter] para voltar ao menu...")