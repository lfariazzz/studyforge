import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

# Imports do seu projeto
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.secretario import Secretario

console = Console()
app = typer.Typer(help="Painel Administrativo do Secretário de Educação")
repo = RepositorioGeral()

# --- AUXILIARES ---

def get_session_secretario() -> Secretario:
    """Recupera o secretário logado e valida o acesso."""
    user = auth_system.get_usuario_logado()
    if not isinstance(user, Secretario):
        console.print("[bold red]❌ Acesso Negado: Comando exclusivo para Secretários.[/bold red]")
        raise typer.Exit(1)
    return user

def exibir_cabecalho(sec: Secretario):
    """Exibe um painel visual no topo do menu."""
    console.clear()
    mun_nome = sec.municipio_responsavel.nome if sec.municipio_responsavel else "N/A"
    console.print(Panel(
        f"[bold blue]STUDYFORGE - PAINEL DO SECRETÁRIO[/bold blue]\n"
        f"[cyan]Usuário:[/cyan] {sec.nome} | [cyan]Município:[/cyan] {mun_nome} | [cyan]Depto:[/cyan] {sec.departamento}",
        expand=False
    ))

# --- COMANDOS TYPER (@app.command) ---

@app.command()
def perfil():
    """Exibe o perfil completo do Secretário logado."""
    sec = get_session_secretario()
    console.print(Panel(sec.exibir_perfil(), title="Meu Perfil", border_style="green"))
    if not typer.Context.resilient_parsing: # Evita travar se for chamado via menu
        typer.pause()

@app.command()
def estatisticas_rede():
    """Gera relatório de todas as escolas do município."""
    sec = get_session_secretario()
    with console.status("[bold green]Buscando dados da rede..."):
        escolas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
        relatorio = sec.ver_estatisticas(escolas)
    
    console.print(f"\n[bold cyan]📊 RELATÓRIO DE REDE[/bold cyan]")
    console.print(relatorio)
    typer.pause()

@app.command()
def comunicado_global(
    titulo: str = typer.Option(..., prompt="Título do Comunicado"),
    conteudo: str = typer.Option(..., prompt="Conteúdo da Mensagem")
):
    """Envia um comunicado para TODAS as escolas do município."""
    sec = get_session_secretario()
    # Sincroniza escolas para a lógica de negócio
    sec.municipio_responsavel.escolas_situadas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
    
    resultado = sec.enviar_mensagem(titulo, conteudo)
    console.print(f"[bold blue]ℹ️ {resultado}[/bold blue]")
    typer.pause()

@app.command()
def gerenciar_pagamento(
    escola_id: int = typer.Option(..., prompt="ID da Escola"),
    demanda_id: str = typer.Option(..., prompt="ID da Demanda")
):
    """Aprova e paga uma demanda financeira de uma escola."""
    sec = get_session_secretario()
    escola = repo.buscar_escola_por_id(escola_id)
    
    if not escola:
        console.print("[red]❌ Escola não encontrada.[/red]")
        return

    console.print(f"\n[yellow]--- Analisando demanda {demanda_id} ---[/yellow]")
    aviso_aprovacao = sec.administrar_solicitacoes(escola, demanda_id, "APROVAR")
    console.print(f"[blue]{aviso_aprovacao}[/blue]")

    if "aprovada" in aviso_aprovacao.lower():
        confirmacao = sec.gerenciar_verba(escola, demanda_id)
        # Sincroniza com o Banco
        repo.atualizar_saldos(sec.municipio_responsavel, escola)
        repo.atualizar_status_demanda(demanda_id, "CONCLUIDA / PAGA")
        console.print(f"[bold yellow]💰 {confirmacao}[/bold yellow]")
    
    typer.pause()

# --- MENU INTERATIVO (O Loop que você queria) ---

def menu_interativo_secretario(sec: Secretario):
    """Loop principal de navegação interativa."""
    while True:
        exibir_cabecalho(sec)
        
        table = Table(show_header=False, box=None)
        table.add_row("1", "👤 Ver Meu Perfil")
        table.add_row("2", "📊 Estatísticas da Rede")
        table.add_row("3", "📢 Enviar Comunicado Global")
        table.add_row("4", "💸 Gerenciar Pagamentos/Demandas")
        table.add_row("0", "🚪 Logout e Sair")
        
        console.print(table)
        opcao = typer.prompt("\nEscolha uma ação", default="0")

        if opcao == "1":
            perfil()
        elif opcao == "2":
            estatisticas_rede()
        elif opcao == "3":
            comunicado_global()
        elif opcao == "4":
            gerenciar_pagamento()
        elif opcao == "0":
            console.print("[bold red]Encerrando sessão...[/bold red]")
            auth_system.fazer_logout()
            break
        else:
            console.print("[red]Opção inválida![/red]")
            typer.pause()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Entrada padrão para o comando 'secretario'"""
    if ctx.invoked_subcommand is None:
        sec = get_session_secretario()
        menu_interativo_secretario(sec)