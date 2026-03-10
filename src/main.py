import sys 
import os 
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

from src.cli.auth import auth_system
from src.cli.commands_handler import registrar_comandos

console = Console()
app = typer.Typer(
    help="CLI do StudyForge – gerencie demandas, usuários e mais.",
    add_completion=False 
)

# Registra os sub-comandos (secretario, gestor, aluno, etc.)
registrar_comandos(app)

@app.command()
def login(
    cpf: str = typer.Option(..., prompt="CPF", help="CPF no formato XXX.XXX.XXX-XX"),
    senha: str = typer.Option(..., prompt=True, hide_input=True, help="Senha do usuário"),
) -> None:
    """Faz login no sistema e inicia o painel correspondente."""
    sucesso, mensagem = auth_system.fazer_login(cpf, senha)
    console.print(mensagem)
    
    if sucesso:
        tipo = auth_system.obter_tipo_usuario_atual()
        usuario = auth_system.obter_usuario_logado()

        # Redirecionamento automático baseado no perfil
        if tipo == "SECRETARIO":
            from src.cli.secretario_cli import menu_interativo_secretario
            menu_interativo_secretario(usuario)
        elif tipo == "GESTOR":
            # Aqui chamamos o menu interativo que criamos no seu gestor_cli
            from src.cli.gestor_cli import menu_interativo_gestor
            menu_interativo_gestor(usuario)
        else:
            console.print(f"[yellow]Painel interativo para {tipo} em desenvolvimento.[/yellow]")
            console.print(f"Use: [bold]python -m src.main {tipo.lower()} --help[/bold] para comandos avulsos.")
    else:
        raise typer.Exit(code=1)

@app.command()
def logout() -> None:
    """Encerra a sessão atual."""
    mensagem = auth_system.fazer_logout()
    console.print(mensagem)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    Menu Inicial do StudyForge.
    Aparece quando você roda apenas 'python -m src.main'.
    """
    if ctx.invoked_subcommand is None:
        # Layout do Menu Inicial
        console.print(Panel.fit(
            "[bold cyan]STUDYFORGE - SISTEMA DE GESTÃO[/bold cyan]\n"
            "[white]Versão 1.0 - Módulo CLI[/white]",
            border_style="bright_blue"
        ))
        
        console.print("\n[bold]Menu de Acesso:[/bold]")
        console.print(" 1. [green]login[/green]  - Entrar no sistema")
        console.print(" 2. [blue]help[/blue]   - Ver lista de comandos")
        console.print(" 0. [red]sair[/red]   - Encerrar programa")
        
        opcao = typer.prompt("\nEscolha uma ação", default="1")
        
        if opcao == "1":
            # Invoca o comando de login definido acima
            ctx.invoke(login)
        elif opcao == "2" or opcao == "help":
            console.print(ctx.get_help())
        elif opcao == "0" or opcao == "sair":
            console.print("[yellow]Até logo![/yellow]")
            raise typer.Exit()
        else:
            console.print("[red]Opção inválida. Use --help para assistência.[/red]")

if __name__ == "__main__":
    app()