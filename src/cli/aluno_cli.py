import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional
from rich.prompt import Prompt

# Imports do seu projeto
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.aluno import Aluno

console = Console()
app = typer.Typer(help="Portal do Aluno - StudyForge")
repo = RepositorioGeral()

# --- AUXILIARES ---

# Removi a lógica de verificação de tipo_usuario que causava o erro
def exibir_cabecalho_aluno(aluno: Aluno):
    """Exibe um painel visual no topo do menu."""
    console.clear()
    
    # Tratamento seguro para Turma (evita erro se for ID ou Objeto)
    turma_info = "Não Vinculada"
    # Note o uso de _turma_associada para bater com seu __init__
    turma_attr = getattr(aluno, '_turma_associada', None)
    
    if turma_attr:
        if hasattr(turma_attr, 'nome'):
            turma_info = turma_attr.nome
        else:
            turma_info = f"ID: {turma_attr}"

    console.print(Panel(
        f"[bold green]STUDYFORGE - ÁREA DO ESTUDANTE[/bold green]\n"
        f"[cyan]Estudante:[/cyan] {aluno.nome} | [cyan]Matrícula:[/cyan] {getattr(aluno, '_id_matricula', 'N/A')}\n"
        f"[cyan]Turma:[/cyan] {turma_info} | [cyan]Frequência:[/cyan] {getattr(aluno, 'frequencia', 0)}%",
        border_style="green",
        expand=False
    ))

# --- FUNÇÕES DE AÇÃO (Agora recebem o objeto aluno diretamente) ---

def comando_perfil(aluno: Aluno):
    console.clear()
    try:
        dados = aluno.exibir_perfil()
        console.print(Panel(dados, title="👤 Meus Dados", border_style="blue", expand=False))
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
    
    # O input vazio garante que o programa espere o usuário antes de limpar a tela e voltar ao menu
    input("\nPressione [Enter] para voltar ao menu...")

def comando_boletim(aluno: Aluno):
    """Consulta as notas."""
    with console.status("[bold blue]Sincronizando notas..."):
        try:
            notas_db = repo.listar_notas_por_aluno(aluno._id_usuario)
            aluno.notas = notas_db
            console.print(f"\n[bold magenta]📝 BOLETIM ESCOLAR[/bold magenta]")
            console.print(aluno.visualizar_notas())
        except Exception as e:
            console.print(f"[red]Erro ao carregar boletim: {e}[/red]")
    input("\nPressione [Enter] para voltar ao menu...")

def comando_frequencia(aluno: Aluno):
    """Exibe histórico de presença."""
    with console.status("[bold yellow]Consultando diário..."):
        try:
            freq_db = repo.listar_frequencia_por_aluno(aluno._id_usuario)
            aluno._presencas = freq_db 
            console.print(f"\n[bold yellow]📅 HISTÓRICO DE FREQUÊNCIA[/bold yellow]")
            console.print(aluno.ver_frequencia())
        except Exception as e:
            console.print(f"[red]Erro ao carregar frequência: {e}[/red]")
    input("\nPressione [Enter] para voltar ao menu...")

# --- MENU INTERATIVO ---

def menu_interativo_aluno(aluno: Aluno):
    while True:
        exibir_cabecalho_aluno(aluno)
        
        print("\n[1] Ver Perfil")
        print("[2] Consultar Boletim")
        print("[3] Minha Frequência")
        print("[0] Sair")
        
        opcao = Prompt.ask("\nEscolha uma opção", choices=["0", "1", "2", "3"], default="0")

        if opcao == "1":
            comando_perfil(aluno)
        elif opcao == "2":
            comando_boletim(aluno)
        elif opcao == "3":
            comando_frequencia(aluno)
        elif opcao == "0":
            break