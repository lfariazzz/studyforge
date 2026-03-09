"""
Módulo de utilitários para a CLI do StudyForge.
Contém funções auxiliares para formatação, validação e manipulação de dados.

"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import re
import json 
import os 


class FormatadorCLI:
    """Classe responsável por formatar saídas da CLI de forma consistente."""
    
    @staticmethod
    def titulo(texto: str) -> str:
        """Formata um título com bordas."""
        return f"\n{'=' * 60}\n{texto.center(60)}\n{'=' * 60}\n"
    
    @staticmethod
    def subtitulo(texto: str) -> str:
        """Formata um subtítulo com linha inferior."""
        return f"\n{texto}\n{'-' * len(texto)}\n"
    
    @staticmethod
    def sucesso(mensagem: str) -> str:
        """Formata mensagem de sucesso em verde."""
        return f" {mensagem}"
    
    @staticmethod
    def erro(mensagem: str) -> str:
        """Formata mensagem de erro em vermelho."""
        return f" {mensagem}"
    
    @staticmethod
    def aviso(mensagem: str) -> str:
        """Formata mensagem de aviso em amarelo."""
        return f"{mensagem}"
    
    @staticmethod
    def info(mensagem: str) -> str:
        """Formata mensagem informativa em azul."""
        return f"{mensagem}"
    
    @staticmethod
    def tabela(dados: List[Dict[str, Any]], colunas: Optional[List[str]] = None) -> str:
        """
        Formata dados em formato de tabela.
        
        Args:
            dados: Lista de dicionários com os dados
            colunas: Lista de colunas a exibir (se None, usa todas)
        
        Returns:
            String formatada em tabela
        """
        if not dados:
            return "Nenhum registro encontrado."
        
        if colunas is None:
            colunas = list(dados[0].keys())
        
        # Calcula largura das colunas
        larguras = {col: len(col) for col in colunas}
        for linha in dados:
            for col in colunas:
                valor = str(linha.get(col, ""))
                larguras[col] = max(larguras[col], len(valor))
        
        # Cabeçalho
        linha_separadora = "+" + "+".join(["-" * (larguras[col] + 2) for col in colunas]) + "+"
        cabecalho = "| " + " | ".join([col.ljust(larguras[col]) for col in colunas]) + " |"
        
        # Montando tabela
        resultado = f"\n{linha_separadora}\n{cabecalho}\n{linha_separadora}\n"
        
        # Linhas de dados
        for linha in dados:
            valores = [str(linha.get(col, "")).ljust(larguras[col]) for col in colunas]
            resultado += "| " + " | ".join(valores) + " |\n"
        
        resultado += linha_separadora + "\n"
        return resultado


class ValidadorCLI:
    """Classe responsável por validações de entrada da CLI."""
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """
        Valida se um CPF está em formato correto.
        
        Args:
            cpf: String com CPF (ex: "123.456.789-00")
        
        Returns:
            True se válido, False caso contrário
        """
        cpf_limpo = re.sub(r'\D', '', cpf)
        
        if len(cpf_limpo) != 11:
            return False
        
        if cpf_limpo == cpf_limpo[0] * 11:
            return False
        
        return True
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """
        Valida se um email está em formato correto.
        
        Args:
            email: String com email
        
        Returns:
            True se válido, False caso contrário
        """
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    @staticmethod
    def validar_data(data: str, formato: str = "%d/%m/%Y") -> bool:
        """
        Valida se uma data está em formato correto.
        
        Args:
            data: String com data
            formato: Formato esperado da data (padrão: DD/MM/YYYY)
        
        Returns:
            True se válido, False caso contrário
        """
        try:
            datetime.strptime(data, formato)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_opcao(opcao: str, opcoes_validas: List[str]) -> bool:
        """
        Valida se uma opção está dentro das válidas.
        
        Args:
            opcao: Opção escolhida
            opcoes_validas: Lista de opções válidas
        
        Returns:
            True se válido, False caso contrário
        """
        return opcao.upper() in [opt.upper() for opt in opcoes_validas]


class GerenciadorSessao:
    _instancia = None

    def __init__(self):
        self.caminho_sessao = "data/sessao.json"
        self._usuario_memoria = None
        self._tipo_memoria = None

    @classmethod
    def obter_instancia(cls):
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def definir_usuario(self, usuario, tipo):
        """Salva a sessão tanto em memória quanto em arquivo."""
        self._usuario_memoria = usuario
        self._tipo_memoria = tipo
        
        # Cria a pasta data se não existir
        os.makedirs(os.path.dirname(self.caminho_sessao), exist_ok=True)
        
        # Salva apenas o CPF para podermos 'reidratar' depois
        with open(self.caminho_sessao, "w") as f:
            json.dump({"cpf": usuario.cpf, "tipo": tipo}, f)

    def obter_usuario(self):
        """Busca o usuário. Se a memória estiver vazia (novo comando), tenta ler do arquivo."""
        if self._usuario_memoria:
            return self._usuario_memoria
        
        # Tenta reidratar a partir do arquivo
        if os.path.exists(self.caminho_sessao):
            with open(self.caminho_sessao, "r") as f:
                dados = json.load(f)
                from src.database.RepositorioGeral import RepositorioGeral
                repo = RepositorioGeral()
                usuario_data = repo.buscar_usuario_por_cpf(dados['cpf'])
                
                # Usa a mesma lógica que você já tem no auth_system para criar o objeto
                # Para evitar import circular, você pode buscar o auth_system aqui
                from src.cli.auth import auth_system 
                self._usuario_memoria = auth_system._criar_objeto_usuario(usuario_data)
                return self._usuario_memoria
        return None

    def limpar_sessao(self):
        self._usuario_memoria = None
        if os.path.exists(self.caminho_sessao):
            os.remove(self.caminho_sessao)