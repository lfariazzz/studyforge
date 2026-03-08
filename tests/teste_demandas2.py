"""
Esse teste serve para integrar as classes Demanda por completo, incluido a Factory. 
"""

import sys
import os

# Adiciona a pasta raiz (StudyForge-POO) ao path do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock
from src.core.demanda_factory import DemandaFactory
from src.models.demanda_pedagogica import DemandaPedagogica

class TestDemandaPedagogica(unittest.TestCase):

    def setUp(self):
        """Configura os objetos básicos (Mocks) para os testes."""
        # Simula o Município com suas regras de negócio
        self.mock_municipio = MagicMock()
        self.mock_municipio.id_municipio = 101
        self.mock_municipio.lacuna_maxima_permitida = 0.3  # 30%
        self.mock_municipio.media_frequencia = 0.75       # 75%

        # Simula o Solicitante (Secretário ou Gestor)
        self.mock_solicitante = MagicMock()
        self.mock_solicitante.municipio_responsavel = self.mock_municipio

        # Simula a Turma com 5 alunos matriculados
        self.mock_turma = MagicMock()
        self.mock_turma.nome = "9º Ano B"
        self.mock_turma._alunos_matriculados = [1, 2, 3, 4, 5] 

    def test_criacao_demanda_por_notas_baixas(self):
        """
        RN04: Valida se a Factory cria corretamente uma demanda quando 
        recebe um relatório de alunos com notas baixas.
        """
        # Dados de entrada simulando o retorno do AvaliadorLacuna (2 alunos em risco)
        relatorio_fake = [
            {"nome": "Alice", "media": 5.5, "disciplina": "Matemática"},
            {"nome": "Bruno", "media": 4.2, "disciplina": "Matemática"}
        ]

        # Execução: Chamada da Factory
        demanda = DemandaFactory.criar_demanda(
            tipo_demanda="PEDAGOGICA",
            solicitante=self.mock_solicitante,
            descricao="Reforço Urgente - Matemática",
            prioridade="ALTA",
            turma=self.mock_turma,
            relatorio_alunos=relatorio_fake,
            disciplina_alvo="Matemática",
            professor="Prof. Ricardo"
        )

        # --- ASSERTS (Validações) ---
        
        # 1. Verifica se o objeto criado é do tipo correto
        self.assertIsInstance(demanda, DemandaPedagogica)

        # 2. Valida o cálculo do Índice de Lacuna (2 alunos em risco / 5 totais = 0.4 ou 40%)
        self.assertEqual(demanda.indice_lacuna, 0.4)

        # 3. Valida se a regra de reforço é ativada (40% > 30% permitido)
        self.assertTrue(demanda.validar_reforco())

        # 4. Valida se os dados da disciplina e professor foram preservados
        self.assertEqual(demanda.disciplina_alvo, "Matemática")
        
        # 5. Valida se o AuditMixin registrou a data no relatório ao processar
        demanda.processar_solicitacao(self.mock_solicitante)
        self.assertIn("DATA:", demanda.alerta_gerado)
        self.assertIn("Alice", demanda.alerta_gerado)

        print("\n✅ Teste Unitário: Cenário de Notas Baixas passou com sucesso!")

    def test_cenario_notas_boas_nao_deve_exigir_reforco(self):
            # 1. SETUP: Relatório VAZIO (pois o avaliador não achou ninguém abaixo de 7)
            relatorio_vazio = []
            
            # 2. AÇÃO: Factory cria a demanda pedagógica
            demanda_regular = DemandaFactory.criar_demanda(
                tipo_demanda="PEDAGOGICA",
                solicitante=self.mock_solicitante,
                descricao="Monitoramento de Rotina",
                turma=self.mock_turma,
                relatorio_alunos=relatorio_vazio,
                disciplina_alvo="História",
                professor="Prof. Helena"
            )

            # 3. VALIDAÇÕES
            # O índice de lacuna deve ser 0.0
            self.assertEqual(demanda_regular.indice_lacuna, 0.0)
            
            # O validar_reforco deve retornar FALSE (pois 0.0 não é maior que a meta do município)
            self.assertFalse(demanda_regular.validar_reforco())
            
            # Ao processar, o status deve ser "REGULAR"
            demanda_regular.processar_solicitacao(self.mock_solicitante)
            self.assertEqual(demanda_regular.status, "REGULAR")
            
            print("✅ Teste de Notas Boas: REGULARIDADE confirmada!")

if __name__ == '__main__':
    unittest.main()