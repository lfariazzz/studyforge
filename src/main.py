"""
Entry‑point da aplicação.  
Define a aplicação Typer e os primeiros comandos (login / logout).
Servirá também como ponto de extensão para os sub‑comandos de
aluno/professor/gestor/secretario, que serão registrados
posteriormente pelo commands_handler.
"""

import sys 
import os 

from typing import Optional

import typer

from src.cli.auth import auth_system
from src.cli.commands_handler import registrar_comandos
from src.cli.secretario_cli import get_session_secretario

app = typer.Typer(help="CLI do StudyForge – gerencie demandas, usuários e mais.")

# registra dinamicamente os sub‑comandos de cada perfil
registrar_comandos(app)


@app.command()
def login(
    cpf: str = typer.Option(..., help="CPF no formato XXX.XXX.XXX-XX"),
    senha: str = typer.Option(..., help="Senha do usuário (mín. 8 caracteres)"),
) -> None:
    """Faz login no sistema e inicia sessão."""
    sucesso, mensagem = auth_system.fazer_login(cpf, senha)
    typer.echo(mensagem)
    if not sucesso:
        raise typer.Exit(code=1)


@app.command()
def logout() -> None:
    """Encerra a sessão atual (se houver)."""
    mensagem = auth_system.fazer_logout()
    typer.echo(mensagem)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    Callback executado sempre. Se nenhum subcomando for invocado, exibe
    instruções básicas.
    """
    if ctx.invoked_subcommand is None:
        typer.echo("StudyForge CLI – execute 'studyforge --help' para ver os comandos disponíveis.")


if __name__ == "__main__":
    app()