import typer
from rich import print
from rich.table import Table
from src.cli.auth import auth_system  # Supondo que você tem esse gerenciador de sessão
from src.database.RepositorioGeral import RepositorioGeral
from src.models.secretario import Secretario

app = typer.Typer(help="Painel Administrativo do Secretário de Educação")
repo = RepositorioGeral()

def get_session_secretario() -> Secretario:
    """Recupera o secretário logado e valida o acesso."""
    user = auth_system.get_usuario_logado()
    if not isinstance(user, Secretario):
        print("[bold red] Acesso Negado: Comando exclusivo para Secretários.[/bold red]")
        raise typer.Exit(1)
    return user

@app.command()
def perfil():
    """Exibe o perfil completo do Secretário logado."""
    sec = get_session_secretario()
    print(sec.exibir_perfil())

@app.command()
def estatisticas_rede():
    """Gera relatório de todas as escolas do município."""
    sec = get_session_secretario()
    
    # O Repo busca a lista de objetos Escola vinculados ao município do Secretário
    escolas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
    
    relatorio = sec.ver_estatisticas(escolas)
    print(f"[bold cyan]{relatorio}[/bold cyan]")

@app.command()
def nomear_gestor(
    gestor_id: int = typer.Argument(..., help="ID do usuário Gestor"),
    escola_id: int = typer.Argument(..., help="ID da Escola alvo")
):
    """Vincula um Gestor a uma Escola (Respeitando a Jurisdição)."""
    sec = get_session_secretario()
    
    # Busca os objetos reais no banco para passar para o método do Secretario
    gestor = repo.buscar_usuario_por_id(gestor_id)
    escola_alvo = repo.buscar_escola_por_id(escola_id)

    if not gestor or not escola_alvo:
        print("[red]❌ Gestor ou Escola não encontrados no banco.[/red]")
        return

    # Chama o seu método 'realizar_cadastro' que você escreveu
    try:
        resultado = sec.realizar_cadastro(gestor, escola_alvo)
        if "Sucesso" in resultado:
            # Alimenta o banco com a mudança
            repo.vincular_gestor_escola(gestor.id_usuario, escola_alvo.id_escola)
            print(f"[green] {resultado}[/green]")
        else:
            print(f"[yellow] {resultado}[/yellow]")
    except Exception as e:
        print(f"[red] Erro na regra de negócio: {e}[/red]")

@app.command()
def comunicado_global(titulo: str, conteudo: str):
    """Envia um comunicado para TODAS as escolas do município."""
    sec = get_session_secretario()
    
    # Carrega as escolas para a lista interna do objeto municipio (necessário para o seu método)
    sec.municipio_responsavel.escolas_situadas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
    
    resultado = sec.enviar_mensagem(titulo, conteudo)
    print(f"[bold blue] {resultado}[/bold blue]")

@app.command()
def gerenciar_pagamento(escola_id: int, demanda_id: str):
    """Aprova e paga uma demanda financeira de uma escola."""
    sec = get_session_secretario()
    escola = repo.buscar_escola_por_id(escola_id)
    
    if not escola:
        print("[red] Escola não encontrada.[/red]")
        return

    # 1. Administrar (Aprovar)
    print(f"--- Analisando demanda {demanda_id} ---")
    aviso_aprovacao = sec.administrar_solicitacoes(escola, demanda_id, "APROVAR")
    print(aviso_aprovacao)

    # 2. Se aprovado, Gerenciar Verba (Pagar)
    if "aprovada" in aviso_aprovacao.lower():
        confirmacao = sec.gerenciar_verba(escola, demanda_id)
        # Atualiza o saldo da escola e do municipio no banco
        repo.atualizar_saldos(sec.municipio_responsavel, escola)
        # Atualiza o status da demanda no banco
        repo.atualizar_status_demanda(demanda_id, "CONCLUIDA / PAGA")
        print(f"[bold gold1]{confirmacao}[/bold gold1]")

@app.command()
def mudar_status_gestor(gestor_id: int, ativo: bool):
    """Ativa ou Desativa um Gestor da rede municipal."""
    sec = get_session_secretario()
    gestor = repo.buscar_usuario_por_id(gestor_id)

    if not gestor:
        print("[red] Gestor não encontrado.[/red]")
        return

    resultado = sec.gerenciar_status_gestor(gestor, ativo)
    if "Sucesso" in resultado:
        repo.atualizar_status_usuario(gestor_id, ativo)
        print(f"[green] {resultado}[/green]")
    else:
        print(f"[red] {resultado}[/red]")