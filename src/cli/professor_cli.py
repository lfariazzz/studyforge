from datetime import date, datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.nota import Nota
from src.models.professor import Professor
from src.services.avaliador_frequencia import AvaliadorFrequencia

console = Console()
app = typer.Typer(help="Portal do Professor - StudyForge")
repo = RepositorioGeral()


def _pausar_tela() -> None:
    """Pausa simples e estável para uso dentro do menu interativo."""
    input("\nPressione [Enter] para continuar...")


def get_session_professor() -> Professor:
    """Valida se o usuário logado é um Professor (RN01)."""
    user = auth_system.obter_usuario_logado()
    if not isinstance(user, Professor):
        console.print("[bold red]Acesso negado: espaço restrito a professores.[/bold red]")
        raise typer.Exit(1)
    return user


def _carregar_turmas_do_professor(prof: Professor):
    turmas = repo.listar_turmas_por_professor(prof.id_usuario)
    prof._turmas_associadas = turmas
    return turmas


def _selecionar_turma_do_professor(prof: Professor, titulo: str = "Minhas turmas"):
    turmas = _carregar_turmas_do_professor(prof)
    if not turmas:
        console.print("[yellow]Você não possui turmas vinculadas.[/yellow]")
        return None, []

    table = Table(title=titulo)
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Ano", style="green")
    table.add_column("Turno", style="magenta")
    for turma in turmas:
        table.add_row(str(turma.id_turma), turma.nome, str(turma.ano_letivo), str(turma.turno))
    console.print(table)

    id_turma = typer.prompt("Digite o ID da turma")
    turma_sel = next((t for t in turmas if str(t.id_turma) == str(id_turma)), None)
    if not turma_sel:
        console.print("[red]Turma inválida ou sem permissão.[/red]")
        return None, turmas

    return turma_sel, turmas


def _selecionar_aluno_da_turma(turma_sel):
    alunos = repo.listar_alunos_por_turma(turma_sel.id_turma)
    if not alunos:
        console.print("[yellow]Turma sem alunos cadastrados.[/yellow]")
        return None, []

    table_alunos = Table(title=f"Alunos da turma {turma_sel.nome}")
    table_alunos.add_column("ID", style="cyan")
    table_alunos.add_column("Nome", style="white")
    for aluno in alunos:
        table_alunos.add_row(str(aluno.id_usuario), aluno.nome)
    console.print(table_alunos)

    id_aluno = typer.prompt("ID do aluno")
    aluno_sel = next((a for a in alunos if str(a.id_usuario) == str(id_aluno)), None)
    if not aluno_sel:
        console.print("[red]Aluno inválido para esta turma.[/red]")
        return None, alunos

    return aluno_sel, alunos


def exibir_cabecalho_professor(prof: Professor):
    console.clear()
    escola_nome = prof.escola_associada.nome if prof.escola_associada else "Escola não vinculada"
    console.print(
        Panel(
            f"[bold blue]STUDYFORGE - AREA DO DOCENTE[/bold blue]\n"
            f"[cyan]Prof.:[/cyan] {prof.nome} | [cyan]RF:[/cyan] {prof.registro_funcional} | [cyan]Area:[/cyan] {prof.area_atuacao}\n"
            f"[cyan]Escola:[/cyan] {escola_nome}",
            expand=False,
        )
    )


def _acao_perfil(prof: Professor) -> None:
    turmas = _carregar_turmas_do_professor(prof)
    nomes_turmas = []
    for turma in turmas:
        nome_turma = getattr(turma, "nome", None)
        if nome_turma and nome_turma not in nomes_turmas:
            nomes_turmas.append(nome_turma)

    turmas_str = ", ".join(nomes_turmas) if nomes_turmas else "Nenhuma turma alocada"
    status_conta = "Ativa" if getattr(prof, "status", True) else "Inativa"
    perfil_texto = (
        f"Nome: {prof.nome}\n"
        f"RF: {prof.registro_funcional}\n"
        f"Titulação: {prof.titulacao}\n"
        f"Área: {prof.area_atuacao}\n"
        f"E-mail: {prof.email}\n"
        f"Turmas: {turmas_str}\n"
        f"Status: {status_conta}"
    )

    console.print(Panel(perfil_texto, title="Dados funcionais", border_style="blue"))
    _pausar_tela()


@app.command()
def perfil():
    """Exibe o perfil funcional e turmas regentes (RN01)."""
    prof = get_session_professor()
    _acao_perfil(prof)


@app.command()
def minhas_turmas():
    """Lista turmas vinculadas ao professor e quantidade de alunos."""
    prof = get_session_professor()
    turmas = _carregar_turmas_do_professor(prof)

    if not turmas:
        console.print("[yellow]Você não possui turmas vinculadas.[/yellow]")
        _pausar_tela()
        return

    table = Table(title="Turmas sob sua regência")
    table.add_column("ID", style="cyan")
    table.add_column("Turma", style="white")
    table.add_column("Ano", style="green")
    table.add_column("Turno", style="magenta")
    table.add_column("Alunos", justify="right", style="yellow")

    for turma in turmas:
        total_alunos = len(repo.listar_alunos_por_turma(turma.id_turma))
        table.add_row(
            str(turma.id_turma),
            turma.nome,
            str(turma.ano_letivo),
            str(turma.turno),
            str(total_alunos),
        )

    console.print(table)
    _pausar_tela()


