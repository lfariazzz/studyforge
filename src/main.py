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
def login():
    """Faz login no sistema e inicia o painel correspondente."""
    # Como não estamos mais usando invoke/forward complexo, 
    # o Typer gerencia os prompts automaticamente aqui.
    cpf = typer.prompt("Digite seu CPF")
    senha = typer.prompt("Sua senha")
    
    sucesso, mensagem = auth_system.fazer_login(cpf, senha)
    console.print(mensagem)
    
    if sucesso:
        tipo = auth_system.obter_tipo_usuario_atual()
        usuario = auth_system.obter_usuario_logado()

        if tipo == "SECRETARIO":
            from src.cli.secretario_cli import menu_interativo_secretario
            menu_interativo_secretario(usuario)
        elif tipo == "GESTOR":
            from src.cli.gestor_cli import menu_interativo_gestor
            menu_interativo_gestor(usuario)
        elif tipo == "ALUNO":
            from src.cli.aluno_cli import menu_interativo_aluno
            menu_interativo_aluno(usuario)
        elif tipo == "PROFESSOR":
            from src.cli.professor_cli import menu_interativo_professor
            menu_interativo_professor(usuario)
        else:
            console.print(f"[yellow]Painel interativo para {tipo} em desenvolvimento.[/yellow]")
    else:
        if typer.confirm("Deseja tentar o login novamente?"):
            login() # Aqui a recursão simples funciona sem erro de ctx

@app.command()
def logout() -> None:
    """Encerra a sessão atual."""
    mensagem = auth_system.fazer_logout()
    console.print(mensagem)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Menu Inicial do StudyForge."""
    # Se o usuário digitou um comando (ex: python -m src.main login), 
    # o programa executa o comando e ignora o menu.
    if ctx.invoked_subcommand is not None:
        return

    # Se rodou apenas 'python -m src.main', entra no loop do menu principal
    while True:
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
            login() # Chama a função diretamente, sem ctx.forward/invoke
        elif opcao == "2" or opcao == "help":
            console.print(ctx.get_help())
            typer.pause() # Pausa para o usuário ler o help antes de limpar a tela
        elif opcao == "0" or opcao == "sair":
            console.print("[yellow]Até logo![/yellow]")
            raise typer.Exit()
        else:
            console.print("[red]Opção inválida.[/red]")

if __name__ == "__main__":
    app()