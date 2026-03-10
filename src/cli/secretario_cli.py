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

from src.models.escola import Escola

# Guardamos o construtor original
_original_init = Escola.__init__

def _novo_init(self, *args, **kwargs):
    # 1. LIMPEZA: Remove o que faz o Python reclamar de "argumento extra"
    kwargs.pop('id_localizacao', None)
    
    # 2. COMPLEMENTO: Se o repositório esquecer o id_endereco, nós damos um valor padrão
    if 'id_endereco' not in kwargs and 'id_endereco' not in args:
        kwargs['id_endereco'] = 0  # Ou None, dependendo da sua lógica

    # 3. EXECUÇÃO: Chama o init real com os dados corrigidos
    _original_init(self, *args, **kwargs)

# Substitui o comportamento da classe Escola apenas nesta execução
Escola.__init__ = _novo_init

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
    """Exibe o perfil completo do Secretário com a estética de Painel."""
    console.clear()
    try:
        # Pegamos a string formatada que vem do modelo
        dados_perfil = sec.exibir_perfil()
        
        # Exibimos dentro de um Painel, igual ao comando_perfil do Aluno
        console.print(Panel(
            dados_perfil, 
            title="👤 Meus Dados Administrativos", 
            border_style="blue", 
            expand=False
        ))
    except Exception as e:
        console.print(f"[red]Erro ao carregar perfil: {e}[/red]")
    
    # Padronizado com o estilo do Aluno
    input("\nPressione [Enter] para voltar ao menu...")

def comando_estatisticas(sec: Secretario):
    """Relatório da rede municipal."""
    console.clear()
    with console.status("[bold green]Buscando dados da rede..."):
        try:
            # 1. Busca as escolas do município
            escolas = repo.buscar_escolas_por_municipio(sec.municipio_responsavel.id_municipio)
            
            # 2. CARGA MANUAL DE DEMANDAS (O pulo do gato 🐈)
            for escola in escolas:
                # Busca as demandas no banco vinculadas a esta escola
                demandas_banco = repo.buscar_demandas_por_escola(escola.id_escola)
                # Injeta no atributo que o modelo Secretario usa para contar
                escola._solicitacoes_enviadas = demandas_banco

            # 3. Agora o relatório terá dados para contar!
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
    while True:
        exibir_cabecalho(sec)
        
        table = Table(show_header=False, box=None)
        table.add_row("[1]", "👤 Ver Meu Perfil")
        table.add_row("[2]", "📊 Estatísticas da Rede")
        table.add_row("[3]", "📢 Enviar Comunicado Global")
        table.add_row("[4]", "💸 Gerenciar Pagamentos")
        table.add_row("[0]", "🚪 Logout e Sair")
        console.print(table)
        
        opcao = Prompt.ask("\nEscolha uma opção", choices=["0", "1", "2", "3", "4"], default="0")

        if opcao == "1":
            comando_perfil(sec)
        elif opcao == "2":
            comando_estatisticas(sec)
        elif opcao == "3":
            comando_comunicado(sec)
        elif opcao == "4":
            comando_pagamento(sec)
        elif opcao == "0":
            break