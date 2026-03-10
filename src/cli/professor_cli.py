import typer
from rich import print
from rich.console import Console
from datetime import date
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.professor import Professor

app = typer.Typer(help="Portal do Professor")
repo = RepositorioGeral()
console = Console()

def get_session_professor() -> Professor:
    """Recupera o professor logado e valida o acesso."""
    user = auth_system.get_usuario_logado()
    if not isinstance(user, Professor):
        print("[bold red]❌ Acesso Negado: Comando exclusivo para Professores.[/bold red]")
        raise typer.Exit(1)
    return user

def sincronizar_turmas(professor: Professor):
    """Garante que as turmas do professor sejam objetos Turma carregados do banco."""
    turmas_ids = repo.listar_turmas_por_professor(professor.id_usuario)
    professor._turmas_associadas = [] # Limpa para evitar duplicatas
    for t_id in turmas_ids:
        turma_obj = repo.buscar_turma_por_id(t_id)
        if turma_obj:
            professor.turmas_associadas.append(turma_obj)

# -----------------
# COMANDOS
# -----------------

@app.command()
def perfil():
    """Exibe o perfil funcional e turmas (Método: exibir_perfil)."""
    prof = get_session_professor()
    sincronizar_turmas(prof)
    print(prof.exibir_perfil())

@app.command()
def lancar_nota(
    turma_id: int, 
    aluno_id: int, 
    disciplina: str, 
    valor: float, 
    tipo: str = "Prova"
):
    """Lança nota para um aluno (Método: lancar_nota)."""
    prof = get_session_professor()
    sincronizar_turmas(prof)
    
    turma = next((t for t in prof.turmas_associadas if t.id_turma == turma_id), None)
    aluno = repo.buscar_aluno_por_id(aluno_id)
    
    if not turma or not aluno:
        print("[bold red]❌ Erro: Turma ou Aluno não encontrados no sistema.[/bold red]")
        return

    # Executa lógica do modelo
    resultado = prof.lancar_nota(turma, aluno, disciplina, valor, tipo, date.today())
    
    if "sucesso" in resultado:
        # Persiste no banco de dados via repositório
        repo.salvar_nota_db(aluno_id, disciplina, valor, tipo, date.today(), turma_id)
        print(f"[bold green]✅ {resultado}[/bold green]")
    else:
        print(f"[bold yellow]⚠️ {resultado}[/bold yellow]")

@app.command()
def chamada(
    turma_id: int, 
    conteudo: str = typer.Option(..., prompt="Conteúdo ministrado hoje")
):
    """Realiza chamada interativa (Método: realizar_chamada)."""
    prof = get_session_professor()
    sincronizar_turmas(prof)
    
    turma = next((t for t in prof.turmas_associadas if t.id_turma == turma_id), None)
    if not turma:
        print("[bold red]❌ Erro: Turma não vinculada a este professor.[/bold red]")
        return

    print(f"\n[bold yellow]🔔 Iniciando Chamada - Turma: {turma.nome}[/bold yellow]")
    lista_presenca = []
    hoje = date.today()

    for aluno in turma.alunos_matriculados:
        presente = typer.confirm(f"O aluno {aluno.nome} está presente?")
        lista_presenca.append({"aluno": aluno, "presenca": presente})

    # Executa lógica do modelo (registra no aluno e na turma)
    resultado = prof.realizar_chamada(turma, hoje, lista_presenca, conteudo)
    
    # Persiste a aula e as frequências no banco
    repo.salvar_aula_db(turma_id, hoje, conteudo, prof.id_usuario)
    for registro in lista_presenca:
        repo.salvar_frequencia_db(registro['aluno'].id_usuario, hoje, registro['presenca'])

    print(f"\n[bold green]✅ {resultado}[/bold green]")

@app.command()
def enviar_material(
    turma_id: int, 
    nome_material: str, 
    link: str
):
    """Posta material didático (Método: enviar_material)."""
    prof = get_session_professor()
    sincronizar_turmas(prof)
    
    turma = next((t for t in prof.turmas_associadas if t.id_turma == turma_id), None)
    if not turma:
        print("[bold red]❌ Erro: Turma não encontrada.[/bold red]")
        return

    resultado = prof.enviar_material(turma, nome_material, link)
    
    if "sucesso" in resultado:
        repo.salvar_material_db(turma_id, nome_material, link)
        print(f"[bold blue]📂 {resultado}[/bold blue]")
    else:
        print(f"[bold yellow]⚠️ {resultado}[/bold yellow]")