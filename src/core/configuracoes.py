class Configuracoes:
    """Gerencia as configurações e limites do sistema usando os padrões Multiton e Fallback.

    Esta classe centraliza as regras de negócio (RN02, RN03, RN04), garantindo que
    cada município possua uma instância única na memória. Se um parâmetro não for
    customizado para um município específico, o sistema utiliza automaticamente 
    os valores padrões definidos no nível da classe (Fallback).

    Attributes:
        FREQUENCIA_MINIMA (float): Percentual mínimo de presença (RN02). Padrão: 0.75.
        INDICE_LACUNA_MINIMO (float): Limite inferior para detecção de lacunas (RN03). Padrão: 0.3.
        LIMITE_CUSTO_DEMANDA (float): Teto orçamentário para requisições (RN04). Padrão: 15000.0.
        _instancias (dict): Repositório privado que armazena as instâncias únicas por município.
    """
    
    _instancias = {}

    # --- Valores Padrão (Fallback) ---
    FREQUENCIA_MINIMA = 0.75
    INDICE_LACUNA_MINIMO = 0.3
    LIMITE_CUSTO_DEMANDA = 15000.0

    def __new__(cls, municipio="GLOBAL"):
        """Controla a criação de instâncias para garantir o padrão Multiton.

        Args:
            municipio (str): Nome do contexto municipal. Defaults to "GLOBAL".

        Returns:
            Configuracoes: A instância única associada ao município informado.
        """
        municipio = municipio.upper()
        if municipio not in cls._instancias:
            instancia = super().__new__(cls)
            instancia.municipio = municipio
            cls._instancias[municipio] = instancia
            instancia._carregar_do_backend()
        return cls._instancias[municipio]

    def _carregar_do_backend(self):
        """Simula a carga inicial de dados de uma fonte externa (Banco de Dados/JSON).
        
        Este método é disparado automaticamente apenas na criação da instância.
        Atualmente, serve como um ponto de integração para futuras consultas SQL.
        """
        print(f"Carregando as configurações para o município {self.municipio}")

    def atualizar_parametro(self, nome, valor):
        """Atualiza um parâmetro específico apenas para a instância atual.

        Cria uma 'sombra' (shadowing) sobre o atributo da classe, permitindo que
        este município tenha uma regra diferente da regra global.

        Args:
            nome (str): Nome do atributo a ser atualizado.
            valor (any): Novo valor, que deve ser compatível com o tipo original.

        Raises:
            ValueError: Se o parâmetro não existir ou for privado (iniciado com '_').
            TypeError: Se o tipo do novo valor for diferente do tipo do valor atual.
        """
        nome = nome.upper()
        if hasattr(self, nome) and not nome.startswith("_"):
            atual = getattr(self, nome)
            # Define tipos permitidos (ex: permite int em campos float)
            permitidos = (int, float) if isinstance(atual, float) else type(atual)
            
            if isinstance(valor, permitidos):
                setattr(self, nome, valor)
            else:
                raise TypeError(f"Valor para '{nome}' deve ser do tipo {permitidos}")
        else:
            raise ValueError(f"Parâmetro '{nome}' inválido ou inexistente.")

    def resetar_padroes(self):
        """Remove todas as customizações locais da instância.

        Limpa o dicionário interno (__dict__) do objeto. Após o reset, qualquer 
        consulta a atributos buscará os valores globais definidos na classe.
        """
        for k in list(self.__dict__.keys()):
            if not k.startswith("_") and k != "municipio":
                delattr(self, k)