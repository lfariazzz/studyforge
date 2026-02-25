import sys
import os
import re
from datetime import datetime

# Ajuste de path para encontrar o modelo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models.usuario import Usuario

class UsuarioTeste(Usuario):
    def get_permissao(self):
        return ["ACESSO_TOTAL"]
    
    def exibir_perfil(self):
        return f"Teste: {self.nome}"

def testar_tudo():
    print("="*50)
    print("INICIANDO BATERIA DE TESTES EXAUSTIVOS")
    print("="*50)

    # --- 1. TESTE DE INSTANCIAÇÃO E GETTERS BÁSICOS ---
    u = UsuarioTeste(
        nome="Fulano Detal", 
        cpf="123.456.789-01", 
        email="Teste@Email.com", 
        senha="Senha_Especial_123", 
        telefone="11988887777", 
        data_nascimento="01/01/2000"
    )
    
    print("\n[GETTERS - ESTADO INICIAL]")
    print(f"ID: {u.id} | Esperado: 1")
    print(f"Nome: {u.nome} | Esperado: Fulano Detal (Title Case)")
    print(f"CPF: {u.cpf} | Esperado: 12345678901 (Apenas números)")
    print(f"Email: {u.email} | Esperado: teste@email.com (Lower case)")
    print(f"Telefone: {u.telefone} | Esperado: (11) 98888-7777")
    print(f"Data: {u.data_nascimento} | Esperado: 01/01/2000")
    print(f"Status: {u.status} | Esperado: Ativo")
    print(f"Login: {u.login} | Esperado: Offline")

    # --- 2. TESTE DE SETTERS (VALIDAÇÕES DE ERRO) ---
    print("\n[SETTERS - TESTANDO RESTRIÇÕES]")
    
    # Nome Inválido (Números)
    try:
        u.nome = "Fulano 123"
    except ValueError as e:
        print(f"OK - Barrou nome com número: {e}")

    # CPF Inválido (Tamanho)
    try:
        u.cpf = "12345"
    except ValueError as e:
        print(f"OK - Barrou CPF curto: {e}")

    # Email Inválido (Regex)
    try:
        u.email = "email_errado.com"
    except ValueError as e:
        print(f"OK - Barrou email sem @: {e}")

    # Senha Inválida (Apenas letras)
    try:
        u.senha = "senhatodaabc"
    except ValueError as e:
        print(f"OK - Barrou senha sem números/especiais: {e}")

    # Telefone Inválido (Letras)
    try:
        u.telefone = "11-9999-AAAA"
    except ValueError:
        print("OK - Barrou telefone com letras (via re.sub)")

    # Data Inválida (Futuro)
    try:
        u.data_nascimento = "01/01/2099"
    except ValueError as e:
        print(f"OK - Barrou data no futuro: {e}")

    # --- 3. TESTE DE MÉTODOS DE NEGÓCIO ---
    print("\n[MÉTODOS - COMPORTAMENTO]")

    # Login com dados errados
    try:
        u.realizar_login("teste@email.com", "senha_errada")
    except ValueError as e:
        print(f"OK - Login negado (senha incorreta): {e}")

    # Login correto
    if u.realizar_login("teste@email.com", "Senha_Especial_123"):
        print(f"OK - Login realizado. Status atual: {u.login}")

    # Trocar senha
    try:
        u.trocar_senha("senha_errada", "NovaSenha123!")
    except ValueError as e:
        print(f"OK - Troca de senha negada (verificador errado): {e}")

    u.trocar_senha("Senha_Especial_123", "NovaSenha123!")
    print(f"OK - Senha alterada com sucesso. Nova senha no dict: {u.to_dict()['senha']}")

    # Encerrar Sessão
    u.encerrar_sessao()
    print(f"OK - Sessão encerrada. Status atual: {u.login}")

    # Teste de Conta Desativada
    u._status = False # Simulando suspensão administrativa
    try:
        u.realizar_login("teste@email.com", "NovaSenha123!")
    except PermissionError as e:
        print(f"OK - Bloqueou login de conta inativa: {e}")

    # --- 4. TESTE DE EXPORTAÇÃO (TO_DICT) ---
    print("\n[TO_DICT - VALIDAÇÃO FINAL]")
    dados = u.to_dict()
    # Verificando se todas as chaves esperadas existem
    chaves_esperadas = ["tipo", "id", "nome", "cpf", "email", "senha", "telefone", "data_nascimento", "status", "sessao"]
    todas_chaves = all(chave in dados for chave in chaves_esperadas)
    print(f"OK - Todas as chaves presentes no dict: {todas_chaves}")
    print(f"Dicionário final: {dados}")

    print("\n" + "="*50)
    print("BATERIA DE TESTES CONCLUÍDA")
    print("="*50)

if __name__ == "__main__":
    testar_tudo()