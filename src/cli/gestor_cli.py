import typer
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.gestor import Gestor

app = typer.Typer(help="Portal de Gestão Escolar")
repo = RepositorioGeral()

def get_gestor_session() -> Gestor:
    user = auth_system.get_usuario_logado()
    if not isinstance(user, Gestor):
        typer.secho("Erro: Acesso restrito a Gestores.", fg=typer.colors.RED)
        raise typer.Exit(1)
    return user

# --- COMANDO: VISUALIZAR PERFIL ---
@app.command()
def meu_perfil():
    """Exibe os dados detalhados do gestor e sua escola."""
    gestor = get_gestor_session()
    typer.echo(gestor.exibir_perfil())

# --- COMANDO: VER ESTATÍSTICA ESCOLA ---
@app.command()
def estatisticas():
    """Gera o relatório de ocupação, professores e verba da unidade."""
    gestor = get_gestor_session()
    dados = gestor.ver_estatisticas()
    
    if isinstance(dados, str): # Caso retorne erro de status
        typer.secho(dados, fg=typer.colors.YELLOW)
        return
    
    typer.secho(f"RELATÓRIO: {dados['escola']}", fg=typer.colors.CYAN, bold=True)
    typer.echo(f"Alunos: {dados['total_alunos']} | Profs: {dados['total_professores']}")
    typer.echo(f"Capacidade: {dados['capacidade_utilizada_pct']}% | Verba: R$ {dados['verba_disponivel']}")

# --- COMANDO: REALIZAR CADASTRO (O coração da alimentação) ---
@app.command()
def cadastrar_professor(nome: str, cpf: str, salario: float):
    """Cria um professor e o vincula à escola automaticamente."""
    from src.models.professor import Professor
    gestor = get_gestor_session()

    # 1. Cria o objeto Professor (Fábrica)
    novo_prof = Professor(None, nome, cpf, f"{nome}@edu.com", "123", "", "", "PROFESSOR")
    
    # 2. Usa o método da sua classe Gestor
    try:
        resultado = gestor.realizar_cadastro(novo_prof)
        repo.salvar_usuario(novo_prof) # Persiste a alimentação
        typer.secho(f"{resultado}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.echo(f"{e}")

# --- COMANDO: ENVIAR MENSAGEM ---
@app.command()
def comunicado(titulo: str, conteudo: str):
    """Publica uma notícia no mural da escola."""
    gestor = get_gestor_session()
    resultado = gestor.enviar_mensagem(titulo, conteudo)
    
    # IMPORTANTE: Aqui você salvaria a notícia no repo se tiver tabela mural
    typer.echo(resultado)

# --- COMANDO: REALIZAR SOLICITAÇÃO DE VERBA ---
@app.command()
def pedir_verba(valor: float, motivo: str):
    """Usa a DemandaFactory via Gestor para pedir recursos."""
    gestor = get_gestor_session()
    resultado = gestor.realizar_solicitacao(
        tipo_demanda="VERBA_INFRAESTRUTURA", 
        descricao=motivo, 
        valor=valor
    )
    typer.secho(resultado, fg=typer.colors.MAGENTA)

# --- COMANDO: ADMINISTRAR SOLICITAÇÕES ---
@app.command()
def lista_demandas():
    """Visualiza o status de todos os pedidos feitos à secretaria."""
    gestor = get_gestor_session()
    typer.echo(gestor.administrar_solicitacoes())