from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.gestor import Gestor

console = Console()
app = typer.Typer(help="Portal do Gestor - StudyForge")
repo = RepositorioGeral()


def get_session_gestor() -> Gestor:
    user = auth_system.obter_usuario_logado()
    if not isinstance(user, Gestor):
        console.print("[bold red]Acesso negado: área exclusiva para gestores.[/bold red]")
        raise typer.Exit(1)
    return user


def menu_interativo_gestor(usuario, repo_local=None):
    """
    Interface CLI completa para o Gestor com gatilhos de RN.
    """
    # Garante contexto mínimo para o menu mesmo quando chamado pelo login sem repo.
    repo_local = repo_local or repo
    if repo_local and not getattr(usuario, "escola_associada", None):
        try:
            gestor_db = repo_local.buscar_gestor_por_id(usuario.id_usuario)
            if gestor_db and gestor_db.escola_associada:
                usuario.escola_associada = gestor_db.escola_associada
        except Exception:
            pass

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
        exibir_notificacoes_urgentes(usuario, repo_local)
        
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
            gerenciar_turmas(usuario, repo_local)
        elif opcao == "4":
            gerenciar_professores(usuario, repo_local)
        elif opcao == "5":
            gerenciar_alunos(usuario, repo_local)
        elif opcao == "6":
            publicar_comunicado(usuario)
        elif opcao == "7":
            administrar_demandas(usuario, repo_local)
        elif opcao == "0":
            console.print("[yellow]Efetuando logout... Até logo![/]")
            break

# --- FUNÇÕES DE APOIO (AÇÕES DO GESTOR) ---

def exibir_notificacoes_urgentes(usuario, repo_local):
    """ RN06 - Notifica automaticamente demandas Críticas ou de Evasão (RN02) """
    if not repo_local or not usuario.escola_associada:
        return
    
    try:
        # Busca no repo as demandas vinculadas a esta escola
        id_escola = usuario.escola_associada.id_escola
        demandas = repo_local.buscar_demandas_por_escola(id_escola)
        
        # Filtra o que é urgente ou aguarda licitação (RN03)
        alertas = [d for d in demandas if d.prioridade.upper() == "ALTA" or "LICITAÇÃO" in d.status.upper()]
        
        if alertas:
            msg = ""
            for d in alertas[:3]: # Mostra os 3 primeiros
                msg += f"• [bold red]URGENTE:[/] {d.descricao[:70]}...\n"
            
            console.print(Panel(msg.strip(), title="ALERTAS DO SISTEMA", border_style="red"))
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
        # Hidrata dados de escola para evitar estatísticas vazias.
        escola = usuario.escola_associada
        if escola:
            turmas = repo.listar_turmas_por_escola(escola.id_escola)
            for turma in turmas:
                turma._alunos_matriculados = repo.buscar_alunos_por_turma(turma.id_turma)
            escola._turmas_existentes = turmas
            escola._professores_empregados = repo.buscar_professores_por_escola(escola.id_escola)

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

def administrar_demandas(usuario, repo_local):
    """ Exibe e gerencia as demandas da Factory (RN02, RN03, RN04) """
    console.clear()
    console.print(Panel("[bold yellow]CENTRAL DE DEMANDAS E LICITAÇÕES[/]", border_style="yellow"))
    
    if not repo_local:
        console.print("[red]Erro: Repositório não conectado.[/red]")
        input("\nPressione [Enter] para voltar...")
        return

    if not usuario.escola_associada:
        console.print("[red]Escola não vinculada ao gestor.[/red]")
        input("\nPressione [Enter] para voltar...")
        return

    try:
        demandas = repo_local.buscar_demandas_por_escola(usuario.escola_associada.id_escola)
        
        if not demandas:
            console.print("[green]Nenhuma demanda pendente para esta unidade.[/green]")
        else:
            table = Table(title="Lista de Solicitações")
            table.add_column("ID", style="cyan")
            table.add_column("Título/Descrição", style="white")
            table.add_column("Prioridade", justify="center")
            table.add_column("Status", style="yellow")
            
            for d in demandas:
                cor = "red" if d.prioridade.upper() == "ALTA" else "white"
                table.add_row(str(d.id_demanda), d.descricao[:60], f"[{cor}]{d.prioridade}[/]", d.status)
            
            console.print(table)

            if Prompt.ask("Deseja atualizar status de alguma demanda?", choices=["s", "n"], default="n") == "s":
                id_dem = Prompt.ask("Digite o ID da demanda")
                novo_status = Prompt.ask(
                    "Novo status",
                    choices=["PENDENTE", "APROVADO", "RECUSADO", "EM_EXECUCAO", "CONCLUIDO"],
                    default="EM_EXECUCAO",
                )
                try:
                    repo_local.atualizar_status_demanda(int(id_dem), novo_status)
                    console.print("[green]Status atualizado com sucesso.[/green]")
                except Exception as e:
                    console.print(f"[red]Erro ao atualizar demanda: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Erro ao carregar demandas: {e}[/]")
    
    input("\nPressione [Enter] para voltar...")

