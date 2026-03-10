import typer
from rich import print
from rich.console import Console
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.aluno import Aluno

app = typer.Typer(help="Portal do Aluno")
repo = RepositorioGeral()
console = Console()

def get_session_aluno() -> Aluno:
    """Recupera o aluno logado e valida o acesso."""
    user = auth_system.get_usuario_logado()
    if not isinstance(user, Aluno):
        print("[bold red]❌ Acesso Negado: Comando exclusivo para Alunos.[/bold red]")
        raise typer.Exit(1)
    return user

def carregar_objeto_turma(aluno: Aluno):
    """Auxiliar: Garante que turma_associada seja um objeto e não apenas um ID."""
    if aluno.turma_associada and isinstance(aluno.turma_associada, (int, str)):
        turma_obj = repo.buscar_turma_por_id(aluno.turma_associada)
        if turma_obj:
            aluno.turma_associada = turma_obj

@app.command()
def perfil():
    """Exibe o perfil completo do Aluno logado (Método: exibir_perfil)."""
    aluno = get_session_aluno()
    carregar_objeto_turma(aluno) # Necessário para exibir o nome da turma no perfil
    print(aluno.exibir_perfil())

@app.command()
def boletim():
    """Exibe o boletim com médias (Método: visualizar_notas)."""
    aluno = get_session_aluno()
    
    # Busca notas do banco e alimenta o dicionário self.notas do modelo
    notas_db = repo.listar_notas_por_aluno(aluno._id_usuario)
    if notas_db:
        aluno.notas = {} # Limpa cache local
        for n in notas_db:
            aluno.adicionar_nota(n.disciplina, n.valor)
    
    print(f"\n[bold blue]📝 Boletim Escolar: {aluno.nome}[/bold blue]")
    print(f"[cyan]{aluno.visualizar_notas()}[/cyan]")

@app.command()
def frequencia():
    """Exibe histórico detalhado (Método: ver_frequencia)."""
    aluno = get_session_aluno()
    
    # Sincroniza presenças do banco para a lista self.presencas
    presencas_db = repo.listar_frequencia_por_aluno(aluno._id_usuario)
    aluno.presencas = presencas_db if presencas_db else []
    
    print(f"\n[bold green]📅 Relatório de Frequência[/bold green]")
    print(f"[white]{aluno.ver_frequencia()}[/white]")

@app.command()
def horario():
    """Consulta o quadro de horários (Método: ver_horario)."""
    aluno = get_session_aluno()
    carregar_objeto_turma(aluno) # Requer objeto Turma para acessar obter_quadro_horario()
    
    print(f"\n[bold yellow]⏰ Quadro de Horários[/bold yellow]")
    print(aluno.ver_horario())

@app.command()
def mural():
    """Acessa as notícias da escola (Método: ver_noticias)."""
    aluno = get_session_aluno()
    carregar_objeto_turma(aluno) # Requer objeto Turma -> Escola -> _mural_oficial
    
    print(f"\n[bold magenta]🏛️ Mural da Escola[/bold magenta]")
    print(aluno.ver_noticias())

@app.command()
def baixar_material(nome: str = typer.Argument(..., help="Nome exato do material")):
    """Faz download de materiais (Método: baixar_material)."""
    aluno = get_session_aluno()
    carregar_objeto_turma(aluno)
    
    resultado = aluno.baixar_material(nome)
    if "Download" in resultado:
        print(f"[green]✅ {resultado}[/green]")
    else:
        print(f"[yellow]⚠️ {resultado}[/yellow]")