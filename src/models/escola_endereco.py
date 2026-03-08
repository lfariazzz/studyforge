class Endereco:
    """
    Classe que representa a localização física de uma unidade escolar.
    Sincronizada com a tabela 'escola_endereco'.
    """
    def __init__(self, id_escola, id_localizacao, cep, rua, numero, bairro):
        self._id_escola = id_escola
        self._id_localizacao = id_localizacao
        self.cep = cep
        self.rua = rua
        self.numero = numero
        self.bairro = bairro

    def __str__(self):
        """Retorna o endereço formatado para exibição rápida."""
        return f"{self.rua}, {self.numero} - {self.bairro} | CEP: {self.cep}"