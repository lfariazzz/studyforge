from src.models.usuario import Usuario
from datetime import date
import re
"""
Representa a entidade Aluno conforme o diagrama UML.
Herda atributos base de Usuario e gerencia sua vida acadêmica.
"""

class Aluno(Usuario):
    def __init__(self, nome, cpf, email, senha, telefone, data_nascimento,
                 id_matricula, turma_associada=None, status=True):
        super().__init__(nome, cpf, email, senha, telefone, data_nascimento, status)

        self.id_matricula = id_matricula
        self.turma_associada = turma_associada 
        self._notas = {}
        self._historico_frequencia = [] 

    # -----------------
    # GETTERS E SETTERS
    # -----------------

    @property
    def id_matricula(self):
        """Retorna a matrícula única do aluno."""
        return self._id_matricula
    
    @id_matricula.setter
    def id_matricula(self, valor):
        if not isinstance(valor, str):
            raise TypeError("Erro: O id da matrícula deve ser uma string!")
        
        matricula_limpa = valor.strip().upper()

        padrao_matricula = r'^MAT-\d{4}-\d{4}$'

        if not re.match(padrao_matricula, matricula_limpa):
            raise ValueError("Erro: Matrícula inválida! Use o padrão MAT-ANO-0000 (Ex: MAT-2026-0001).")
        
        else:
            self._id_matricula = matricula_limpa

    @property
    def turma_associada(self):
        """Retorna o objeto ou identificador da turma do aluno."""
        return self._turma_associada
    
    @turma_associada.setter
    def turma_associada(self, valor):
        if hasattr(valor, 'id_turma'):
            self._turma_associada = valor
        elif isinstance(valor, str):
            self._turma_associada = valor
        elif valor is None:
            self._turma_associada = None
        else:
            raise ValueError("Erro: turma_associada deve ser um objeto Turma ou uma string identificadora.")

    #implementado por Levi para integração com o src/services/avaliador_frequencia.py (RN02)    
    @property
    def presenca(self):
        return self._historico_frequencia


    #requer refatoração, ass:Levi 
    @property
    def frequencia(self):
        """
        Calcula a frequência baseada no total de aulas da TURMA.
        """
        from src.models.turma import Turma
        
        if not self.turma_associada or not hasattr(self.turma_associada, '_diario_de_classe'):
            return 100.0
        total_aulas_turma = len(self.turma_associada._diario_de_classe)
        
        if total_aulas_turma == 0:
            return 100.0

        presencas = sum(1 for registro in self._historico_frequencia if registro.get('presenca') is True)
        
        percentual = (presencas / total_aulas_turma) * 100
        return round(percentual, 2)
        
    # -------
    # MÉTODOS
    # -------

    def get_permissao(self) -> str:
        if not self.turma_associada:
            return "Aluno: Sem turma vinculada. Acesso restrito."
        
        nome_turma = self.turma_associada.nome if hasattr(self.turma_associada, 'nome') else self.turma_associada
        return f"Aluno: Visualização de conteúdos acadêmicos limitada à turma {nome_turma}."
    
    def ver_frequencia(self):
        freq = self.frequencia
        alerta = "⚠️ ATENÇÃO: Frequência abaixo de 75%!" if freq < 75 else "✅ Frequência regular."

        print(f"\n--- Relatório de Frequência: {self.nome} ---")
        print(f"Frequência Atual: {freq}%")
        print(alerta)
        print("------------------------------------------")

    def ver_horario(self):
        if not self.turma_associada:
            print(f"⚠️ Aluno {self.nome} não possui vínculo com turma.")
            return

        cronograma = self.turma_associada.obter_quadro_horario()
        print(f"\n--- QUADRO DE HORÁRIOS: {cronograma['Turma']} ---")
        print(f"Professores: {cronograma['Professores']}")

        if "Horarios" in cronograma:
            for dia, horas in cronograma["Horarios"].items():
                print(f"{dia}: {', '.join(horas)}")
        else:
            print("Horários detalhados não definidos.")
    
    def exibir_perfil(self):
        nome_t = self.turma_associada.nome if hasattr(self.turma_associada, 'nome') else self.turma_associada
        freq = self.frequencia
        alerta = " ⚠️" if freq < 75 else "" 

        print("\n" + "="*35)
        print(f"🎓 PERFIL DO ALUNO: {self.nome}")
        print("="*35)
        print(f"Matrícula: {self.id_matricula}")
        print(f"Turma:     {nome_t}")
        print(f"E-mail:    {self.email}")
        print(f"Frequência: {freq}%{alerta}")
        print(f"Status:    {'Ativo' if self.status else 'Inativo'}")
        print("="*35 + "\n")

    def ver_noticias(self, lista_noticias: list[dict]):
        if not self.turma_associada:
            return

        id_escola_aluno = self.turma_associada.id_escola
        id_turma_aluno = self.turma_associada.id_turma
        
        print(f"\n--- MURAL DE NOTÍCIAS PARA: {self.nome} ---")
        avisos = False

        for n in lista_noticias:
            if n.get("id_escola") == id_escola_aluno or n.get("id_turma") == id_turma_aluno:
                tipo = "TURMA" if n.get("id_turma") else "ESCOLA"
                print(f"[{tipo}] {n['data']} - {n['titulo']}")
                avisos = True

        if not avisos:
            print("Nenhuma notícia nova.")

    #refatorado por Levi para implementação da RN02
    def registrar_presenca(self, data: date, presente: bool):
        """Alimenta o histórico (Data e Booleano)."""
        if not isinstance(presente, bool):
            raise TypeError("O status de presença deve ser True ou False.")
        
        self._historico_frequencia.append({
            "data": data,
            "aluno": self.nome,
            "presenca": presente
        })

    def baixar_material(self):
        pass
    
    def to_dict(self):
        dados = super().to_dict()
        id_t = self.turma_associada.id_turma if hasattr(self.turma_associada, 'id_turma') else self.turma_associada
        
        dados.update({
            "id_matricula": self.id_matricula,
            "id_turma": id_t,
            "percentual_frequencia": self.frequencia,
            "historico_frequencia": self._historico_frequencia,
            "notas": self._notas 
        })
        return dados