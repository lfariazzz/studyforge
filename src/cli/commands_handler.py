"""
Módulo responsável por adicionar os sub‑comandos específicos de cada
perfil à aplicação Typer principal.

Cada grupo de comandos (aluno, professor, etc.) reside num ficheiro próprio
(e.g. aluno_commands.py).  Esta rotina apenas importa dinamicamente esses
módulos e regista os `Typer` internos no `app` passado como argumento.
"""

from typing import List
import importlib
import typer
from src.cli.secretario_cli import app as secretario_app
from src.cli.aluno_cli import app as aluno_app
from src.cli.professor_cli import app as professor_app

def registrar_comandos(main_app):
    main_app.add_typer(secretario_app, name="secretario")

PERFIS = ["aluno", "professor", "gestor", "secretario"]

def registrar_comandos(app: typer.Typer) -> None:
    """
    Adiciona os Typer dos diversos perfis ao aplicativo principal.

    Args:
        app: instância de `typer.Typer` principal (em `src.main`)
    """
    for perfil in PERFIS:
        try:
            module = importlib.import_module(f"src.cli.{perfil}_commands")
            # cada módulo deve expor uma variável `app` do tipo Typer
            if hasattr(module, "app") and isinstance(getattr(module, "app"), typer.Typer):
                app.add_typer(getattr(module, "app"), name=perfil)
        except ModuleNotFoundError:
            # módulo ainda não criado; ignora temporariamente
            pass