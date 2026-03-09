import sqlite3
import os
from src.models.municipio import Municipio
from src.models.professor import Professor
from src.models.secretario import Secretario
from src.models.gestor import Gestor
from src.models.aluno import Aluno
from src.models.escola import Escola
from src.models.turma import Turma
from src.models.nota import Nota
from src.models.diario import Diario
from src.models.frequencia import Frequencia
from src.models.demanda import Demanda


class RepositorioGeral:
	"""Classe responsável por gerenciar a conexão com o banco de dados SQLite e realizar as operações de CRUD para todas as entidades do sistema."""
	def __init__(self):
		""""Inicializa a conexão com o banco de dados e cria as colunas necessárias se elas ainda não existirem."""
		os.makedirs("data", exist_ok=True)
		self.connect = sqlite3.connect("data/studyforge.db")
		self.cursor = self.connect.cursor()
		self._criar_colunas()

	""""Responsável por criar as colunas no banco de dados SQLite."""
	def _criar_colunas(self):
		codigo_SQL = ('''
    CREATE TABLE IF NOT EXISTS usuario(
	"id_usuario"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"cpf"	TEXT NOT NULL UNIQUE,
	"nome"	TEXT NOT NULL,
	"email"	TEXT NOT NULL UNIQUE,
	"senha"	TEXT NOT NULL,
	"telefone"	TEXT NOT NULL CHECK(length("telefone") = 10 OR length("telefone") = 11),
	"data_nascimento"	TEXT NOT NULL,
    "login"	INTEGER DEFAULT 0,
	"status"	INTEGER  DEFAULT 1,
	"tipo"	TEXT CHECK("tipo" IN ('SECRETARIO', 'GESTOR', 'PROFESSOR', 'ALUNO'))
    ); 
                         
    CREATE TABLE IF NOT EXISTS municipio(
	"id_municipio"	INTEGER,
	"nome"	TEXT NOT NULL,
	"estado"	TEXT NOT NULL CHECK(length("estado") = 2),
	"verba_disponivel_municipio"	REAL DEFAULT 0.0,
	"nota_de_corte" REAL DEFAULT 7.0,
	PRIMARY KEY("id_municipio" AUTOINCREMENT)
    );
                         
    CREATE TABLE IF NOT EXISTS gestor(
    "id_usuario"    INTEGER PRIMARY KEY,
    "id_escola"     INTEGER, -- Referencia escola_associada na classe
    FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola"),
    FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
	);
                         
    CREATE TABLE IF NOT EXISTS escola(
	"id_escola"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"nome"	TEXT NOT NULL,
	"verba_disponivel_escola"	REAL DEFAULT 0.0,
    "capacidade_infraestrutura" 	INTEGER DEFAULT 500,     
	"id_municipio"	INTEGER, -- referencia municipio na classe
	"id_gestor"	INTEGER, -- referencia gestor_atual na classe
    "id_localizacao" INTEGER, -- referencia endereco na classe
	FOREIGN KEY("id_gestor") REFERENCES "gestor"("id_usuario"),
	FOREIGN KEY("id_municipio") REFERENCES "municipio"("id_municipio"),
    FOREIGN KEY("id_localizacao") REFERENCES "escola_endereco"("id_localizacao")
    );
                         
    CREATE TABLE IF NOT EXISTS escola_endereco(
	"id_escola"	INTEGER,
	"id_localizacao"	INTEGER,
	"cep"	TEXT NOT NULL,
	"rua"	TEXT NOT NULL,
	"numero"	TEXT NOT NULL,
	"bairro"	TEXT NOT NULL,
	PRIMARY KEY("id_escola","id_localizacao"),
	FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola") ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS turma(
	"id_turma"	INTEGER,
	"nome"	TEXT NOT NULL,
	"ano_letivo"	INTEGER NOT NULL,
	"turno"	TEXT NOT NULL CHECK("turno" IN ('MANHÃ', 'TARDE', 'NOITE', 'INTEGRAL')),
	"capacidade_maxima"	INTEGER NOT NULL,
	"id_escola"	INTEGER,
	PRIMARY KEY("id_turma" AUTOINCREMENT),
	FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola") ON DELETE RESTRICT
    );
                         
    CREATE TABLE IF NOT EXISTS secretario(
	"id_usuario"	INTEGER,
	"departamento"	TEXT NOT NULL,
	"id_municipio"	INTEGER, -- Referencia municipio_responsável no init da classe
	PRIMARY KEY("id_usuario"),
	FOREIGN KEY("id_municipio") REFERENCES "municipio"("id_municipio"),
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS professor(
	"id_usuario"	INTEGER PRIMARY KEY,
	"salario"	REAL NOT NULL CHECK("salario" > 0),
	"titulacao"	TEXT NOT NULL,
	"area_atuacao"	TEXT NOT NULL,
	"registro_funcional"	TEXT NOT NULL UNIQUE,
    "id_escola" INTEGER,
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE,
    FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola")
    );
                         
    CREATE TABLE IF NOT EXISTS aluno(
	"id_usuario"	INTEGER PRIMARY KEY,
	"matricula"	TEXT NOT NULL UNIQUE,
	"id_turma"	INTEGER, -- Referencia turma_associada na classe
	FOREIGN KEY("id_turma") REFERENCES "turma"("id_turma") ON DELETE RESTRICT,
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS demanda(
	"id_demanda"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"descricao"	TEXT NOT NULL,
	"status"	TEXT DEFAULT 'PENDENTE' CHECK("status" IN ('PENDENTE', 'APROVADO', 'RECUSADO', 'EM_EXECUCAO', 'CONCLUIDO')),
	"prioridade"	TEXT NOT NULL CHECK("prioridade" IN ('BAIXA', 'MEDIA', 'ALTA', 'URGENTE')),
	"id_solicitante"	INTEGER, -- Referencia solicitante na classe
	"id_municipio"	INTEGER, -- Referencia municipio_responsavel na classe
    "tipo" TEXT CHECK("tipo" IN('INFRAESTRUTURA', 'PEDAGOGICA')),
    "data_criacao" TEXT NOT NULL, -- referencia criado_em na classe
	"ultimo_editor" TEXT, -- referencia alterado_por na classe
    "data_alteracao" TEXT,  
    "alerta_auditoria" TEXT, 
	FOREIGN KEY("id_municipio") REFERENCES "municipio"("id_municipio"),
	FOREIGN KEY("id_solicitante") REFERENCES "usuario"("id_usuario")
    );
                         
    CREATE TABLE IF NOT EXISTS demanda_infraestrutura(
	"id_demanda"	INTEGER,
	"custo_estimado"	REAL NOT NULL CHECK("custo_estimado" >= 0),
	"id_escola"	INTEGER,
	PRIMARY KEY("id_demanda"),
	FOREIGN KEY("id_demanda") REFERENCES "demanda"("id_demanda"),
	FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola") ON DELETE RESTRICT
    );
                         
    CREATE TABLE IF NOT EXISTS demanda_pedagogica(
	"id_demanda"	INTEGER PRIMARY KEY,
	"indice_lacuna"	REAL NOT NULL CHECK("indice_lacuna" >= 0.0 AND "indice_lacuna" <= 1.0),
	"frequencia_apurada"	REAL NOT NULL CHECK("frequencia_apurada" <= 1.0 AND "frequencia_apurada" >= 0),
	"id_turma"	INTEGER, -- referencia turma_alvo na classe
    "disciplina_alvo" TEXT NOT NULL,
    "id_professor" INTEGER, -- referencia professor_responsavel na classe,
    "qtd_alunos_risco" INTEGER,
	FOREIGN KEY("id_demanda") REFERENCES "demanda"("id_demanda"),
	FOREIGN KEY("id_turma") REFERENCES "turma"("id_turma") ON DELETE RESTRICT,
    FOREIGN KEY("id_professor") REFERENCES "professor"("id_usuario")
    );
                         
    CREATE TABLE IF NOT EXISTS nota(
	"id_nota"	INTEGER,
	"disciplina"	TEXT NOT NULL,
	"valor"	REAL NOT NULL CHECK("valor" >= 0 AND "valor" <= 10),
	"data"	TEXT NOT NULL,
	"tipo"	TEXT NOT NULL,
	"id_aluno"	INTEGER,
	"id_turma"	INTEGER,
	PRIMARY KEY("id_nota" AUTOINCREMENT),
	FOREIGN KEY("id_aluno") REFERENCES "aluno"("id_usuario") ON DELETE RESTRICT,
	FOREIGN KEY("id_turma") REFERENCES "turma"("id_turma")
    );
                         
    CREATE TABLE IF NOT EXISTS diario(
	"id_diario"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"disciplina"	TEXT NOT NULL,
	"data"	TEXT NOT NULL,
	"conteudo"	TEXT NOT NULL,
	"id_professor"	INTEGER,
	"id_turma"	INTEGER,
	FOREIGN KEY("id_professor") REFERENCES "professor"("id_usuario") ON DELETE RESTRICT,
	FOREIGN KEY("id_turma") REFERENCES "turma"("id_turma") ON DELETE RESTRICT
    );
                         
    CREATE TABLE IF NOT EXISTS frequencia(
	"id_frequencia"	INTEGER,
	"status"	TEXT NOT NULL CHECK("status" IN ('PRESENTE', 'AUSENTE')),
	"id_aluno"	INTEGER,
	"id_diario"	INTEGER,
	PRIMARY KEY("id_frequencia" AUTOINCREMENT),
	FOREIGN KEY("id_aluno") REFERENCES "aluno"("id_usuario") ON DELETE RESTRICT,
	FOREIGN KEY("id_diario") REFERENCES "diario"("id_diario") ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS configuracoes(
	"id_config"	INTEGER,
	"frequencia_minima"	REAL DEFAULT 0.75 CHECK("frequencia_minima" >= 0 AND "frequencia_minima" <= 1),
	"indice_lacuna_maximo"	REAL DEFAULT 0.3 CHECK("indice_lacuna_maximo" >= 0 AND "indice_lacuna_maximo" <= 1),
	"limite_custo_demanda"	REAL DEFAULT 15000.0 CHECK("limite_custo_demanda" >= 0),
	"id_municipio"	INTEGER UNIQUE, -- referencia municipio na classe
	PRIMARY KEY("id_config" AUTOINCREMENT),
	FOREIGN KEY("id_municipio") REFERENCES "municipio"("id_municipio")
    );
                         
    CREATE TABLE IF NOT EXISTS professor_escola_alocado(
	"id_professor"	INTEGER,
	"id_escola"	INTEGER,
	PRIMARY KEY("id_professor","id_escola"),
	FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola") ON DELETE RESTRICT,
	FOREIGN KEY("id_professor") REFERENCES "professor"("id_usuario") ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS professor_turma_alocado(
	"id_professor"	INTEGER,
	"id_turma"	INTEGER,
	PRIMARY KEY("id_professor","id_turma"),
	FOREIGN KEY("id_professor") REFERENCES "professor"("id_usuario") ON DELETE CASCADE,
	FOREIGN KEY("id_turma") REFERENCES "turma"("id_turma") ON DELETE RESTRICT
    );
		''')
		self.cursor.executescript(codigo_SQL)
		self.connect.commit()

	""""Métodos responsáveis por salvar os objetos do sistema no banco de dados SQLite."""
	def salvar_municipio(self, municipio_obj):
		try:
			dados = municipio_obj.to_dict()
			codigo_SQL = ('''INSERT INTO municipio (nome, estado, verba_disponivel_municipio, nota_de_corte) VALUES (:nome,:estado,:verba_disponivel_municipio,:nota_de_corte)''')
			self.cursor.execute(codigo_SQL, dados)
			municipio_obj._id_municipio = self.cursor.lastrowid
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar município no banco de dados.")
		
	def salvar_usuario(self, usuario_obj):
		try:
			dados = usuario_obj.to_dict()
			codigo_SQL = ('''INSERT INTO usuario (cpf, nome, email, senha, telefone, data_nascimento, tipo) VALUES (:cpf,:nome,:email,:senha,:telefone,:data_nascimento,:tipo)''')
			self.cursor.execute(codigo_SQL, dados)
			usuario_obj._id_usuario = self.cursor.lastrowid
			dados_especificos = usuario_obj.to_dict_especifico()
			dados_especificos["id_usuario"] = usuario_obj._id_usuario
			sql_filha = None
			if usuario_obj._tipo == "SECRETARIO":
				sql_filha = ('''INSERT INTO secretario(id_usuario, departamento, id_municipio) VALUES (:id_usuario, :departamento, :id_municipio)''')
			elif usuario_obj._tipo == "GESTOR":
				sql_filha = ('''INSERT INTO gestor(id_usuario, id_escola) VALUES (:id_usuario, :id_escola)''')
			elif usuario_obj._tipo == "PROFESSOR":
				sql_filha = ('''INSERT INTO professor(id_usuario, salario, titulacao, area_atuacao, registro_funcional, id_escola) VALUES (:id_usuario, :salario, :titulacao, :area_atuacao, :registro_funcional, :id_escola)''')
			elif usuario_obj._tipo == "ALUNO":
				sql_filha = ('''INSERT INTO aluno(id_usuario, matricula, id_turma) VALUES (:id_usuario, :matricula, :id_turma)''')
			if sql_filha:
				self.cursor.execute(sql_filha, dados_especificos)
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar usuário no banco de dados.")
		
	def salvar_escola(self, escola_obj):
		try:
			dados = escola_obj.to_dict()
			codigo_SQL = ('''INSERT INTO escola(nome, verba_disponivel_escola, capacidade_infraestrutura, id_municipio, id_gestor) VALUES (:nome, :verba_disponivel_escola, :capacidade_infraestrutura, :id_municipio, :id_gestor)''')
			self.cursor.execute(codigo_SQL, dados)
			escola_obj._id_escola = self.cursor.lastrowid
			if escola_obj._endereco:
				dados_endereco = escola_obj._endereco.to_dict()
				dados_endereco["id_escola"] = escola_obj._id_endereco
				dados_endereco["id_localizacao"] = 1
				sql_endereco = ('''INSERT INTO endereco(id_escola, id_localizacao, cep, rua, numero, bairro) VALUES (:id_escola, :id_localizacao, :cep, :rua, :numero, :bairro)''')
				self.cursor.execute(sql_endereco, dados_endereco)
				escola_obj._endereco._id_localizacao = 1
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar escola no banco de dados.")

	def salvar_turma(self, turma_obj):
		try:
			dados = turma_obj.to_dict()
			codigo_SQL = ('''INSERT INTO turma(nome, ano_letivo, turno, capacidade_maxima, id_escola) VALUES (:nome, :ano_letivo, :turno, :capacidade_maxima, :id_escola)''')
			self.cursor.execute(codigo_SQL, dados)
			turma_obj._id_turma = self.cursor.lastrowid
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar turma no banco de dados.")
		
	def salvar_nota(self, nota_obj):
		try:
			dados = nota_obj.to_dict()
			codigo_SQL = ('''INSERT INTO nota(disciplina, valor, data, tipo, id_aluno, id_turma) VALUES (:disciplina, :valor, :data, :tipo, :id_aluno, :id_turma)''')
			self.cursor.execute(codigo_SQL, dados)
			nota_obj._id_nota = self.cursor.lastrowid
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar nota no banco de dados.")
		
	def salvar_diario(self, diario_obj):
		try:
			dados = diario_obj.to_dict()
			codigo_SQL = ('''INSERT INTO diario(disciplina, data, conteudo, id_professor, id_turma) VALUES (:disciplina, :data, :conteudo, :id_professor, :id_turma)''')
			self.cursor.execute(codigo_SQL, dados)
			diario_obj._id_diario = self.cursor.lastrowid
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar diário no banco de dados.")
		
	def salvar_frequencia(self, frequencia_obj):
		try:
			dados = frequencia_obj.to_dict()
			codigo_SQL = ('''INSERT INTO frequencia(status, id_aluno, id_diario) VALUES (:status, :id_aluno, :id_diario)''')
			self.cursor.execute(codigo_SQL, dados)
			frequencia_obj._id_frequencia = self.cursor.lastrowid
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar frequência no banco de dados.")
		
	def salvar_demanda(self, demanda_obj):
		try:
			dados = demanda_obj.to_dict()
			codigo_SQL = ('''INSERT INTO demanda(descricao, status, prioridade, id_solicitante, id_municipio, tipo, data_criacao, ultimo_editor, data_alteracao, alerta_auditoria) VALUES (:descricao, :status, :prioridade, :id_solicitante, :id_municipio, :tipo, :data_criacao, :ultimo_editor, :data_alteracao, :alerta_auditoria)''')
			self.cursor.execute(codigo_SQL, dados)
			demanda_obj._id_demanda = self.cursor.lastrowid
			dados_especificos = demanda_obj._to_dict_especifico()
			dados_especificos["id_demanda"] = demanda_obj._id_demanda
			SQL_filha = None
			if demanda_obj._tipo == "INFRAESTRUTURA":
				SQL_filha = ('''INSERT INTO demanda_infraestrutura(id_demanda, custo_estimado, id_escola) VALUES (:id_demanda, :custo_estimado, :id_escola)''')
			elif demanda_obj._tipo =="PEDAGOGICA":
				SQL_filha = ('''INSERT INTO demanda_pedagogica(id_demanda, indice_lacuna, frequencia_apurada, id_turma, disciplina_alvo, id_professor, qtd_alunos_risco) VALUES (:id_demanda, :indice_lacuna, :frequencia_apurada, :id_turma, :disciplina_alvo, :id_professor, :qtd_alunos_risco)''')
			if SQL_filha:
				self.cursor.execute(SQL_filha, dados_especificos)
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar demanda no banco de dados.")
		
	""""Métodos responsáveis por ler os dados do sistema no banco de dados SQLite e transformar em objetos novamente."""
	def buscar_usuario_por_cpf(self, cpf_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM usuario WHERE cpf = (:cpf)''')
			self.cursor.execute(busca_tupla_sql, {"cpf": cpf_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				usuario_obj = Usuario(tupla_sql[0], tupla_sql[2], tupla_sql[1], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[9], tupla_sql[7], tupla_sql[8])
				return usuario_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar usuário por CPF no banco de dados.")
		
	def buscar_municipio_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM municipio WHERE id_municipio = (:id_municipio)''')
			self.cursor.execute(busca_tupla_sql, {"id_municipio": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				municipio_obj = Municipio(tupla_sql[1], tupla_sql[0], tupla_sql[2], tupla_sql[3], tupla_sql[4])
				return municipio_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar município no banco de dados.")
	
	def listar_municipios(self):
		try:
			lista_municipios_sql = ('''SELECT * FROM municipio''')
			self.cursor.execute(lista_municipios_sql)
			tuplas_encontradas = self.cursor.fetchall()
			objetos_municipio = []
			for tupla in tuplas_encontradas:
				municipio_obj = Municipio(tupla[1], tupla[0], tupla[2], tupla[3], tupla[4])
				objetos_municipio.append(municipio_obj)
			return objetos_municipio
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar municípios no banco de dados.")
		
	def buscar_secretario_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM usuario JOIN secretario ON usuario.id_usuario = secretario.id_usuario WHERE usuario.id_usuario = (:id_usuario)''')
			self.cursor.execute(busca_tupla_sql, {"id_usuario": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				secretario_obj = Secretario(tupla_sql[0], tupla_sql[2], tupla_sql[1], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[12], tupla_sql[11])
				return secretario_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar secretário no banco de dados.")
		
	def listar_secretarios(self):
		try:
			lista_secretarios_sql = ('''SELECT * FROM usuario JOIN secretario ON usuario.id_usuario = secretario.id_usuario''')
			self.cursor.execute(lista_secretarios_sql)
			tuplas_secretario = self.cursor.fetchall()
			objetos_secretario = []
			for tupla in tuplas_secretario:
				secretario_obj = Secretario(tupla[0], tupla[2], tupla[1], tupla[3], tupla[4], tupla[5], tupla[6], tupla[12], tupla[11])
				objetos_secretario.append(secretario_obj)
			return objetos_secretario
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar secretários no banco de dados.")
		
	def buscar_gestor_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM usuario JOIN gestor ON usuario.id_usuario = gestor.id_usuario WHERE usuario.id_usuario = (:id_usuario)''')
			self.cursor.execute(busca_tupla_sql, {"id_usuario": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				gestor_obj = Gestor(tupla_sql[0], tupla_sql[2], tupla_sql[1], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[11])
				return gestor_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar gestor no banco de dados.")
		
	def listar_gestores(self):
		try:
			lista_gestores_sql = ('''SELECT * FROM usuario JOIN gestor ON usuario.id_usuario = gestor.id_usuario''')
			self.cursor.execute(lista_gestores_sql)
			tuplas_gestor = self.cursor.fetchall()
			objetos_gestor = []
			for tupla in tuplas_gestor:
				gestor_obj = Gestor(tupla[0], tupla[2], tupla[1], tupla[3], tupla[4], tupla[5], tupla[6], tupla[11])
				objetos_gestor.append(gestor_obj)
			return objetos_gestor
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar gestores no banco de dados.")
		
	def buscar_professor_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM usuario JOIN professor ON usuario.id_usuario = professor.id_usuario WHERE usuario.id_usuario = (:id_usuario)''')
			self.cursor.execute (busca_tupla_sql, {"id_usuario": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				professor_obj = Professor(tupla_sql[0], tupla_sql[2], tupla_sql[1], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[14], tupla_sql[15], tupla_sql[12], tupla_sql[13], tupla_sql[11])
				return professor_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar professor no banco de dados.")
		
	def listar_professores(self):
		try:
			lista_professores_sql = ('''SELECT * FROM usuario JOIN professor ON usuario.id_usuario = professor.id_usuario''')
			self.cursor.execute(lista_professores_sql)
			tuplas_professor = self.cursor.fetchall()
			objetos_professor = []
			for tupla in tuplas_professor:
				professor_obj = Professor(tupla[0], tupla[2], tupla[1], tupla[3], tupla[4], tupla[5], tupla[6], tupla[14], tupla[15], tupla[12], tupla[13], tupla[11])
				objetos_professor.append(professor_obj)
			return objetos_professor
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar professores no banco de dados.")
		
	def buscar_aluno_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM usuario JOIN aluno ON usuario.id_usuario = aluno.id_usuario WHERE usuario.id_usuario = (:id_usuario)''')
			self.cursor.execute(busca_tupla_sql, {"id_usuario": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				aluno_obj = Aluno(tupla_sql[0], tupla_sql[2], tupla_sql[1], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[12], tupla_sql[11])
				return aluno_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar aluno no banco de dados.")
		
	def listar_alunos(self):
		try:
			lista_alunos_sql = ('''SELECT * FROM usuario JOIN aluno ON usuario.id_usuario = aluno.id_usuario''')
			self.cursor.execute(lista_alunos_sql)
			tuplas_aluno = self.cursor.fetchall()
			objetos_aluno = []
			for tupla in tuplas_aluno:
				aluno_obj = Aluno(tupla[0], tupla[2], tupla[1], tupla[3], tupla[4], tupla[5], tupla[6], tupla[12], tupla[11])
				objetos_aluno.append(aluno_obj)
			return objetos_aluno
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar alunos no banco de dados.")
		
	def buscar_escola_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM escola JOIN municipio ON escola.id_municipio = municipio.id_municipio WHERE escola.id_escola = (:id_escola)''')
			self.cursor.execute(busca_tupla_sql, {"id_escola": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				escola_obj = Escola(tupla_sql[1], tupla_sql[6], tupla_sql[0], tupla_sql[5], tupla_sql[2], tupla_sql[4], tupla_sql[8], tupla_sql[3])
				return escola_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar escola no banco de dados.")
	
	def listar_escolas(self):
		try:
			lista_escolas_sql = ('''SELECT * FROM escola JOIN municipio ON escola.id_municipio = municipio.id_municipio''')
			self.cursor.execute(lista_escolas_sql)
			tuplas_escola = self.cursor.fetchall()
			objetos_escola = []
			for tupla in tuplas_escola:
				escola_obj = Escola(tupla[1], tupla[6], tupla[0], tupla[5], tupla[2], tupla[4], tupla[8], tupla[3])
				objetos_escola.append(escola_obj)
			return objetos_escola
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar escolas no banco de dados.")
		
	def listar_escolas_por_municipio(self, municipio_buscado):
		try:
			lista_escolas_sql = ('''SELECT * FROM escola JOIN municipio ON escola.id_municipio = municipio.id_municipio WHERE municipio.nome = (:municipio)''')
			self.cursor.execute(lista_escolas_sql, {"municipio" : municipio_buscado})
			tuplas_escola = self.cursor.fetchall()
			escolas_obj = []
			for tupla in tuplas_escola:
				escola_obj = Escola(tupla[1], tupla[6], tupla[0], tupla[5], tupla[2], tupla[4], tupla[8], tupla[3])
				escolas_obj.append(escola_obj)
			return escolas_obj
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar escolas por município no banco de dados.")
		
	def buscar_turma_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM turma JOIN escola ON turma.id_escola = escola.id_escola WHERE turma.id_turma = (:id_turma)''')
			self.cursor.execute(busca_tupla_sql, {"id_turma": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				turma_obj = Turma(tupla_sql[0], tupla_sql[1], tupla_sql[2], tupla_sql[5], tupla_sql[7], tupla_sql[3], tupla_sql[4])
				return turma_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar turma no banco de dados.")
		
	def listar_turmas(self):
		try:
			lista_turmas_sql = ('''SELECT * FROM turma JOIN escola ON turma.id_escola = escola.id_escola''')
			self.cursor.execute(lista_turmas_sql)
			tuplas_turma = self.cursor.fetchall()
			objetos_turma = []
			for tupla in tuplas_turma:
				turma_obj = Turma(tupla[0], tupla[1], tupla[2], tupla[5], tupla[7], tupla[3], tupla[4])
				objetos_turma.append(turma_obj)
			return objetos_turma
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar turmas no banco de dados.")
	
	def listar_turmas_por_escola(self, escola_buscada):
		try:
			lista_turmas_sql = ('''SELECT * FROM turma JOIN escola ON turma.id_escola = escola.id_escola WHERE escola.nome = (:escola)''')
			self.cursor.execute(lista_turmas_sql, {"escola" : escola_buscada})
			tuplas_turma = self.cursor.fetchall()
			turmas_obj = []
			for tupla in tuplas_turma:
				turma_obj = Turma(tupla[0], tupla[1], tupla[2], tupla[5], tupla[7], tupla[3], tupla[4])
				turmas_obj.append(turma_obj)
			return turmas_obj
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar turmas por escola no banco de dados.")
		
	def buscar_nota_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM nota JOIN aluno ON nota.id_aluno = aluno.id_usuario JOIN usuario ON nota.id_aluno = usuario.id_usuario WHERE nota.id_nota = (:id_nota)''')
			self.cursor.execute(busca_tupla_sql, {"id_nota": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				nota_obj = Nota(tupla_sql[0], tupla_sql[5], tupla_sql[12], tupla_sql[6], tupla_sql[1], tupla_sql[2], tupla_sql[3], tupla_sql[4])
				return nota_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar nota no banco de dados.")
		
	def listar_notas_por_aluno(self, id_aluno):
		try:
			lista_notas_sql = ('''SELECT * FROM nota JOIN aluno ON nota.id_aluno = aluno.id_usuario JOIN usuario ON nota.id_aluno = usuario.id_usuario WHERE aluno.id_usuario = (:id_aluno)''')
			self.cursor.execute(lista_notas_sql, {"id_aluno": id_aluno})
			tuplas_nota = self.cursor.fetchall()
			notas_obj = []
			for tupla in tuplas_nota:
				nota_obj = Nota(tupla[0], tupla[5], tupla[12], tupla[6], tupla[1], tupla[2], tupla[3], tupla[4])
				notas_obj.append(nota_obj)
			return notas_obj
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar notas por aluno no banco de dados.")
	
	def listar_notas_por_turma(self, id_turma):
		try:
			lista_notas_sql = ('''SELECT * FROM nota JOIN aluno ON nota.id_aluno = aluno.id_usuario JOIN usuario ON nota.id_aluno = usuario.id_usuario JOIN turma ON nota.id_turma = turma.id_turma WHERE  turma.id_turma = (:id_turma)''')
			self.cursor.execute(lista_notas_sql, {"id_turma": id_turma})
			tuplas_nota = self.cursor.fetchall()
			notas_obj = []
			for tupla in tuplas_nota:
				nota_obj = Nota(tupla[0], tupla[5], tupla[12], tupla[6], tupla[1], tupla[2], tupla[3], tupla[4])
				notas_obj.append(nota_obj)
			return notas_obj
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar notas por turma no banco de dados.")
		
	