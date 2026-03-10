import sys
import os

# Ajuste de path para localizar o diretório 'src'
raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
pasta_src = os.path.join(raiz, 'src')
if pasta_src not in sys.path:
    sys.path.insert(0, pasta_src)

from models.municipio import Municipio
from unittest.mock import MagicMock

def executar_teste_visual_municipio():
    print("="*50)
    print("INICIANDO BATERIA DE TESTES: CLASSE MUNICIPIO")
    print("="*50)

    # 1. Instanciação e Getters
    try:
        mun = Municipio(nome="EducaCity", id_municipio=1, estado="sp", verba_disponivel_municipio=100000.0)
        
        print("\n[GETTERS - ESTADO INICIAL]")
        print(f"ID: {mun.id_municipio} | Esperado: 1")
        print(f"Nome: {mun.nome} | Esperado: EducaCity")
        print(f"Estado: {mun.estado} | Esperado: SP (Auto-uppercase)")
        print(f"Verba: R$ {mun.verba_disponivel_municipio} | Esperado: 100000.0")
        print(f"Escolas: {len(mun.escolas_situadas)} | Esperado: 0")

        # 2. Setters e Restrições
        print("\n[SETTERS - TESTANDO RESTRIÇÕES]")
        
        # Teste Estado
        try:
            mun.estado = "SPA"
        except ValueError as e:
            print(f"OK - Barrou UF longa: {e}")
            
        try:
            mun.estado = "12"
        except ValueError as e:
            print(f"OK - Barrou UF com números: {e}")

        # Teste Verba
        try:
            mun.verba_disponivel_municipio = -500.0
        except ValueError as e:
            print(f"OK - Barrou verba negativa: {e}")

        # 3. Métodos e Comportamento
        print("\n[MÉTODOS - COMPORTAMENTO]")
        
        # Cadastro de Escola
        mock_esc = MagicMock()
        from models.escola import Escola
        mock_esc.__class__ = Escola
        mock_esc.nome = "Escola Padrão"
        mock_esc.verba_disponivel_escola = 25000.0
        
        if mun.cadastrar_escola(mock_esc):
            print(f"OK - Escola cadastrada. Total na lista: {len(mun.escolas_situadas)}")
        
        if not mun.cadastrar_escola(mock_esc):
            print("OK - Barrou cadastro duplicado da mesma escola.")

        # Cálculo Financeiro
        investimento = mun.calcular_investimento_total()
        print(f"OK - Investimento Total: R$ {investimento} | (Mun 100k + Esc 25k)")

        # 4. To_Dict e Validação Final
        print("\n[TO_DICT - VALIDAÇÃO FINAL]")
        dicionario = mun.to_dict()
        chaves_ok = all(k in dicionario for k in ["nome", "id_municipio", "estado", "verba_disponivel_municipio"])
        print(f"OK - Todas as chaves presentes no dict: {chaves_ok}")
        print(f"Dicionário final: {dicionario}")
        
        print("\n" + "="*50)
        print("TESTES FINALIZADOS COM SUCESSO")
        print("="*50)

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO DURANTE OS TESTES: {e}")

if __name__ == "__main__":
    executar_teste_visual_municipio()