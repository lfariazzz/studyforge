import typer
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer(help="Painel de Gestão Escolar (Diretor/Gestor)")

# --- MAPEAMENTO DAS 9 FUNÇÕES REAIS DO GESTOR ---

@app.command()
def exibir_perfil():
    """[Ação 1] Mostra os dados detalhados do gestor e status da conta."""
    console.print(Panel("Chamando: [bold]Gestor.exibir_perfil()[/bold]", title="Perfil", border_style="blue"))

@app.command()
def exibir_total_alunos():
    """[Ação 2] Calcula e exibe o somatório de alunos em todas as turmas."""
    console.print("🔢 Chamando: [bold]Gestor._get_total_alunos()[/bold]")

@app.command()
def ver_estatistica():
    """[Ação 3] Gera o relatório consolidado de ocupação, frequência e verba."""
    console.print("📊 Chamando: [bold]Gestor.ver_estatisticas()[/bold]")

@app.command()
def realizar_cadastro():
    """[Ação 4] Registra novos alunos ou professores na unidade escolar."""
    console.print("📝 Chamando: [bold]Gestor.realizar_cadastro()[/bold]")

@app.command()
def enviar_mensagem():
    """[Ação 5] Publica um comunicado oficial no mural da escola."""
    console.print("📢 Chamando: [bold]Gestor.enviar_mensagem()[/bold]")

@app.command()
def realizar_solicitacao():
    """[Ação 6] Interface com a Factory para criar novas demandas."""
    console.print("🏗️ Chamando: [bold]Gestor.realizar_solicitacao()[/bold]")

@app.command()
def administrar_solicitacoes():
    """[Ação 7] Painel de monitoramento de status das demandas enviadas."""
    console.print("📋 Chamando: [bold]Gestor.administrar_solicitacoes()[/bold]")

@app.command()
def gerenciar_escola():
    """[Ação 8] Atualiza a capacidade física e dados estruturais da unidade."""
    console.print("🏫 Chamando: [bold]Gestor.gerenciar_escola()[/bold]")

@app.command()
def alterar_status_usuario():
    """[Ação 9] Ativa ou desativa contas de alunos e professores."""
    console.print("🔄 Chamando: [bold]Gestor.alterar_status_usuario()[/bold]")

# --- FIM DO MAPEAMENTO ---

if __name__ == "__main__":
    app()