def gerenciar_turmas(usuario, repo_local):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE TURMAS[/]", border_style="cyan"))
    if not repo_local or not usuario.escola_associada:
        console.print("[red]Escola não vinculada ou repositório indisponível.[/red]")
        input("\nPressione [Enter] para voltar...")
        return

    turmas = repo_local.listar_turmas_por_escola(usuario.escola_associada.id_escola)
    if not turmas:
        console.print("[yellow]Nenhuma turma cadastrada na unidade.[/yellow]")
    else:
        table = Table(title="Turmas da unidade")
        table.add_column("ID", style="cyan")
        table.add_column("Nome", style="white")
        table.add_column("Ano", style="green")
        table.add_column("Turno", style="magenta")
        table.add_column("Alunos", justify="right")

        for turma in turmas:
            alunos = repo_local.buscar_alunos_por_turma(turma.id_turma)
            table.add_row(
                str(turma.id_turma),
                turma.nome,
                str(turma.ano_letivo),
                str(turma.turno),
                str(len(alunos)),
            )
        console.print(table)

    input("\nPressione [Enter] para voltar...")

def gerenciar_professores(usuario, repo_local):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE PROFESSORES[/]", border_style="yellow"))
    if not repo_local or not usuario.escola_associada:
        console.print("[red]Escola não vinculada ou repositório indisponível.[/red]")
        input("\nPressione [Enter] para voltar...")
        return

    professores = repo_local.buscar_professores_por_escola(usuario.escola_associada.id_escola)
    if not professores:
        console.print("[yellow]Nenhum professor cadastrado na unidade.[/yellow]")
    else:
        table = Table(title="Professores da unidade")
        table.add_column("ID", style="cyan")
        table.add_column("Nome", style="white")
        table.add_column("Área", style="green")
        table.add_column("RF", style="magenta")
        table.add_column("Status", justify="center")

        for prof in professores:
            status = "Ativo" if getattr(prof, "status", True) else "Inativo"
            table.add_row(str(prof.id_usuario), prof.nome, prof.area_atuacao, prof.registro_funcional, status)
        console.print(table)

    input("\nPressione [Enter] para voltar...")

def gerenciar_alunos(usuario, repo_local):
    console.clear()
    console.print(Panel("[bold]GERENCIAMENTO DE ALUNOS[/]", border_style="magenta"))
    if not repo_local or not usuario.escola_associada:
        console.print("[red]Escola não vinculada ou repositório indisponível.[/red]")
        input("\nPressione [Enter] para voltar...")
        return

    alunos = repo_local.buscar_alunos_por_escola(usuario.escola_associada.id_escola)
    if not alunos:
        console.print("[yellow]Nenhum aluno cadastrado na unidade.[/yellow]")
    else:
        table = Table(title="Alunos da unidade")
        table.add_column("ID", style="cyan")
        table.add_column("Nome", style="white")
        table.add_column("Matrícula", style="green")
        table.add_column("Turma", style="magenta")
        table.add_column("Status", justify="center")

        for aluno in alunos:
            turma = getattr(aluno, "turma_associada", None)
            turma_nome = turma.nome if turma else "Sem turma"
            matricula = getattr(aluno, "id_matricula", None) or getattr(aluno, "_matricula", "N/A")
            status = "Ativo" if getattr(aluno, "status", True) else "Inativo"
            table.add_row(str(aluno.id_usuario), aluno.nome, str(matricula), turma_nome, status)
        console.print(table)

    input("\nPressione [Enter] para voltar...")

def publicar_comunicado(usuario):
    titulo = Prompt.ask("Título")
    conteudo = Prompt.ask("Mensagem")
    try:
        mensagem = usuario.enviar_mensagem(titulo, conteudo)
        if usuario.escola_associada:
            repo.salvar_noticia(usuario.escola_associada.id_escola, titulo, conteudo, autor=usuario.nome)
        console.print(f"\n[green]{mensagem}[/green]")
    except Exception as e:
        console.print(f"\n[red]Erro ao publicar comunicado: {e}[/red]")
    typer.pause()


@app.command()
def perfil():
    gestor = get_session_gestor()
    exibir_perfil_gestor(gestor)


@app.command()
def dashboard():
    gestor = get_session_gestor()
    exibir_dashboard_estatisticas(gestor)


@app.command()
def demandas():
    gestor = get_session_gestor()
    administrar_demandas(gestor, repo)


@app.command()
def comunicado():
    gestor = get_session_gestor()
    publicar_comunicado(gestor)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        gestor = get_session_gestor()
        menu_interativo_gestor(gestor, repo)


if __name__ == "__main__":
    app()