@app.command()
def lancar_notas():
    """Lançamento de notas com persistência no banco."""
    prof = get_session_professor()
    turma_sel, _ = _selecionar_turma_do_professor(prof)
    if not turma_sel:
        _pausar_tela()
        return

    aluno_sel, _ = _selecionar_aluno_da_turma(turma_sel)
    if not aluno_sel:
        _pausar_tela()
        return

    valor = typer.prompt("Valor da nota (0-10)", type=float)
    tipo = typer.prompt("Tipo (Prova/Trabalho/A2)")

    try:
        nota_obj = Nota(
            id_nota=None,
            id_aluno=aluno_sel.id_usuario,
            id_turma=turma_sel.id_turma,
            disciplina=prof.area_atuacao,
            valor=valor,
            data=date.today().isoformat(),
            tipo=tipo,
            aluno=aluno_sel,
        )
        repo.salvar_nota(nota_obj)
        console.print(f"[bold green]Nota {valor} lançada para {aluno_sel.nome}.[/bold green]")
    except Exception as e:
        console.print(f"[red]Erro ao salvar nota: {e}[/red]")

    _pausar_tela()


@app.command()
def registrar_aula():
    """Registra aula e chamada com tentativa de gatilho RN02."""
    prof = get_session_professor()
    turma_sel, _ = _selecionar_turma_do_professor(prof, titulo="Selecione a turma da aula")
    if not turma_sel:
        _pausar_tela()
        return

    conteudo = typer.prompt("Conteúdo ministrado")

    try:
        id_diario = repo.criar_diario_classe(
            id_turma=turma_sel.id_turma,
            id_professor=prof.id_usuario,
            data_aula=date.today().isoformat(),
            conteudo=conteudo,
            disciplina=prof.area_atuacao,
        )
    except Exception as e:
        console.print(f"[red]Erro ao criar diário: {e}[/red]")
        _pausar_tela()
        return

    alunos = repo.listar_alunos_por_turma(turma_sel.id_turma)
    console.print("\n[bold yellow]Iniciando chamada[/bold yellow]")
    for aluno in alunos:
        presente = typer.confirm(f"O aluno {aluno.nome} está presente?", default=True)
        status = "PRESENTE" if presente else "AUSENTE"
        try:
            repo.registrar_frequencia(id_diario, aluno.id_usuario, status)
        except Exception as e:
            console.print(f"[red]Falha ao registrar frequência de {aluno.nome}: {e}[/red]")

    console.print("[bold green]Aula e chamada registradas com sucesso.[/bold green]")

    console.print("[cyan]Verificando indicadores de evasão (RN02)...[/cyan]")
    try:
        turma_completa = repo.buscar_turma_por_id(turma_sel.id_turma)
        if turma_completa:
            # RN02 depende de turma com alunos, diário e presenças hidratados.
            turma_completa._alunos_matriculados = repo.listar_alunos_por_turma(turma_sel.id_turma)
            turma_completa._diario_de_classe = repo.listar_diario_por_turma(turma_sel.id_turma)

            for aluno_obj in turma_completa._alunos_matriculados:
                aluno_obj._presencas = repo.listar_frequencia_por_aluno(aluno_obj.id_usuario)

        avaliador = AvaliadorFrequencia()
        mes_atual = datetime.now().month
        nova_demanda = avaliador.verificar_media_frequencia_mensal(turma_completa, mes_atual)
        if nova_demanda:
            repo.salvar_demanda(nova_demanda)
            console.print(
                Panel(
                    "[bold red]ALERTA RN02 DISPARADO![/]\n"
                    "Frequência mensal abaixo de 75%. Uma demanda foi gerada para o Gestor.",
                    border_style="red",
                )
            )
    except Exception as e:
        console.print(f"[dim red]Não foi possível processar alerta automático: {e}[/dim red]")

    _pausar_tela()


@app.command()
def enviar_material():
    """Publica material didático para uma turma e registra comunicado da escola."""
    prof = get_session_professor()
    turma_sel, _ = _selecionar_turma_do_professor(prof, titulo="Selecione a turma para envio de material")
    if not turma_sel:
        _pausar_tela()
        return

    nome_material = typer.prompt("Nome do material")
    link = typer.prompt("Link do material")

    try:
        mensagem = prof.enviar_material(turma_sel, nome_material, link)
        console.print(f"[bold green]{mensagem}[/bold green]")
    except Exception as e:
        console.print(f"[red]Erro ao registrar material na turma: {e}[/red]")
        _pausar_tela()
        return

    if prof.escola_associada:
        try:
            titulo = f"Material de {prof.area_atuacao} - {turma_sel.nome}"
            conteudo = (
                f"O(a) professor(a) {prof.nome} publicou o material '{nome_material}' "
                f"para a turma {turma_sel.nome}.\nAcesso: {link}"
            )
            repo.salvar_noticia(prof.escola_associada.id_escola, titulo, conteudo, autor=prof.nome)
            console.print("[green]Comunicado do material publicado no mural da escola.[/green]")
        except Exception as e:
            console.print(f"[dim yellow]Material salvo, mas falhou a publicação no mural: {e}[/dim yellow]")

    _pausar_tela()


