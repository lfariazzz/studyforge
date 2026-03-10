import sys
import os
from datetime import date, datetime

# Garante o path do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Imports do seu projeto
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.professor import Professor
from src.services.avaliador_frequencia import AvaliadorFrequencia # Import necessário para RN02

console = Console()
app = typer.Typer(help="Portal do Professor - StudyForge")
repo = RepositorioGeral()

# --- AUXILIARES ---

def get_session_professor() -> Professor:
    """Valida se o usuário logado é um Professor (RN01)."""
    user = auth_system.obter_usuario_logado()
    if not isinstance(user, Professor):
        console.print("[bold red]❌ Acesso Negado: Espaço restrito a Professores.[/bold red]")
        raise typer.Exit(1)
    return user

def exibir_cabecalho_professor(prof: Professor):
    """Cabeçalho visual com dados do RF e Área."""
    console.clear()
    escola_nome = prof.escola_associada.nome if prof.escola_associada else "Escola não vinculada"
    console.print(Panel(
        f"[bold blue]STUDYFORGE - ÁREA DO DOCENTE[/bold blue]\n"
        f"[cyan]Prof.:[/cyan] {prof.nome} | [cyan]RF:[/cyan] {prof.registro_funcional} | [cyan]Área:[/cyan] {prof.area_atuacao}\n"
        f"[cyan]Escola:[/cyan] {escola_nome}",
        expand=False
    ))

# --- COMANDOS TYPER ---

@app.command()
def perfil():
    """Exibe o perfil funcional e turmas regentes (RN01)."""
    prof = get_session_professor()
    # Hidrata as turmas do banco antes de exibir para garantir integridade
    prof._turmas_associadas = repo.listar_turmas_por_professor(prof._id_usuario)
    console.print(Panel(prof.exibir_perfil(), title="Dados Funcionais", border_style="blue"))
    typer.pause()

@app.command()
def lancar_notas():
    """Menu para lançamento de notas (RN04 - Base para lacuna de conteúdo)."""
    prof = get_session_professor()
    turmas = repo.listar_turmas_por_professor(prof._id_usuario)
    
    if not turmas:
        console.print("[yellow]Você não possui turmas vinculadas.[/yellow]")
        return typer.pause()

    table = Table(title="Minhas Turmas")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    for t in turmas:
        table.add_row(str(t._id_turma), t.nome)
    console.print(table)
    
    id_t = typer.prompt("Digite o ID da Turma")
    turma_sel = next((t for t in turmas if str(t._id_turma) == id_t), None)
    
    if not turma_sel:
        return console.print("[red]Turma inválida ou sem permissão.[/red]")

    alunos = repo.listar_alunos_por_turma(id_t)
    table_alunos = Table(title=f"Alunos da Turma {turma_sel.nome}")
    table_alunos.add_column("ID", style="cyan")
    table_alunos.add_column("Nome", style="white")
    for a in alunos:
        table_alunos.add_row(str(a._id_usuario), a.nome)
    console.print(table_alunos)
    
    id_a = typer.prompt("ID do Aluno")
    aluno_sel = next((a for a in alunos if str(a._id_usuario) == id_a), None)

    if aluno_sel:
        valor = typer.prompt("Valor da Nota (0-10)", type=float)
        tipo = typer.prompt("Tipo (Prova/Trabalho/A2)")
        
        try:
            repo.salvar_nota(aluno_sel._id_usuario, prof.area_atuacao, valor, tipo, date.today().isoformat())
            console.print(f"[bold green]✅ Nota {valor} lançada para {aluno_sel.nome}![/bold green]")
        except Exception as e:
            console.print(f"[red]Erro ao salvar nota: {e}[/red]")
    
    typer.pause()

@app.command()
def registrar_aula():
    """Registra aula e realiza chamada com GATILHO AUTOMÁTICO RN02."""
    prof = get_session_professor()
    turmas = repo.listar_turmas_por_professor(prof._id_usuario)
    
    if not turmas:
        return console.print("[yellow]Nenhuma turma encontrada.[/yellow]")

    # Listar turmas para escolha
    table = Table(title="Selecione a Turma para a Aula")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    for t in turmas:
        table.add_row(str(t._id_turma), t.nome)
    console.print(table)

    id_t = typer.prompt("ID da Turma")
    turma_sel = next((t for t in turmas if str(t._id_turma) == id_t), None)
    
    if not turma_sel:
        return console.print("[red]Turma não encontrada.[/red]")

    conteudo = typer.prompt("Conteúdo Ministrado")
    
    # 1. Registrar o Diário (Aula)
    id_diario = repo.criar_diario_classe(id_t, prof._id_usuario, date.today().isoformat(), conteudo)
    
    # 2. Realizar a Chamada
    alunos = repo.listar_alunos_por_turma(id_t)
    console.print("\n[bold yellow]--- INICIANDO CHAMADA ---[/bold yellow]")
    for a in alunos:
        presente = typer.confirm(f"O aluno {a.nome} está presente?", default=True)
        status = "PRESENTE" if presente else "FALTA"
        repo.registrar_frequencia(id_diario, a._id_usuario, status)
    
    console.print("[bold green]✅ Aula e Chamada registradas![/bold green]")

    # --- AUTOMAÇÃO RN02: GATILHO DE EVASÃO ---
    console.print("[cyan]Verificando indicadores de evasão (RN02)...[/cyan]")
    try:
        # Precisamos carregar o objeto turma completo com alunos e diários para o avaliador funcionar
        turma_completa = repo.buscar_turma_por_id(id_t) 
        avaliador = AvaliadorFrequencia()
        mes_atual = datetime.now().month
        
        # O método abaixo já usa a Factory internamente
        nova_demanda = avaliador.verificar_media_frequencia_mensal(turma_completa, mes_atual)
        
        if nova_demanda:
            repo.salvar_demanda(nova_demanda)
            console.print(Panel(f"[bold red]ALERTA RN02 DISPARADO![/]\nFrequência mensal abaixo de 75%. "
                                f"Uma demanda foi gerada para o Gestor.", border_style="red"))
    except Exception as e:
        console.print(f"[dim red]Não foi possível processar alerta automático: {e}[/dim red]")

    typer.pause()

# --- MENU INTERATIVO ---

def menu_interativo_professor(prof: Professor):
    while True:
        exibir_cabecalho_professor(prof)
        
        table = Table(show_header=False, box=None)
        table.add_row("1", "👤 Meu Perfil")
        table.add_row("2", "📝 Lançar Notas")
        table.add_row("3", "📅 Registrar Aula e Chamada")
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

if __name__ == "__main__":
    app()
