from abc import ABC, abstractmethod
import re
from datetime import datetime

"""
Representa a entid_usuarioade base para todos os usuários do sistema StudyForge. 
Esta é uma classe abstrata (ABC) que define os atributos e métodos comuns 
a todos os perfis (Professor, Aluno, Gestor e Secretario). Não deve ser 
instanciada diretamente.
"""
class Usuario(ABC):
    def __init__(self, id_usuario, nome, cpf, email, senha, telefone, data_nascimento, tipo, login=False, status=True):
        self._id_usuario = id_usuario
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.data_nascimento = data_nascimento
        self._tipo = tipo 
        self._login = login
        self._status = status


    #-----------------
    #GETTERS E SETTERS
    #-----------------

    @property
    def id_usuario(self):
        """Permite ler o id_usuario, mas sem altera-lo diretamente"""
        return self._id_usuario
    @property
    def nome(self):
        return self._nome
    
    @nome.setter
    def nome(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: Nome deve ser uma string!")
        padrao_nome = r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$'

        if not re.match(padrao_nome, valor):
            raise ValueError("Erro: Nome inválid_usuarioo! Use apenas letras.")
        else:
            self._nome = valor.strip().title()
            
    @property
    def cpf(self):
        return self._cpf
    
    @cpf.setter
    def cpf(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: O CPF deve ser uma string!")
        
        cpf_limpo = re.sub(r'\D', '', valor)

        if len(cpf_limpo) != 11:
            raise ValueError("Erro: O CPF deve conter exatamente 11 dígitos numéricos!")
        self._cpf = cpf_limpo

    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: O email deve ser uma string!")

        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(padrao, valor):
            raise ValueError("Erro: Formato de email inválid_usuarioo!")
        
        else:
            self._email = valor.lower().strip()

    @property
    def senha(self):
        return self._senha
    
    @senha.setter   
    def senha(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: A senha deve ser uma string!")
        
        senha_limpa = valor.strip()

        if len(senha_limpa) < 8:
            raise ValueError("Erro: A senha deve ter no mínimo 8 caracteres!")
        if senha_limpa.isalpha():
            raise ValueError("Erro: A senha deve conter pelo menos um número ou caractere especial!")
        else:
            self._senha = senha_limpa

    @property
    def telefone(self):
        t = self._telefone
        if len(t) == 11:
            return f"({t[:2]}) {t[2:7]}-{t[7:]}"
        return f"({t[:2]}) {t[2:6]}-{t[6:]}"
    
    @telefone.setter
    def telefone(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: O telefone deve ser uma string!")
        tel_limpo = re.sub(r'\D', '', valor)
        if len(tel_limpo) not in [10, 11]:
            raise ValueError("Erro: O telefone deve conter 10 ou 11 dígitos!")
        self._telefone = tel_limpo
    
    @property
    def data_nascimento(self):
        return self._data_nascimento.strftime("%d/%m/%Y")
    
    @data_nascimento.setter
    def data_nascimento(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: A data deve ser uma string no formato DD/MM/AAAA!")
        try:
            data_convertid_usuarioa = datetime.strptime(valor, "%d/%m/%Y")
            if data_convertid_usuarioa > datetime.now():
                raise ValueError("Erro: Data de nascimento inválid_usuarioa!")
            self._data_nascimento = data_convertid_usuarioa
        
        except ValueError:
            raise ValueError("Erro: Data inválid_usuarioa! Use o formato DD/MM/AAAA (ex: 02/08/2003).") 
        
    @property
    def status(self):
        return "Ativo" if self._status else "Inativo (Conta Suspensa/Desativada)"
    
    @status.setter
    def status(self, valor):
        if not isinstance(valor, bool):
            raise TypeError("Erro: O status deve ser um valor booleano (True ou False)!")
        self._status = valor
    
    @property
    def login(self):
        return "Online" if self._login == True else "Offline"

    #-------
    #MÉTODOS
    #-------

    @abstractmethod
    def get_permissao(self):
        """Método abstrato: cada subclasse retornará 
        sua propria lista de permissões.
        """
        pass

    @abstractmethod
    def exibir_perfil(self):
        """Método abstrato: cada subclasse retornará
        suas próprias informações de usuario
        """
        pass

    def realizar_login(self, email_tentativa, senha_tentativa):
        """Lógica para realizar o login do Usuário"""
        if not self._status:
            raise PermissionError("Erro: Esta conta está desativada, por favor entrar em contato com a secretaria.")
        if senha_tentativa != self._senha or email_tentativa != self._email:
            raise  ValueError("Erro: Email ou senha inválid_usuarioos.")
        
        self._login = True
        return True

    def encerrar_sessao(self):
        """Lógica para deslogar do Sistema"""
        if not self._login:
            return False
        
        self._login = False
        return True
        
    def trocar_senha(self, verificador, nova_senha):
        """Lógica para alterar a senha"""
        if verificador != self._senha:
            raise ValueError("Erro: Senha anterior inválid_usuarioa.")
        
        self.senha = nova_senha

    def to_dict(self):
        return {
            "id_usuario": self._id_usuario, 
            "cpf": self._cpf,
            "nome": self._nome,
            "email": self._email,
            "senha": self._senha,
            "telefone": self._telefone,
            "data_nascimento": self._data_nascimento,
            "login": int(self._login),        
            "status": int(self._status),
            "tipo": self.__class__.__name__.upper(),
        }