@app.command()
def historico_aulas():
    """Exibe o histórico de aulas registradas no diário de classe."""
    prof = get_session_professor()

    try:
        diarios = repo.listar_diario_por_professor(prof.id_usuario)
    except Exception as e:
        console.print(f"[red]Erro ao buscar diário de classe: {e}[/red]")
        _pausar_tela()
        return

    if not diarios:
        console.print("[yellow]Nenhuma aula registrada até o momento.[/yellow]")
        _pausar_tela()
        return

    table = Table(title="Histórico de aulas")
    table.add_column("ID", style="cyan")
    table.add_column("Data", style="green")
    table.add_column("Disciplina", style="white")
    table.add_column("Conteúdo", style="magenta")

    for diario in diarios:
        data_str = "-"
        if hasattr(diario, "data"):
            data_obj = diario.data
            if hasattr(data_obj, "strftime"):
                data_str = data_obj.strftime("%d/%m/%Y")
            else:
                data_str = str(data_obj)

        conteudo = str(getattr(diario, "conteudo", ""))
        if len(conteudo) > 60:
            conteudo = conteudo[:57] + "..."

        table.add_row(
            str(getattr(diario, "id_diario", "-")),
            data_str,
            str(getattr(diario, "disciplina", prof.area_atuacao)),
            conteudo,
        )

    console.print(table)
    _pausar_tela()


@app.command()
def painel_turma():
    """Mostra indicadores rápidos da turma (alunos, média de notas e frequência)."""
    prof = get_session_professor()
    turma_sel, _ = _selecionar_turma_do_professor(prof, titulo="Selecione a turma para o painel")
    if not turma_sel:
        _pausar_tela()
        return

    alunos = repo.listar_alunos_por_turma(turma_sel.id_turma)
    if not alunos:
        console.print("[yellow]Turma sem alunos cadastrados.[/yellow]")
        _pausar_tela()
        return

    medias = []
    frequencias = []

    for aluno in alunos:
        try:
            notas_aluno = repo.listar_notas_por_aluno(aluno.id_usuario)
        except Exception:
            notas_aluno = []
        notas_turma = [n.valor for n in notas_aluno if str(getattr(n, "id_turma", "")) == str(turma_sel.id_turma)]
        if notas_turma:
            medias.append(sum(notas_turma) / len(notas_turma))

        try:
            freq_aluno = repo.listar_frequencia_por_aluno(aluno.id_usuario)
        except Exception:
            freq_aluno = []

        if freq_aluno:
            presencas = sum(1 for f in freq_aluno if str(getattr(f, "status", "")).upper() == "PRESENTE")
            frequencias.append((presencas / len(freq_aluno)) * 100)

    media_geral = (sum(medias) / len(medias)) if medias else 0.0
    freq_geral = (sum(frequencias) / len(frequencias)) if frequencias else 0.0

    painel = Table(title=f"Painel da Turma {turma_sel.nome}")
    painel.add_column("Indicador", style="cyan")
    painel.add_column("Valor", style="white", justify="right")
    painel.add_row("Total de alunos", str(len(alunos)))
    painel.add_row("Média geral de notas", f"{media_geral:.2f}")
    painel.add_row("Frequência média", f"{freq_geral:.1f}%")
    painel.add_row("Disciplina", prof.area_atuacao)
    console.print(painel)
    _pausar_tela()


def menu_interativo_professor(prof: Professor):
    while True:
        exibir_cabecalho_professor(prof)

        table = Table(show_header=False, box=None)
        table.add_row("1", "Meu perfil")
        table.add_row("2", "Minhas turmas")
        table.add_row("3", "Lançar notas")
        table.add_row("4", "Registrar aula e chamada")
        table.add_row("5", "Enviar material")
        table.add_row("6", "Histórico de aulas")
        table.add_row("7", "Painel da turma")
        table.add_row("0", "Sair")

        console.print(table)
        opcao = Prompt.ask(
            "\nEscolha uma ação",
            choices=["0", "1", "2", "3", "4", "5", "6", "7"],
            default="0",
        )

        if opcao == "1":
            _acao_perfil(prof)
        elif opcao == "2":
            minhas_turmas()
        elif opcao == "3":
            lancar_notas()
        elif opcao == "4":
            registrar_aula()
        elif opcao == "5":
            enviar_material()
        elif opcao == "6":
            historico_aulas()
        elif opcao == "7":
            painel_turma()
        elif opcao == "0":
            auth_system.fazer_logout()
            break
        else:
            console.print("[red]Opção inválida.[/red]")
            _pausar_tela()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        prof = get_session_professor()
        menu_interativo_professor(prof)


if __name__ == "__main__":
    app()
