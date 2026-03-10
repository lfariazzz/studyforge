import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

# Imports do seu projeto
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.aluno import Aluno

console = Console()
app = typer.Typer(help="Portal do Aluno - StudyForge")
repo = RepositorioGeral()

# --- AUXILIARES ---

def get_session_aluno() -> Aluno:
    """Recupera o aluno logado e valida o acesso."""
    user = auth_system.get_usuario_logado()
    if not isinstance(user, Aluno):
        console.print("[bold red]❌ Acesso Negado: Comando exclusivo para Alunos.[/bold red]")
        raise typer.Exit(1)
    return user

def exibir_cabecalho_aluno(aluno: Aluno):
    """Exibe um painel visual no topo do menu do aluno."""
    console.clear()
    turma_nome = "Não Vinculada"
    if aluno.turma_associada:
        # Se for objeto, pega o nome; se for ID, pode-se buscar no repo
        turma_nome = aluno.turma_associada.nome if hasattr(aluno.turma_associada, 'nome') else f"ID: {aluno.turma_associada}"
        
    console.print(Panel(
        f"[bold green]STUDYFORGE - PORTAL DO ALUNO[/bold green]\n"
        f"[cyan]Nome:[/cyan] {aluno.nome} | [cyan]Matrícula:[/cyan] {aluno.id_matricula} | [cyan]Turma:[/cyan] {turma_nome}",
        expand=False
    ))

# --- COMANDOS TYPER (@app.command) ---

@app.command()
def perfil():
    """Exibe o perfil completo e dados cadastrais."""
    aluno = get_session_aluno()
    console.print(Panel(aluno.exibir_perfil(), title="Meu Perfil", border_style="blue"))
    typer.pause()

@app.command()
def boletim():
    """Consulta as notas e médias por disciplina."""
    aluno = get_session_aluno()
    with console.status("[bold blue]Carregando boletim..."):
        # Sincroniza notas do banco para o objeto aluno
        notas_db = repo.listar_notas_por_aluno(aluno._id_usuario)
        aluno.notas = {} # Limpa para recarregar
        for n in notas_db:
            aluno.adicionar_nota(n._disciplina, n._valor)
            
    console.print(f"\n[bold magenta]📝 BOLETIM ESCOLAR[/bold magenta]")
    console.print(aluno.visualizar_notas())
    typer.pause()

@app.command()
def frequencia():
    """Exibe o histórico de presença e faltas."""
    aluno = get_session_aluno()
    with console.status("[bold yellow]Consultando frequência..."):
        # Busca frequências do banco
        freq_db = repo.listar_frequencia_por_aluno(aluno._id_usuario)
        # Mapeia para o formato que o método ver_frequencia() da sua classe espera
        aluno.presencas = []
        for f in freq_db:
            aluno.presencas.append({
                "data": f._id_diario, # Ou buscar a data real no diário via repo
                "presenca": True if f._status == "PRESENTE" else False
            })

    console.print(f"\n[bold yellow]📅 HISTÓRICO DE FREQUÊNCIA[/bold yellow]")
    console.print(aluno.ver_frequencia())
    typer.pause()

@app.command()
def noticias():
    """Acessa o mural de notícias da escola."""
    aluno = get_session_aluno()
    # Para ver notícias, precisamos garantir que a escola está carregada via Turma
    if aluno.turma_associada:
        with console.status("[bold cyan]Lendo mural da escola..."):
            # Se turma_associada for apenas um ID no banco, precisamos hidratar o objeto
            if isinstance(aluno.turma_associada, (int, str)):
                aluno.turma_associada = repo.buscar_turma_por_id(aluno.turma_associada)
            
        console.print(aluno.ver_noticias())
    else:
        console.print("[red]Você não possui uma turma vinculada para ver notícias.[/red]")
    typer.pause()

# --- MENU INTERATIVO ---

def menu_interativo_aluno(aluno: Aluno):
    """Loop principal de navegação para o Aluno."""
    while True:
        exibir_cabecalho_aluno(aluno)
        
        table = Table(show_header=False, box=None)
        table.add_row("1", "👤 Meu Perfil")
        table.add_row("2", "📝 Ver Notas (Boletim)")
        table.add_row("3", "📅 Ver Frequência")
        table.add_row("4", "📢 Mural de Notícias")
        table.add_row("0", "🚪 Sair")
        
        console.print(table)
        opcao = typer.prompt("\nEscolha uma opção", default="0")

        if opcao == "1":
            perfil()
        elif opcao == "2":
            boletim()
        elif opcao == "3":
            frequencia()
        elif opcao == "4":
            noticias()
        elif opcao == "0":
            console.print("[bold red]Saindo...[/bold red]")
            auth_system.fazer_logout()
            break
        else:
            console.print("[red]Opção inválida![/red]")
            typer.pause()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Entrada padrão para o comando 'aluno'"""
    if ctx.invoked_subcommand is None:
        aluno = get_session_aluno()
        menu_interativo_aluno(aluno)