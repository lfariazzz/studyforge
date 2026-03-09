"""
Testes para a classe Usuario usando unittest.
Para executar: python -m unittest tests.teste_usuario -v
"""
import sys
import os
import unittest
from datetime import datetime

# Ajuste de path para encontrar o modelo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.usuario import Usuario

class UsuarioTeste(Usuario):
    def get_permissao(self):
        return ["ACESSO_TOTAL"]
    
    def exibir_perfil(self):
        return f"Teste: {self.nome}"

class TestUsuario(unittest.TestCase):
    def setUp(self):
        """Configura um usuário de teste antes de cada teste."""
        self.u = UsuarioTeste(
            id_usuario=1,
            nome="Fulano Detal",
            cpf="123.456.789-01",
            email="Teste@Email.com",
            senha="Senha_Especial_123",
            telefone="11988887777",
            data_nascimento="01/01/2000",
            tipo="TESTE"
        )

    def test_instantiation_and_getters(self):
        """Testa instanciação e getters básicos."""
        self.assertEqual(self.u.id_usuario, 1)
        self.assertEqual(self.u.nome, "Fulano Detal")
        self.assertEqual(self.u.cpf, "12345678901")
        self.assertEqual(self.u.email, "teste@email.com")
        self.assertEqual(self.u.telefone, "(11) 98888-7777")
        self.assertEqual(self.u.data_nascimento, "01/01/2000")
        self.assertEqual(self.u.status, "Ativo")
        self.assertEqual(self.u.login, "Offline")

    def test_setters_invalid(self):
        """Testa validações de erro nos setters."""
        # Nome com números
        with self.assertRaises(ValueError):
            self.u.nome = "Fulano 123"

        # CPF curto
        with self.assertRaises(ValueError):
            self.u.cpf = "12345"

        # Email inválido
        with self.assertRaises(ValueError):
            self.u.email = "email_errado.com"

        # Senha apenas letras
        with self.assertRaises(ValueError):
            self.u.senha = "senhatodaabc"

        # Telefone com letras (deve falhar na limpeza)
        with self.assertRaises(ValueError):
            self.u.telefone = "11-9999-AAAA"

        # Data no futuro
        with self.assertRaises(ValueError):
            self.u.data_nascimento = "01/01/2099"

    def test_setters_valid(self):
        """Testa setters com valores válidos."""
        self.u.nome = "Novo Nome"
        self.assertEqual(self.u.nome, "Novo Nome")

        self.u.email = "novo@email.com"
        self.assertEqual(self.u.email, "novo@email.com")

        self.u.senha = "NovaSenha123!"
        self.assertEqual(self.u.senha, "NovaSenha123!")

        self.u.telefone = "11987654321"
        self.assertEqual(self.u.telefone, "(11) 98765-4321")

        self.u.data_nascimento = "02/02/1990"
        self.assertEqual(self.u.data_nascimento, "02/02/1990")

    def test_login_methods(self):
        """Testa métodos de login e sessão."""
        # Login com credenciais erradas
        with self.assertRaises(ValueError):
            self.u.realizar_login("teste@email.com", "senha_errada")

        # Login correto
        result = self.u.realizar_login("teste@email.com", "Senha_Especial_123")
        self.assertTrue(result)
        self.assertEqual(self.u.login, "Online")

        # Encerrar sessão
        result = self.u.encerrar_sessao()
        self.assertTrue(result)
        self.assertEqual(self.u.login, "Offline")

        # Encerrar sessão já encerrada
        result = self.u.encerrar_sessao()
        self.assertFalse(result)

    def test_trocar_senha(self):
        """Testa troca de senha."""
        # Verificador errado
        with self.assertRaises(ValueError):
            self.u.trocar_senha("senha_errada", "NovaSenha123!")

        # Troca correta
        self.u.trocar_senha("Senha_Especial_123", "NovaSenha123!")
        self.assertEqual(self.u.senha, "NovaSenha123!")

    def test_conta_desativada(self):
        """Testa login com conta desativada."""
        self.u._status = False
        with self.assertRaises(PermissionError):
            self.u.realizar_login("teste@email.com", "Senha_Especial_123")

    def test_to_dict(self):
        """Testa exportação para dicionário."""
        dados = self.u.to_dict()
        chaves_esperadas = ["id_usuario", "nome", "cpf", "email", "senha", "telefone", "data_nascimento", "login", "status", "tipo"]
        for chave in chaves_esperadas:
            self.assertIn(chave, dados)
        self.assertEqual(dados["id_usuario"], 1)
        self.assertEqual(dados["tipo"], "USUARIOTESTE")  # Nome da classe

if __name__ == "__main__":
    unittest.main()