from src.models.usuario import Usuario
from datetime import date, datetime
from src.models.frequencia import Frequencia
from src.models.nota import Nota

"""
Representa a entidade Aluno conforme o diagrama UML.
Herda atributos base de Usuario e gerencia sua vida acadêmica.
"""

class Aluno(Usuario):
    def __init__(self, id_usuario, nome, cpf, email, senha, telefone, data_nascimento,
                turma_associada = None, matricula = None):
        """
        Inicializa um novo aluno no sistema StudyForge.
        
        Args:
            id_usuario (int): Identificador unico do aluno.
            nome (str): Nome completo do aluno.
            cpf (str): CPF do aluno (11 digitos numericos).
            email (str): Endereco de email do aluno.
            senha (str): Senha de acesso (minimo 8 caracteres).
            telefone (str): Numero de telefone (10 ou 11 digitos).
            data_nascimento (str): Data de nascimento no formato DD/MM/AAAA.
            turma_associada (Turma, optional): Objeto da turma ou ID da turma. Defaults to None.
            matricula (str, optional): Matricula do aluno. Se nao informada, e gerada automaticamente
                                      usando o ano atual e ID do usuario. Defaults to None.
        """
        super().__init__(id_usuario, nome, cpf, email, senha, telefone, data_nascimento, "ALUNO")

        self._turma_associada = turma_associada 

        if matricula:
            self._id_matricula = matricula
        else:
            ano = datetime.now().year
            self._id_matricula = f"{ano}{self._id_usuario}"

        self.notas = [] 
        self._presencas = []  

    # -----------------
    # GETTERS E SETTERS
    # -----------------

    @property
    def id_matricula(self):
        """Retorna a matrícula única do aluno."""
        return self._id_matricula
    
    @property
    def turma_associada(self):
        """Retorna o objeto ou identificador da turma do aluno."""
        return self._turma_associada
    
    @turma_associada.setter
    def turma_associada(self, valor):
        from src.models.turma import Turma
        if valor is not None and not isinstance(valor, (Turma, int, str)):
            raise TypeError("Erro: Turma deve ser um objeto Turma ou ID válido.")
        self._turma_associada = valor

    #implementado por Levi para integração com o src/services/avaliador_frequencia.py (RN02)    
    @property
    def presencas(self):
        return self._presencas


    #requer refatoração, ass:Levi 
    @property
    def frequencia(self):
        """
        Calcula a frequência real comparando as presenças com o 
        total de aulas ministradas (registradas nos diários da turma).
        """
        if not self.turma_associada or not hasattr(self.turma_associada, '_diario_de_classe'):
            return 100.0
        
        # O total de aulas vem do Diário da Turma
        total_aulas_ministradas = len(self.turma_associada._diario_de_classe)
        
        if total_aulas_ministradas == 0:
            return 100.0

        # Conta quantos objetos Frequencia têm status "PRESENTE"
        presencas_confirmadas = sum(1 for f in self._presencas if f.status == "PRESENTE")
        return round((presencas_confirmadas / total_aulas_ministradas) * 100, 2)
        
    # -------
    # MÉTODOS
    # -------

    def get_permissao(self):
        """
        Retorna as permissoes do aluno no sistema.
        
        Returns:
            list: Lista contendo as permissoes do aluno:
                  - VISUALIZAR_NOTAS: Acessar boletim escolar
                  - VER_FREQUENCIA: Consultar historico de frequencia
                  - VER_NOTICIAS: Acessar mural da escola
                  - VER_HORARIO: Consultar quadro de horarios
                  - BAIXAR_MATERIAL: Baixar materiais de aula
        """
        return ["VISUALIZAR_NOTAS", "VER_FREQUENCIA", "VER_NOTICIAS", "VER_HORARIO", "BAIXAR_MATERIAL"]
        
    
    def ver_frequencia(self):
        """
        Retorna o historico detalhado de frequencia do aluno.
        
        Exibe a frequencia percentual atual e lista todas as datas com status
        de presenca ou falta.
        
        Returns:
            str: Relatorio formatado com frequencia percentual e historico de presencas.
        """
        if not self.presencas:
            return "Nenhum registro de frequência encontrado."
            
        relatorio = [f"Frequência atual: {self.frequencia}%"]
        
        for freq in self.presencas:
            status = "✅ Presente" if freq.status == "PRESENTE" else "❌ Falta"
            relatorio.append(f"Aula ID {freq.id_diario}: {status}")

        return "\n".join(relatorio)
    

    def ver_horario(self):
        """
        Retorna o quadro de horarios e professores da turma associada.
        
        Consulta as informacoes da turma e exibe os professores regentes
        e dados de horario.
        
        Returns:
            str: String formatada contendo nome da turma e lista de professores regentes,
                 ou mensagem de erro se a turma nao estiver vinculada.
        """
        if not self.turma_associada or isinstance(self.turma_associada, str):
            return "Aluno sem turma vinculada. Horário indisponível."

        # Garante que o método existe antes de chamar
        if hasattr(self.turma_associada, 'obter_quadro_horario'):
            quadro = self.turma_associada.obter_quadro_horario()
            professores = ", ".join(quadro["Professores"]) if isinstance(quadro["Professores"], list) else quadro["Professores"]
            return (f"--- HORÁRIO DA TURMA: {quadro['Turma']} ---\n"
                f"Professores Regentes: {professores}")
    
        return "O recurso de horário não está disponível nesta turma."

    def exibir_perfil(self):
        """
        Exibe o perfil completo do aluno.
        
        Implementacao do metodo abstrato da classe Usuario que retorna uma string
        formatada com os dados principais do aluno, incluindo matricula, turma,
        status da conta e frequencia geral.
        
        Returns:
            str: String formatada contendo informacoes do perfil do aluno.
        """
        turma_attr = getattr(self, '_turma_associada', None)
        nome_turma = turma_attr.nome if hasattr(turma_attr, 'nome') else str(turma_attr or "Não vinculada")
        status_conta = "Ativa" if getattr(self, '_status', True) else "Inativa"
        
        return (
            f"Nome: {self.nome}\n"
            f"Matrícula: {getattr(self, '_id_matricula', 'N/A')}\n"
            f"Turma: {nome_turma}\n"
            f"E-mail: {self.email}\n"
            f"Status: {status_conta}\n"
            f"Frequência: {getattr(self, 'frequencia', 0)}%"
        )

    def visualizar_notas(self):
        """
        Exibe o boletim escolar do aluno com suas notas por disciplina.
        
        Retorna uma listagem formatada de todas as disciplinas com suas notas
        e media calculada por disciplina.
        
        Returns:
            str: Boletim formatado com notas e medias por disciplina,
                 ou mensagem indicando que nao ha notas lancadas.
        """
        if not self.notas:
            return "Nenhuma nota foi lançada no sistema até o momento."

        boletim = {}
        for n in self.notas:
            if n.disciplina not in boletim:
                boletim[n.disciplina] = []
            boletim[n.disciplina].append(n.valor)

        exibicao = [f"--- BOLETIM ESCOLAR: {self.nome} ---"]
        for disc, valores in boletim.items():
            media = sum(valores) / len(valores)
            exibicao.append(f"🔹 {disc}: {' | '.join(map(str, valores))} (Média: {media:.2f})")
        
        return "\n".join(exibicao)

    def adicionar_nota(self, nota: Nota):
        """
        Adiciona uma nota do aluno em uma disciplina especifica.
        
        Metodo auxiliar chamado pelo professor para inserir notas. Cada disciplina
        pode ter multiplas notas que serao usadas para calculo de media.
        
        Args:
            disciplina (str): Nome da disciplina.
            valor (float): Valor da nota (deve estar entre 0 e 10).
        
        Raises:
            ValueError: Se a nota nao estiver no intervalo de 0 a 10.
        """
        if not (0 <= nota.valor <= 10):
            raise ValueError("Erro: A nota deve ser um valor entre 0 e 10.")
        
        self.notas.append(nota)

    def ver_noticias(self):
        """
        Exibe o mural de noticias da escola do aluno.
        
        Retorna as noticias publicadas no mural oficial da escola a qual
        o aluno esta vinculado atraves de sua turma.
        
        Returns:
            str: Mural de noticias formatado com titulos, datas, autores e conteudo,
                 ou mensagem de erro se o aluno nao estiver vinculado a uma turma.
        """
        if not self.turma_associada or isinstance(self.turma_associada, str):
            return "Aluno sem turma vinculada. Não é possível acessar o mural."

        escola = getattr(self.turma_associada, 'escola', None)
        
        if not escola:
            return "Erro: Escola não encontrada para esta turma."

        mural = escola._mural_oficial

        if not mural:
            return f"O mural da escola {escola.nome} está vazio no momento."

        exibicao = [f"--- 📢 MURAL DE NOTÍCIAS: {escola.nome} ---"]

        for noticia in reversed(mural):
            exibicao.append(f"📌 {noticia['titulo']} ({noticia['data']})")
            exibicao.append(f"   Autor: {noticia.get('autor', 'Gestão')}")
            exibicao.append(f"   {noticia['conteudo']}")
            exibicao.append("-" * 30)

        return "\n".join(exibicao)

    #refatorado por Levi para implementação da RN02
    def registrar_presenca(self, presente: Frequencia):
        """
        Registra a presenca ou falta do aluno em uma aula.
        
        Alimenta o historico de frequencia do aluno com informacoes de data
        e status de presenca. Utilizado pela interface de diario de classe.
        
        Args:
            data (date): Data da aula.
            presente (bool): True se o aluno estava presente, False se faltou.
        
        Raises:
            TypeError: Se o parametro presente nao for um booleano.
        """
        if not isinstance(presente, Frequencia):
            raise TypeError("O status de presença deve ser da classe Frequencia.")
        
        self._presencas.append(presente)

    def baixar_material(self, nome_material):
        """
        Faz o download de material de aula postado na turma.
        
        Permite que o aluno acesse e baixe materiais de aula que foram
        postados pela turma a qual esta vinculado.
        
        Args:
            nome_material (str): Nome do material a ser baixado.
        
        Returns:
            str: Mensagem de sucesso com link para download, mensagem de erro
                 se o aluno nao estiver em turma ou material nao encontrado.
        """
        if not self.turma_associada:
            return "Você não está vinculado a nenhuma turma"
        
        for material in getattr(self.turma_associada, '_materiais_postados', []):
            if material ['nome'] == nome_material:
                return f"Download de '{nome_material}' realizado. Link: {material['link']}"
            
        return "Material não encontrado na sua turma"
    
    def to_dict_especifico(self):
        """
        Exporta os dados especificos do aluno em formato de dicionario.
        
        Retorna um dicionario contendo apenas os atributos especificos da classe Aluno
        (diferente do metodo herdado to_dict()).
        
        Returns:
            dict: Dicionario com id_usuario, matricula e id_turma do aluno.
        """
        id_turma = getattr(self._turma_associada, 'id_turma', self._turma_associada)
        
        return {
            "id_usuario": self.id_usuario,
            "id_matricula": self.id_matricula,
            "id_turma": id_turma
        }
    