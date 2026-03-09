from src.models.usuario import Usuario
from datetime import date, datetime

"""
Representa a entidade Aluno conforme o diagrama UML.
Herda atributos base de Usuario e gerencia sua vida acadêmica.
"""

class Aluno(Usuario):
    def __init__(self, id_usuario, nome, cpf, email, senha, telefone, data_nascimento,
                turma_associada = None, matricula = None):
        super().__init__(id_usuario, nome, cpf, email, senha, telefone, data_nascimento, "ALUNO")

        self.turma_associada = turma_associada 

        if matricula:
            self._id_matricula = matricula
        else:
            ano = datetime.now().year
            self._id_matricula = f"{ano}{self._id_usuario}"

        self.notas = {}  # Dicionário público para notas por disciplina (para SQLite)
        self.presencas = []  # Lista pública para histórico de frequência (para SQLite)

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
        if hasattr(valor, 'id_turma'):
            self._turma_associada = valor
            if self not in valor.alunos_matriculados:
                valor.adicionar_aluno(self)
        elif isinstance(valor, str) or valor is None:
            self._turma_associada = valor
        else:
            raise ValueError("Erro: turma_associada deve ser um objeto Turma ou string.")

    #implementado por Levi para integração com o src/services/avaliador_frequencia.py (RN02)    
    @property
    def presenca(self):
        return self.presencas


    #requer refatoração, ass:Levi 
    @property
    def frequencia(self):
        """
        Calcula a frequência baseada no total de aulas da TURMA.
        """
        
        if not self.turma_associada or not hasattr(self.turma_associada, '_diario_de_classe'):
            return 100.0
        total_aulas_turma = len(self.turma_associada._diario_de_classe)
        
        if total_aulas_turma == 0:
            return 100.0

        presencas = sum(1 for registro in self.presencas if registro.get('presenca') is True)
        
        percentual = (presencas / total_aulas_turma) * 100
        return round(percentual, 2)
        
    # -------
    # MÉTODOS
    # -------

    def get_permissao(self):
        """Função que retorna as permissões da classe Aluno"""
        return ["VISUALIZAR_NOTAS", "VER_FREQUENCIA", "VER_NOTICIAS", "VER_HORARIO", "BAIXAR_MATERIAL"]
        
    
    def ver_frequencia(self):
        """Retorna o histórico detalhado de datas e presenças."""
        if not self.presencas:
            return "Nenhum registro de frequência encontrado."
        relatorio = [f"Frequência atual: {self.frequencia}%"]
        for reg in self.presencas:
            status = "Presente" if reg['presenca'] else "Faltou"
            relatorio.append(f"{reg['data']}: {status}")

        return "\n".join(relatorio)
    

    def ver_horario(self):
        """
        Consulta o quadro de horários/professores da turma associada.
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
        Implementação do método abstrato da classe Usuario.
        Retorna uma string formatada com os dados principais do aluno.
        """
        nome_turma = self.turma_associada.nome if hasattr(self.turma_associada, 'nome') else "Não vinculada"
        status_conta = "Ativa" if self._status else "Inativa/Suspensa"

        return (
            f"\n" + "="*40 + "\n"
            f"          PERFIL DO ALUNO\n"
            f"="*40 + "\n"
            f"Nome: {self.nome}\n"
            f"Matrícula: {self.id_matricula}\n"
            f"Turma: {nome_turma}\n"
            f"E-mail: {self.email}\n"
            f"Status: {status_conta}\n"
            f"Frequência Geral: {self.frequencia}%\n"
            f"="*40
        )

    def visualizar_notas(self):
        """
        Permite ao aluno visualizar suas notas organizadas por disciplina.
        """
        if not self.notas:
            return "Nenhuma nota foi lançada no sistema até o momento."

        exibicao = [f"--- BOLETIM ESCOLAR: {self.nome} ---"]
        
        for disciplina, lista_notas in self.notas.items():
            media = sum(lista_notas) / len(lista_notas) if lista_notas else 0
            notas_str = " | ".join(map(str, lista_notas))
            
            exibicao.append(f"🔹 {disciplina}: {notas_str} (Média: {media:.2f})")

        exibicao.append("-" * 40)
        return "\n".join(exibicao)

    def adicionar_nota(self, disciplina: str, valor: float):
        """
        Método auxiliar que será chamado pelo professor para inserir notas.
        """
        if not (0 <= valor <= 10):
            raise ValueError("Erro: A nota deve ser um valor entre 0 e 10.")
        
        if disciplina not in self.notas:
            self.notas[disciplina] = []

        self.notas[disciplina].append(valor)

    def ver_noticias(self):
        """
        Consulta o mural de notícias oficial da escola à qual o aluno pertence.
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
    def registrar_presenca(self, data: date, presente: bool):
        """Alimenta o histórico (Data e Booleano)."""
        if not isinstance(presente, bool):
            raise TypeError("O status de presença deve ser True ou False.")
        
        self.presencas.append({
            "data": data,
            "aluno": self.nome,
            "presenca": presente
        })

    def baixar_material(self, nome_material):
        if not self.turma_associada:
            return "Você não está vinculado a nenhuma turma"
        
        for material in getattr(self.turma_associada, '_materiais_postados', []):
            if material ['nome'] == nome_material:
                return f"Download de '{nome_material}' realizado. Link: {material['link']}"
            
        return "Material não encontrado na sua turma"
    
    def to_dict_especifico(self):
        """Exporta os dados do aluno em formato de dicionário."""
        return{
            "id_usuario": self._id_usuario,
            "matricula": self._id_matricula,
            "id_turma": self._turma_associada._id_turma if self._turma_associada else None
        }
    