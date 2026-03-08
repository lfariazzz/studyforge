class Municipio:
    """Representa a gestão municipal responsável por um conjunto de escolas.
    Controla as verbas públicas e o cadastro de unidades de ensino."""

    def __init__(self, nome, id_municipio, estado, verba_disponivel_municipio, nota_de_corte):
        self._nome = nome
        self._id_municipio = id_municipio
        self.estado = estado
        self.verba_disponivel_municipio = verba_disponivel_municipio
        self.nota_de_corte = nota_de_corte
        
        self._escolas_situadas = []

    @property
    def nome(self):
        """Retorna o nome do município."""
        return self._nome

    @property
    def id_municipio(self):
        """Retorna o identificador único do município."""
        return self._id_municipio

    @property
    def estado(self):
        """Retorna a UF do estado."""
        return self._estado

    @estado.setter
    def estado(self, valor):
        """ Valida a UF: deve ser string, ter 2 caracteres e apenas letras.
        Converte automaticamente para maiúsculas. """
        if not isinstance(valor, str) or len(valor) != 2 or not valor.isalpha():
            raise ValueError("UF deve conter exatamente 2 letras.")
        self._estado = valor.upper()

    @property
    def verba_disponivel_municipio(self):
        """Retorna o saldo atual do município."""
        return self._verba_disponivel_municipio

    @verba_disponivel_municipio.setter
    def verba_disponivel_municipio(self, valor):
        """Garante que a verba seja um número decimal (float) e não negativa."""
        valor = float(valor)
        if valor < 0:
            raise ValueError("A verba disponível não pode ser negativa.")
        self._verba_disponivel_municipio = valor

    @property
    def escolas_situadas(self):
        """Retorna a lista de escolas cadastradas neste município."""
        return self._escolas_situadas

    def cadastrar_escola(self, escola): 
        """Adiciona uma nova escola à lista do município.
        Verifica se o objeto é realmente uma instância da classe Escola."""
        from .escola import Escola
        if not isinstance(escola, Escola):
            raise TypeError("O objeto deve ser do tipo Escola.")

        if escola not in self._escolas_situadas:
            self._escolas_situadas.append(escola)
            print(f"Escola '{escola.nome}' cadastrada no município {self._nome}.")
            return True
        return False

    def calcular_investimento_total(self):
        """Lógica Financeira: Soma a verba própria do município com a verba 
        específica de todas as escolas vinculadas a ele."""
        verba_escolas = sum(
            escola.verba_disponivel_escola
            for escola in self._escolas_situadas
        )
        return self._verba_disponivel_municipio + verba_escolas

    def to_dict(self):
        """Retorna os dados do município em formato dicionário."""
        return {
            "nome": self._nome,
            "id_municipio": self._id_municipio,
            "estado": self._estado,
            "verba_disponivel_municipio": self._verba_disponivel_municipio
        }

    def __str__(self):
        """Retorna uma representação amigável do objeto em formato de texto."""
        return f"Município: {self._nome} - {self._estado} (ID: {self._id_municipio})"