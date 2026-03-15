"""Registro dinâmico dos subcomandos de perfis da CLI."""

import importlib
import typer

PERFIS = ["aluno", "professor", "gestor", "secretario"]

def registrar_comandos(app: typer.Typer) -> None:
    """
    Adiciona os Typer dos diversos perfis ao aplicativo principal.

    Args:
        app: instância de `typer.Typer` principal (em `src.main`)
    """
    for perfil in PERFIS:
        try:
            module = importlib.import_module(f"src.cli.{perfil}_cli")
            # cada módulo deve expor uma variável `app` do tipo Typer
            if hasattr(module, "app") and isinstance(getattr(module, "app"), typer.Typer):
                app.add_typer(getattr(module, "app"), name=perfil)
        except ModuleNotFoundError:
            # módulo ainda não criado; ignora temporariamente
            pass

