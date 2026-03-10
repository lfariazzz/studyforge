import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import date

# Imports do seu projeto
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.professor import Professor

console = Console()
app = typer.Typer(help="Portal do Professor - StudyForge")
repo = RepositorioGeral()

# --- AUXILIARES ---

def get_session_professor() -> Professor:
    """Valida se o usuário logado é um Professor."""
    user = auth_system.get_usuario_logado()
    if not isinstance(user, Professor):
        console.print("[bold red]❌ Acesso Negado: Espaço restrito a Professores.[/bold red]")
        raise typer.Exit(1)
    return user

def exibir_cabecalho_professor(prof: Professor):
    """Cabeçalho visual com dados do RF e Área."""
    console.clear()
    escola = prof.escola_associada.nome if hasattr(prof.escola_associada, 'nome') else "Escola não vinculada"
    console.print(Panel(
        f"[bold blue]STUDYFORGE - ÁREA DO DOCENTE[/bold blue]\n"
        f"[cyan]Prof.:[/cyan] {prof.nome} | [cyan]RF:[/cyan] {prof.registro_funcional} | [cyan]Área:[/cyan] {prof.area_atuacao}\n"
        f"[cyan]Escola:[/cyan] {escola}",
        expand=False
    ))

# --- COMANDOS TYPER ---

@app.command()
def perfil():
    """Exibe o perfil funcional e turmas regentes."""
    prof = get_session_professor()
    # Hidrata as turmas do banco antes de exibir
    prof._turmas_associadas = repo.listar_turmas_por_professor(prof._id_usuario)
    console.print(Panel(prof.exibir_perfil(), title="Dados Funcionais", border_style="blue"))
    typer.pause()

@app.command()
def lancar_notas():
    """Menu para lançamento de notas por turma e aluno."""
    prof = get_session_professor()
    turmas = repo.listar_turmas_por_professor(prof._id_usuario)
    
    if not turmas:
        console.print("[yellow]Você não possui turmas vinculadas.[/yellow]")
        return typer.pause()

    # 1. Selecionar Turma
    table = Table(title="Minhas Turmas")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    for t in turmas:
        table.add_row(str(t._id_turma), t._nome)
    console.print(table)
    
    id_t = typer.prompt("Digite o ID da Turma")
    turma_sel = next((t for t in turmas if str(t._id_turma) == id_t), None)
    
    if not turma_sel:
        return console.print("[red]Turma inválida.[/red]")

    # 2. Selecionar Aluno
    alunos = repo.listar_alunos_por_turma(id_t)
    table_alunos = Table(title=f"Alunos da Turma {turma_sel._nome}")
    table_alunos.add_column("ID", style="cyan")
    table_alunos.add_column("Nome", style="white")
    for a in alunos:
        table_alunos.add_row(str(a._id_usuario), a.nome)
    console.print(table_alunos)
    
    id_a = typer.prompt("ID do Aluno")
    aluno_sel = next((a for a in alunos if str(a._id_usuario) == id_a), None)

    if aluno_sel:
        # 3. Coletar Nota
        valor = typer.prompt("Valor da Nota (0-10)", type=float)
        tipo = typer.prompt("Tipo (Prova/Trabalho/A2)")
        
        # Persistência via Repositório (Refatorado)
        try:
            repo.salvar_nota(aluno_sel._id_usuario, prof.area_atuacao, valor, tipo, date.today().isoformat())
            console.print(f"[bold green]✅ Nota {valor} lançada para {aluno_sel.nome}![/bold green]")
        except Exception as e:
            console.print(f"[red]Erro ao salvar: {e}[/red]")
    
    typer.pause()

@app.command()
def registrar_aula():
    """Registra conteúdo ministrado e realiza a chamada."""
    prof = get_session_professor()
    turmas = repo.listar_turmas_por_professor(prof._id_usuario)
    
    # Seleção de turma simplificada
    id_t = typer.prompt("ID da Turma para a aula")
    turma_sel = next((t for t in turmas if str(t._id_turma) == id_t), None)
    
    if not turma_sel:
        return console.print("[red]Turma não encontrada ou sem acesso.[/red]")

    conteudo = typer.prompt("Conteúdo Ministrado")
    
    # Criar Diário de Classe no Banco
    id_diario = repo.criar_diario_classe(id_t, prof._id_usuario, date.today().isoformat(), conteudo)
    
    # Chamada Interativa
    alunos = repo.listar_alunos_por_turma(id_t)
    console.print("\n[bold yellow]--- INICIANDO CHAMADA ---[/bold yellow]")
    for a in alunos:
        presente = typer.confirm(f"O aluno {a.nome} está presente?", default=True)
        status = "PRESENTE" if presente else "FALTA"
        repo.registrar_frequencia(id_diario, a._id_usuario, status)
    
    console.print("[bold green]✅ Aula e Chamada finalizadas com sucesso![/bold green]")
    typer.pause()

# --- MENU INTERATIVO ---

def menu_interativo_professor(prof: Professor):
    while True:
        exibir_cabecalho_professor(prof)
        
        table = Table(show_header=False, box=None)
        table.add_row("1", "👤 Meu Perfil")
        table.add_row("2", "📝 Lançar Notas")
        table.add_row("3", "📅 Registrar Aula e Chamada")
        table.add_row("4", "📂 Enviar Material (Mock)")
        table.add_row("0", "🚪 Sair")
        
        console.print(table)
        opcao = typer.prompt("\nEscolha uma ação", default="0")

        if opcao == "1":
            perfil()
        elif opcao == "2":
            lancar_notas()
        elif opcao == "3":
            registrar_aula()
        elif opcao == "0":
            auth_system.fazer_logout()
            break
        else:
            console.print("[red]Opção inválida![/red]")
            typer.pause()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        prof = get_session_professor()
        menu_interativo_professor(prof)