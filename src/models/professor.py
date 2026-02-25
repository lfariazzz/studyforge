from src.models.usuario import Usuario
from datetime import date
import re

"""
Representa a entidade Professor conforme o diagrama UML.
Herda atributos base de Usuario e adiciona dados funcionais e acadêmicos.
"""
class Professor(Usuario):
    def __init__(self, nome, cpf, email, senha, telefone, data_nascimento,
                 registro_funcional, escola_associada, titulacao, area_atuacao, 
                 salario, status=True):
        super().__init__(nome, cpf, email, senha, telefone, data_nascimento, status)
        self.registro_funcional = registro_funcional
        self.escola_associada = escola_associada
        self.titulacao = titulacao
        self.area_atuacao = area_atuacao
        self.salario = salario
        self.turmas_associadas = []

    #-----------------
    #GETTERS E SETTERS
    #-----------------

    @property
    def registro_funcional(self):
        """Retorna o registro funcional (RF) do professor."""
        return self._registro_funcional
    
    @registro_funcional.setter
    def registro_funcional(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: Registro Funcional deve ser uma string!")
        
        valor = valor.strip().upper()

        padrao_rf = r'^RF-\d{4}-\d{4}$'

        if not re.match(padrao_rf, valor):
            raise ValueError("Erro: RF inválido! Use o padrão RF-ANO-SEQUENCIAL (Ex: RF-2026-0001).")
        
        self._registro_funcional = valor

    @property
    def escola_associada(self):
        """Retorna o nome da escola onde o professor leciona."""
        return self._escola_associada
    
    @escola_associada.setter
    def escola_associada(self, valor):
        if hasattr(valor, 'id_escola'):
            self._escola_associada = valor
        elif isinstance(valor, str):
            self._escola_associada = valor
        else:
            raise TypeError("Erro: escola_associada deve ser um objeto da classe Escola.")
        
    @property
    def titulacao(self):
        """Retorna o grau acadêmico do professor."""
        return self._titulacao
    
    @titulacao.setter
    def titulacao(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: A titulação deve ser uma string!")
        
        tit_formatado = valor.strip().title()

        titulacoes_validas = ["Graduado", "Especialista", "Mestre", "Doutor", "Pós-Doutor"]

        if tit_formatado not in titulacoes_validas:
            raise ValueError(f"Erro: Titulação inválida! Escolha entre: {', '.join(titulacoes_validas)}")
        
        else:
            self._titulacao = tit_formatado

    @property
    def area_atuacao(self):
        """Retorna a área de especialidade/lecionada pelo professor."""
        return self._area_atuacao
    
    @area_atuacao.setter
    def area_atuacao(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: A área de atuação deve ser uma string!")
        area_limpa = valor.strip().title()

        if len(area_limpa) < 3:
            raise ValueError("Erro: A área de atuação deve ter no mínimo 3 caracteres!")
        
        else: 
            self._area_atuacao = area_limpa

    @property
    def salario(self):
        """Retorna o salário do professor."""
        return self._salario
    
    @salario.setter
    def salario(self, valor):
        if not isinstance(valor, (int,float)):
            raise TypeError("Erro: O salario deve ser um valor numérico!")
        if valor < 0:
            raise ValueError("Erro: Salario não pode ser negativo!")
        
        salario_minimo = 1621.00
        if valor < salario_minimo:
            print(f"⚠️ Aviso: O salário informado (R$ {valor:.2f}) está abaixo do minimo nacional.")
        self._salario = float(valor)

    #-------
    #MÉTODOS
    #-------

    def get_permissao(self):
        """Retorna as permissões específicas do professor no sistema."""
        return "Professor: Acesso a diários de classe, frequências e materiais didáticos."
    
    #Refatorado para atender ao RN02 
    def realizar_chamada(self, turma, data: date, lista_presencas: list[dict]):
        """
        RN02: Registra a presença dos alunos com verificação de permissão.
        """
        if turma not in self.turmas_associadas:
            print(f"❌ Erro de Permissão: O professor {self.nome} não pode realizar chamada na turma {getattr(turma, 'nome', 'desconhecida')} (não vinculada).")
            return
 
        if not hasattr(turma, 'alunos_matriculados'):
            print("❌ Erro: Objeto turma inválido ou sem lista de alunos.")
            return

        if not lista_presencas:
            print("⚠️ Aviso: Nenhuma presença enviada para registro.")
            return

        for registro in lista_presencas:
            aluno = registro.get("aluno")
            status = registro.get("presente")
            
            if aluno and hasattr(aluno, 'registrar_presenca'):
                aluno.registrar_presenca(data, status)
        
        turma.registrar_aula(self, data, f"Chamada realizada pelo Prof. {self.nome}")
        print(f"✅ Chamada concluída para a Turma {turma.nome} na data {data}.")

    def postar_conteudo(self, turma, data: str, conteudo: str):
        """
        Associa o conteúdo lecionado ao diário de classe da turma.
        """
        if hasattr(turma, 'registrar_aula'):
            sucesso = turma.registrar_aula(data, conteudo)
            if sucesso:
                print(f"📖 Conteúdo postado com sucesso na turma {getattr(turma, 'nome', 'desconhecida')}.")
        else:
            print("Erro: Não foi possível acessar o diário desta turma.")

    def lancar_nota(self, aluno, disciplina: str, nota: float):
    # Verificação automática de permissão (RN01)
        if aluno.turma_associada not in self.turmas_associadas:
            print(f"❌ Erro de Permissão: O professor {self.nome} não leciona para a turma {aluno.turma_associada.nome if hasattr(aluno.turma_associada, 'nome') else 'desconhecida'}.")
            return

        if not isinstance(nota, (int, float)) or not (0 <= nota <= 10):
            print("❌ Erro: A nota deve ser entre 0 e 10.")
            return

        if hasattr(aluno, '_notas'):
            aluno._notas[disciplina] = nota
            print(f"⭐ Nota {nota} lançada para {aluno.nome} em {disciplina}.")

    def enviar_material(self, turma, titulo: str, link_ou_conteudo: str):
        """
        Disponibiliza material de estudo para a turma.
        """
        if hasattr(turma, 'adicionar_material'):
            material = {
                "professor": self.nome,
                "titulo": titulo,
                "conteudo": link_ou_conteudo
            }
            turma.adicionar_material(material)
            print(f"📚 Material '{titulo}' enviado para a turma {getattr(turma, 'nome', 'desconhecida')}.")
        else:
            print("❌ Erro: A turma não possui repositório de materiais.")

    def to_dict(self):
        """Transforma dados do Professor em dicionário."""
        dados = super().to_dict() 
        
        id_esc = self.escola_associada.id_escola if hasattr(self.escola_associada, 'id_escola') else self.escola_associada
        
        dados.update({
            "registro_funcional": self.registro_funcional,
            "id_escola": id_esc,
            "titulacao": self.titulacao,
            "area_atuacao": self.area_atuacao,
            "salario": self.salario,
            "turmas_vinculadas": [t.id_turma if hasattr(t, 'id_turma') else t for t in self.turmas_associadas]
        })
        return dados
    
    def exibir_perfil(self):
        """Exibe os dados formatados do professor."""
        print("\n" + "="*40)
        print(f"🍎 PERFIL DO PROFESSOR: {self.nome}")
        print("="*40)
        print(f"RF:         {self.registro_funcional}")
        print(f"Titulação:  {self.titulacao}")
        print(f"Área:       {self.area_atuacao}")
        print(f"E-mail:     {self.email}")
        print(f"Salário:    R$ {self.salario:.2f}")
        print(f"Turmas:     {', '.join([t.nome if hasattr(t, 'nome') else str(t) for t in self.turmas_associadas]) or 'Nenhuma'}")
        print(f"Status:     {'Ativo' if self.status else 'Inativo'}")
        print("="*40 + "\n")