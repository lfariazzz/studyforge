import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from typing import Optional

# Imports do seu projeto
from src.cli.auth import auth_system
from src.database.RepositorioGeral import RepositorioGeral
from src.models.secretario import Secretario

console = Console()
app = typer.Typer(help="Painel Administrativo do Secretário de Educação")
repo = RepositorioGeral()

# --- AUXILIARES ---

def exibir_cabecalho(sec: Secretario):
    """Exibe um painel visual no topo do menu."""
    console.clear()
    # Uso seguro do atributo via property ou getattr
    mun_nome = sec.municipio_responsavel.nome if sec.municipio_responsavel else "N/A"
    
    console.print(Panel(
        f"[bold blue]STUDYFORGE - PAINEL DO SECRETÁRIO[/bold blue]\n"
        f"[cyan]Usuário:[/cyan] {sec.nome} | [cyan]Município:[/cyan] {mun_nome} | [cyan]Depto:[/cyan] {sec.departamento}",
        expand=False,
        border_style="blue"
    ))

# --- FUNÇÕES DE AÇÃO (Baseadas no modelo de Gestor/Aluno) ---

def comando_perfil(sec: Secretario):
    """Exibe o perfil completo do Secretário."""
    console.clear()
    try:
        # Imprime o perfil
        console.print(sec.exibir_perfil())
    except Exception as e:
        console.print(f"[red]Erro ao carregar perfil: {e}[/red]")
    
    # Força o Typer a parar tudo e esperar uma tecla
    print("\n")
    typer.pause(info="Pressione qualquer tecla para voltar ao menu...")

def comando_estatisticas(sec: Secretario):
    """Relatório da rede municipal."""
    console.clear()
    with console.status("[bold green]Buscando dados da rede..."):
        try:
            # Busca as escolas vinculadas ao ID do município do secretário
            escolas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
            relatorio = sec.ver_estatisticas(escolas)
            console.print(Panel(relatorio, title="📊 Relatório de Rede", border_style="cyan"))
        except Exception as e:
            console.print(f"[red]Erro ao gerar estatísticas: {e}[/red]")
    
    input("\nPressione [Enter] para voltar ao menu...")

def comando_comunicado(sec: Secretario):
    """Envia comunicado para todas as escolas."""
    console.print("\n[bold]Novo Comunicado Global[/bold]")
    titulo = Prompt.ask("Título")
    conteudo = Prompt.ask("Conteúdo")
    
    with console.status("[bold blue]Enviando..."):
        try:
            # Sincroniza escolas antes de enviar
            sec.municipio_responsavel.escolas_situadas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
            resultado = sec.enviar_mensagem(titulo, conteudo)
            console.print(f"\n[bold green]✅ {resultado}[/bold green]")
        except Exception as e:
            console.print(f"[red]Erro ao enviar: {e}[/red]")
    
    input("\nPressione [Enter] para continuar...")

def comando_pagamento(sec: Secretario):
    """Aprova e paga demandas."""
    console.clear()
    escola_id = Prompt.ask("Digite o ID da Escola")
    demanda_id = Prompt.ask("Digite o ID da Demanda")

    try:
        escola = repo.buscar_escola_por_id(int(escola_id))
        if not escola:
            console.print("[red]❌ Escola não encontrada.[/red]")
        else:
            console.print(f"\n[yellow]Analisando demanda...[/yellow]")
            aviso = sec.administrar_solicitacoes(escola, demanda_id, "APROVAR")
            console.print(f"[blue]{aviso}[/blue]")

            if "aprovada" in aviso.lower():
                confirmacao = sec.gerenciar_verba(escola, demanda_id)
                # Persistência no Banco
                repo.atualizar_saldos(sec.municipio_responsavel, escola)
                repo.atualizar_status_demanda(demanda_id, "CONCLUIDA / PAGA")
                console.print(f"[bold yellow]💰 {confirmacao}[/bold yellow]")
    except Exception as e:
        console.print(f"[red]Erro no processamento: {e}[/red]")
    
    input("\nPressione [Enter] para continuar...")

# --- MENU INTERATIVO ---

def menu_interativo_secretario(sec: Secretario):
    """Loop principal de navegação."""
    while True:
        exibir_cabecalho(sec)
        
        table = Table(show_header=False, box=None)
        table.add_row("[1]", "👤 Ver Meu Perfil")
        table.add_row("[2]", "📊 Estatísticas da Rede")
        table.add_row("[3]", "📢 Enviar Comunicado Global")
        table.add_row("[4]", "💸 Gerenciar Pagamentos")
        table.add_row("[0]", "🚪 Logout e Sair")
        
        console.print(table)
        
        # Usando o prompt padrão do Typer que é mais limpo para esse caso
        opcao = typer.prompt("\nEscolha uma opção", default="0")

        if opcao == "1":
            comando_perfil(sec)
        elif opcao == "2":
            comando_estatisticas(sec)
        elif opcao == "3":
            comando_comunicado(sec)
        elif opcao == "4":
            comando_pagamento(sec)
        elif opcao == "0":
            console.print("[bold red]Encerrando sessão...[/bold red]")
            auth_system.fazer_logout()
            break
        else:
            console.print("[yellow]Opção inválida.[/yellow]")
            typer.pause()