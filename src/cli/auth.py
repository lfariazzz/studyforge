"""
Módulo de autenticação da CLI do StudyForge.
Responsável por login, logout e gerenciamento de sessão.
"""

from typing import Optional, Tuple
from src.database.RepositorioGeral import RepositorioGeral
from src.models.usuario import Usuario
from src.models.aluno import Aluno
from src.models.professor import Professor
from src.models.gestor import Gestor
from src.models.secretario import Secretario
from .utils import GerenciadorSessao, FormatadorCLI, ValidadorCLI


class SistemaAutenticacao:
    """Sistema responsável pela autenticação de usuários na CLI."""
    
    def __init__(self):
        """Inicializa o sistema de autenticação."""
        self.repositorio = RepositorioGeral()
        self.sessao = GerenciadorSessao.obter_instancia()
    
    def fazer_login(self, cpf: str, senha: str) -> Tuple[bool, str]:
        try:
            # Validações básicas (FormatadorCLI e ValidadorCLI mantidos)
            if not ValidadorCLI.validar_cpf(cpf):
                return False, FormatadorCLI.erro("CPF inválido. Use o formato XXX.XXX.XXX-XX")
            
            # Busca usuário no banco (O repositório do seu amigo já retorna o OBJETO pronto)
            usuario_obj = self.repositorio.buscar_usuario_por_cpf(cpf)
            
            if not usuario_obj:
                return False, FormatadorCLI.erro("Usuário não encontrado")
            
            # Verificação de senha usando o atributo do OBJETO (não dicionário)
            if usuario_obj.senha != senha:
                return False, FormatadorCLI.erro("CPF ou senha incorretos")
            
            # Verifica se o usuário está ativo (se o atributo existir na sua Model)
            if hasattr(usuario_obj, 'status') and not usuario_obj.status:
                return False, FormatadorCLI.erro("Usuário inativo")
            
            # Determina o tipo para a sessão baseado na classe do objeto
            tipo_usuario = usuario_obj.__class__.__name__.upper()
            
            # Define na sessão
            self.sessao.definir_usuario(usuario_obj, tipo_usuario)
            
            return True, FormatadorCLI.sucesso(f"Bem-vindo, {usuario_obj.nome} ({tipo_usuario})!")
            
        except Exception as e:
            return False, FormatadorCLI.erro(f"Erro durante login: {str(e)}")

    def obter_usuario_logado(self) -> Optional[Usuario]:
        """
        Método que o secretario_cli.py chama. 
        Apenas um alias para manter compatibilidade com seu código anterior.
        """
        return self.sessao.obter_usuario()
    
    def fazer_logout(self) -> str:
        """
        Realiza o logout do usuário atual.
        
        Returns:
            Mensagem de confirmação
        """
        if not self.sessao.esta_logado():
            return FormatadorCLI.aviso("Nenhum usuário logado")
        
        usuario = self.sessao.obter_usuario()
        nome = usuario.nome if usuario else "Usuário"
        
        self.sessao.limpar_sessao()
        
        return FormatadorCLI.sucesso(f"Até logo, {nome}!")
    
    def verificar_permissao(self, permissao_requerida: str) -> bool:
        """
        Verifica se o usuário logado tem uma permissão específica.
        
        Args:
            permissao_requerida: Permissão a verificar
        
        Returns:
            True se tem permissão, False caso contrário
        """
        if not self.sessao.esta_logado():
            return False
        
        usuario = self.sessao.obter_usuario()
        if not usuario:
            return False
        
        permissoes = usuario.get_permissao()
        return permissao_requerida in permissoes
    
    def obter_usuario_atual(self) -> Optional[Usuario]:
        """
        Retorna o usuário atualmente logado.
        
        Returns:
            Objeto do usuário ou None se não logado
        """
        return self.sessao.obter_usuario()
    
    def obter_tipo_usuario_atual(self) -> str:
        """
        Retorna o tipo do usuário atualmente logado.
        
        Returns:
            Tipo do usuário ou "DESCONECTADO"
        """
        return self.sessao.obter_tipo_usuario()
    
    def _criar_objeto_usuario(self, dados_usuario: dict) -> Optional[Usuario]:
        """Cria o objeto do usuário baseado nos dados do banco."""
        try:
            # Import local para evitar o erro circular que vimos antes
            from src.models.gestor import Gestor 
            
            tipo = dados_usuario['tipo'].upper()
            
            if tipo == 'ALUNO':
                return Aluno(
                    id_usuario=dados_usuario['id_usuario'],
                    nome=dados_usuario['nome'],
                    cpf=dados_usuario['cpf'],
                    email=dados_usuario['email'],
                    senha=dados_usuario['senha'],
                    telefone=dados_usuario['telefone'],
                    data_nascimento=dados_usuario['data_nascimento'],
                    turma_associada=dados_usuario.get('turma_associada'),
                    matricula=dados_usuario.get('matricula')
                )
            
            elif tipo == 'PROFESSOR':
                return Professor(
                    id_usuario=dados_usuario['id_usuario'],
                    nome=dados_usuario['nome'],
                    cpf=dados_usuario['cpf'],
                    email=dados_usuario['email'],
                    senha=dados_usuario['senha'],
                    telefone=dados_usuario['telefone'],
                    data_nascimento=dados_usuario['data_nascimento'],
                    registro_funcional=dados_usuario['registro_funcional'],
                    escola_associada=dados_usuario['escola_associada'],
                    titulacao=dados_usuario['titulacao'],
                    area_atuacao=dados_usuario['area_atuacao'],
                    salario=dados_usuario['salario']
                )
            
            elif tipo == 'GESTOR':
                return Gestor(
                    id_usuario=dados_usuario['id_usuario'],
                    nome=dados_usuario['nome'],
                    cpf=dados_usuario['cpf'],
                    email=dados_usuario['email'],
                    senha=dados_usuario['senha'],
                    telefone=dados_usuario['telefone'],
                    data_nascimento=dados_usuario['data_nascimento'],
                    escola_associada=dados_usuario['escola_associada']
                )
            
            elif tipo == 'SECRETÁRIO':
                return Secretario(
                    id_usuario=dados_usuario['id_usuario'],
                    nome=dados_usuario['nome'],
                    cpf=dados_usuario['cpf'],
                    email=dados_usuario['email'],
                    senha=dados_usuario['senha'],
                    telefone=dados_usuario['telefone'],
                    data_nascimento=dados_usuario['data_nascimento'],
                    municipio_responsavel=dados_usuario['municipio_responsavel'],
                    departamento=dados_usuario['departamento']
                )
            
            return None
                
        except Exception as e:
            print(f"Erro ao criar objeto usuário: {e}")
            return None


# Instância global do sistema de autenticação
auth_system = SistemaAutenticacao()