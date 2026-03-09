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
        """
        Realiza o login do usuário.
        
        Args:
            cpf: CPF do usuário
            senha: Senha do usuário
        
        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        try:
            # Validações básicas
            if not ValidadorCLI.validar_cpf(cpf):
                return False, FormatadorCLI.erro("CPF inválido. Use o formato XXX.XXX.XXX-XX")
            
            if not senha or len(senha) < 8:
                return False, FormatadorCLI.erro("Senha deve ter pelo menos 8 caracteres")
            
            # Busca usuário no banco
            usuario_data = self.repositorio.buscar_usuario_por_cpf(cpf)
            
            if not usuario_data:
                return False, FormatadorCLI.erro("Usuário não encontrado")
            
            # Verifica se usuário está ativo
            if not usuario_data.get('status', True):
                return False, FormatadorCLI.erro("Usuário inativo. Contate o administrador")
            
            # Verifica senha (NOTA: Em produção, usar hash!)
            if usuario_data['senha'] != senha:
                return False, FormatadorCLI.erro("CPF ou senha incorretos")
            
            # Cria objeto do usuário baseado no tipo
            usuario_obj = self._criar_objeto_usuario(usuario_data)
            
            if not usuario_obj:
                return False, FormatadorCLI.erro("Erro ao carregar perfil do usuário")
            
            # Define na sessão
            tipo_usuario = usuario_data['tipo']
            self.sessao.definir_usuario(usuario_obj, tipo_usuario)
            
            # Mensagem de boas-vindas
            nome = usuario_obj.nome
            tipo_formatado = tipo_usuario.capitalize()
            mensagem = FormatadorCLI.sucesso(f"Bem-vindo, {nome} ({tipo_formatado})!")
            
            return True, mensagem
            
        except Exception as e:
            return False, FormatadorCLI.erro(f"Erro durante login: {str(e)}")
    
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
        """
        Cria o objeto do usuário baseado nos dados do banco.
        
        Args:
            dados_usuario: Dados do usuário do banco
        
        Returns:
            Objeto do usuário ou None se erro
        """
        try:
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
            
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao criar objeto usuário: {e}")
            return None


# Instância global do sistema de autenticação
auth_system = SistemaAutenticacao()