from src.models.demanda import Demanda
from src.core.configuracoes import Configuracoes

class DemandaInfraestrutura(Demanda):
    """
    Essa classe tem a função de ordenar as demandas de estruturas, passando por um 
    processo de solicitação que validam as informações, nível de importância e coleta os 
    dados dos envolvidos. 
    """
    def __init__(self, id_demanda, descricao, prioridade, solicitante, custo_estimado, escola, municipio_responsavel):

        super().__init__(id_demanda, descricao, prioridade, solicitante, municipio_responsavel, "INFRAESTRUTURA")
        self._custo_estimado = custo_estimado
        self._escola = escola
        self.config = Configuracoes


    def validar_usuario(self, usuario):
        """
        Valida se o usuário possui permissão de acesso à demanda baseada em seu perfil e município.

        Verifica se o usuário é um Gestor ou Secretário e se o município vinculado 
        ao seu perfil coincide com o município da demanda (jurisdição).

        Args:
            usuario: Objeto do usuário que está tentando realizar a ação.

        Returns:
            bool: True se o usuário for válido e pertencer ao mesmo município.

        Raises:
            PermissionError: Se o perfil for inválido ou se o município não coincidir.
        """
        #Aqui são duas variáveis que vão verificar se existem esses determinados atributos no usuario.
        gestor = hasattr(usuario, 'escola_associada')
        secretario = hasattr(usuario, 'municipio_responsavel')

        #Se não for secretário ou gestor, erro.
        if not (gestor or secretario):
            raise PermissionError("Acesso negado: Perfil de usuário inválido")

        #Esse atributo serve para pegar qual é o municipio responsável. 
        municipio_obj = getattr(usuario, 'municipio_responsavel', None)
        
        #Nesse caso, se o objeto não tem valor None, entao obrigatoriamente ele cai como um secretário
        if municipio_obj is not None: 
            id_municipio_usuario = municipio_obj.id_municipio 
        #Caso o valor do municipio_obj seja nulo, então obrigatoriamente é um gestor.
        else: 
            id_municipio_usuario = usuario.escola_associada.municipio.id_municipio

        #Se o id do munícipio não bater com o id do munícipio do usuário, da erro. Basicamente, vai dar erro
        # se um gestor ou secretário de Juazeiro tentar mexer em alguma coisa do Crato, por exemplo.
        if self.id_municipio != id_municipio_usuario:
            raise PermissionError("Acesso negado: O usuário não pertence a esse município")
        

        return True 


    def solicitar_demanda(self, usuario):
        """
        Inicia o processo de solicitação de uma demanda de infraestrutura.

        Valida o usuário, verifica se o custo estimado está dentro dos limites 
        configurados e altera o status da demanda para 'PENDENTE'.

        Args:
            usuario: Objeto do usuário (Gestor ou Secretário) que solicita a demanda.

        Returns:
            bool: True se a solicitação for processada com sucesso.

        Raises:
            ValueError: Se o custo estimado ultrapassar o limite permitido.
            PermissionError: Se o usuário não tiver permissão para este município.
        """


        ### Instancia o soliciante como objeto, faz a verificação para
        ### conferir se é gestor ou secretário e na variável municipio
        ### fica guardado o municipio de fato. 

        solicitante_obj = self._solicitante 

        if hasattr(solicitante_obj, 'municipio_responsavel'):
            municipio = solicitante_obj.municipio_responsavel 
        else:
            municipio = solicitante_obj.escola_associada.municipio 

        if self._custo_estimado > municipio.verba_disponivel_municipio:                
            raise ValueError("Custo excede o limite do município.")


        #Chama a função de validar o usuário
        self.validar_usuario(usuario)

        #Salva quem solicitou a demanda e em que horas solicitou essa demanda. 
        self.atualizar(usuario)

        self._status = "PENDENTE"
    
        return True 
    

    def processar_solicitacao(self, usuario): 
        """
        Realiza a aprovação oficial de uma demanda pendente.

        Este método restringe a aprovação exclusivamente a usuários com perfil de 
        Secretário de Educação vinculados ao mesmo município da demanda.

        Args:
            usuario: Objeto do usuário que está tentando aprovar.

        Returns:
            bool: True se a demanda for aprovada com sucesso.

        Raises:
            PermissionError: Se o usuário for um Gestor ou pertencer a outro município.
        """
        #Valida se é um usuário que pode acessar esse método (Gestor ou Secretário)
        self.validar_usuario(usuario)
        
        #Valida se realmente é um secretário 
        if not hasattr(usuario, 'municipio_responsavel'):
            raise PermissionError("Somente um Secretário de Educação pode aprovar uma demanda")
        
        self.atualizar_status("APROVADO")
