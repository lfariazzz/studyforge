"""Classe responsável pela definição de limites e configurações padrões do sistema cumprindo as regras de negócio e 
fazendo uso do Pattern Singleton, mantendo a padronização das instâncias e da consistência global em todo o sistema
        Atributos:
        FREQUENCIA_MINIMA (float): Percentual mínimo de presença (RN02).
        INDICE_LACUNA_MINIMO (float): Limite inferior para detecção de lacunas (RN03).
        LIMITE_CUSTO_DEMANDA (float): Teto orçamentário para requisições (RN04)."""
class Configuracoes:
    _instancia = None
    FREQUENCIA_MINIMA = 0.75
    INDICE_LACUNA_MINIMO = 0.3
    LIMITE_CUSTO_DEMANDA = 15000.0

    def __new__(cls):
        """Método especial para criação da instância ou padronização de já criadas"""
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia


    def atualizar_parametro(self, nome, valor):
        """Altera dinamicamente um parâmetro de configuração do sistema.

        O método normaliza o nome do parâmetro para maiúsculas e valida se o novo 
        valor é compatível com o tipo de dado do valor atual para evitar 
        inconsistências em cálculos das regras de negócio.

        Args:
            nome (str): O nome da configuração (ex: 'frequencia_minima').
            valor (int|float): O novo valor a ser atribuído ao parâmetro.

        Raises:
            ValueError: Se o parâmetro informado não existir ou for privado.
            TypeError: Se o tipo do valor fornecido for incompatível com o atual.
        """
        nome = nome.upper()
        if hasattr(self, nome) and not nome.startswith("_"):
            atual = getattr(self, nome)
            permitidos = (int, float) if isinstance(atual, float) else type(atual)
            if isinstance(valor, permitidos):
                setattr(self, nome, valor)
            else:
                raise TypeError("Valor fornecido inválido")
        else:
            raise ValueError("Parâmetro fornecido inválido")

    def resetar_padroes(self):
        """Restaura todas as configurações para os valores originais da classe.

        Este método remove as customizações feitas no nível da instância (armazenadas 
        em __dict__), fazendo com que o sistema volte a utilizar os valores 
        estáticos definidos originalmente na estrutura da classe.

        Note:
            Atributos internos ou privados (que começam com '_') não são afetados.
        """
        for k in list(self.__dict__.keys()):
            if not k.startswith("_"):
                delattr(self, k)