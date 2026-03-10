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
	"nome"	TEXT NOT NULL,
	"cpf"	TEXT NOT NULL UNIQUE,
	"email"	TEXT NOT NULL UNIQUE,
	"senha"	TEXT NOT NULL,
	"telefone"	TEXT NOT NULL CHECK(length("telefone") = 10 OR length("telefone") = 11),
	"data_nascimento"	TEXT NOT NULL,
	"tipo"	TEXT CHECK("tipo" IN ('SECRETARIO', 'GESTOR', 'PROFESSOR', 'ALUNO')),
    "login"	INTEGER DEFAULT 0,
	"status"	INTEGER  DEFAULT 1
    ); 
                         
    CREATE TABLE IF NOT EXISTS municipio(
	"nome"	TEXT NOT NULL,
	"id_municipio"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"estado"	TEXT NOT NULL CHECK(length("estado") = 2),
	"verba_disponivel_municipio"	REAL DEFAULT 0.0,
	"nota_de_corte" REAL DEFAULT 7.0
    );
                         
    CREATE TABLE IF NOT EXISTS gestor(
    "id_usuario"    INTEGER PRIMARY KEY,
    "id_escola"     INTEGER, -- Referencia escola_associada na classe
    FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola"),
    FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
	);
                         
    CREATE TABLE IF NOT EXISTS escola(
	"nome"	TEXT NOT NULL,
	"id_localizacao" INTEGER, -- referencia id_endereco na classe,
	"id_escola"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"id_gestor"	INTEGER, -- referencia gestor_atual na classe
	"verba_disponivel_escola"	REAL DEFAULT 0.0,
	"id_municipio"	INTEGER, -- referencia municipio na classe
    "capacidade_infraestrutura" 	INTEGER DEFAULT 500,     
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
	"id_turma"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"nome"	TEXT NOT NULL,
	"ano_letivo"	INTEGER NOT NULL,
	"id_escola"	INTEGER,
	"turno"	TEXT NOT NULL CHECK("turno" IN ('MANHÃ', 'TARDE', 'NOITE', 'INTEGRAL')),
	"capacidade_maxima"	INTEGER NOT NULL,
	FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola") ON DELETE RESTRICT
    );
                         
    CREATE TABLE IF NOT EXISTS secretario(
	"id_usuario"	INTEGER PRIMARY KEY,
	"id_municipio"	INTEGER, -- Referencia municipio_responsável no init da classe
	"departamento"	TEXT NOT NULL,
	FOREIGN KEY("id_municipio") REFERENCES "municipio"("id_municipio"),
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS professor(
	"id_usuario"	INTEGER PRIMARY KEY,
	"registro_funcional"	TEXT NOT NULL UNIQUE,
	"id_escola" INTEGER, -- referencia escola_associada no init da classe
	"titulacao"	TEXT NOT NULL,
	"area_atuacao"	TEXT NOT NULL,
	"salario"	REAL NOT NULL CHECK("salario" > 0),
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE,
    FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola")
    );
                         
    CREATE TABLE IF NOT EXISTS aluno(
	"id_usuario"	INTEGER PRIMARY KEY,
	"id_turma"	INTEGER, -- Referencia turma_associada na classe,
	"matricula"	TEXT NOT NULL UNIQUE,
	FOREIGN KEY("id_turma") REFERENCES "turma"("id_turma") ON DELETE RESTRICT,
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS demanda(
	"id_demanda"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"descricao"	TEXT NOT NULL,
	"prioridade"	TEXT NOT NULL CHECK("prioridade" IN ('BAIXA', 'MEDIA', 'ALTA', 'URGENTE')),
	"id_solicitante"	INTEGER, -- Referencia solicitante na classe,
	"id_municipio"	INTEGER, -- Referencia municipio_responsavel na classe,
	"tipo" TEXT CHECK("tipo" IN('INFRAESTRUTURA', 'PEDAGOGICA')),
	"status"	TEXT DEFAULT 'PENDENTE' CHECK("status" IN ('PENDENTE', 'APROVADO', 'RECUSADO', 'EM_EXECUCAO', 'CONCLUIDO')),
    "data_criacao" TEXT NOT NULL, -- referencia criado_em na classe
	"ultimo_editor" TEXT, -- referencia alterado_por na classe
    "data_alteracao" TEXT,  
    "alerta_auditoria" TEXT, -- referencia alerta na classe
	FOREIGN KEY("id_municipio") REFERENCES "municipio"("id_municipio"),
	FOREIGN KEY("id_solicitante") REFERENCES "usuario"("id_usuario")
    );
                         
    CREATE TABLE IF NOT EXISTS demanda_infraestrutura(
	"id_demanda"	INTEGER PRIMARY KEY,
	"custo_estimado"	REAL NOT NULL CHECK("custo_estimado" >= 0),
	"id_escola"	INTEGER,
	FOREIGN KEY("id_demanda") REFERENCES "demanda"("id_demanda"),
	FOREIGN KEY("id_escola") REFERENCES "escola"("id_escola") ON DELETE RESTRICT
    );
                         
    CREATE TABLE IF NOT EXISTS demanda_pedagogica(
	"id_demanda"	INTEGER PRIMARY KEY,
	"id_turma"	INTEGER, -- referencia turma_alvo na classe
	"frequencia_apurada"	REAL NOT NULL CHECK("frequencia_apurada" <= 1.0 AND "frequencia_apurada" >= 0),
    "disciplina_alvo" TEXT NOT NULL,
    "id_professor" INTEGER, -- referencia professor_responsavel na classe,
    "relatorio_alunos" INTEGER,
	"indice_lacuna"	REAL NOT NULL CHECK("indice_lacuna" >= 0.0 AND "indice_lacuna" <= 1.0),
	FOREIGN KEY("id_demanda") REFERENCES "demanda"("id_demanda"),
	FOREIGN KEY("id_turma") REFERENCES "turma"("id_turma") ON DELETE RESTRICT,
    FOREIGN KEY("id_professor") REFERENCES "professor"("id_usuario")
    );
                         
    CREATE TABLE IF NOT EXISTS nota(
	"id_nota"	INTEGER,
	"id_aluno"	INTEGER,
	"id_turma"	INTEGER,
	"disciplina"	TEXT NOT NULL,
	"valor"	REAL NOT NULL CHECK("valor" >= 0 AND "valor" <= 10),
	"data"	TEXT NOT NULL,
	"tipo"	TEXT NOT NULL,
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
	def _limpar_id(self, valor):
		for attr in ["_id_usuario", "_id_municipio", "_id_escola", "_id_turma", "_id_diario"]:
			if hasattr(valor, attr):
				return getattr(valor, attr)
		return valor

	def salvar_municipio(self, municipio_obj):
		try:
			dados = municipio_obj.to_dict()
			codigo_SQL = ('''INSERT INTO municipio (nome, estado, verba_disponivel_municipio, nota_de_corte) VALUES (:nome,:estado,:verba_disponivel_municipio,:nota_de_corte)''')
			self.cursor.execute(codigo_SQL, dados)
			municipio_obj._id_municipio = self.cursor.lastrowid
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco ao salvar município {municipio_obj.nome}: {e}")
			raise ValueError(f"Erro ao salvar município no banco de dados: {e}")
		
	def salvar_usuario(self, usuario_obj):
		try:
			dados = usuario_obj.to_dict()
			codigo_SQL = ('''INSERT INTO usuario (nome, cpf, email, senha, telefone, data_nascimento, tipo, login) VALUES (:nome,:cpf,:email,:senha,:telefone,:data_nascimento,:tipo, :login)''')
			self.cursor.execute(codigo_SQL, dados)
			usuario_obj._id_usuario = self.cursor.lastrowid
			dados_especificos = usuario_obj.to_dict_especifico()
			dados_especificos["id_usuario"] = usuario_obj._id_usuario
			chaves_para_limpar = ["id_municipio", "id_escola", "id_turma", "municipio", "escola", "turma"]
			for chave in chaves_para_limpar:
				if chave in dados_especificos:
					dados_especificos[chave] = self._limpar_id(dados_especificos[chave])
			sql_filha = None
			if usuario_obj._tipo == "SECRETARIO":
				sql_filha = ('''INSERT INTO secretario(id_usuario, id_municipio, departamento) VALUES (:id_usuario, :id_municipio, :departamento)''')
			elif usuario_obj._tipo == "GESTOR":
				sql_filha = ('''INSERT INTO gestor(id_usuario, id_escola) VALUES (:id_usuario, :id_escola)''')
			elif usuario_obj._tipo == "PROFESSOR":
				sql_filha = ('''INSERT INTO professor(id_usuario, registro_funcional, id_escola, titulacao, area_atuacao, salario) VALUES (:id_usuario, :registro_funcional, :id_escola, :titulacao, :area_atuacao, :salario)''')
			elif usuario_obj._tipo == "ALUNO":
				sql_filha = ('''INSERT INTO aluno(id_usuario, id_turma, matricula) VALUES (:id_usuario, :id_turma, :matricula)''')
			if sql_filha:
				self.cursor.execute(sql_filha, dados_especificos)
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco ao salvar {usuario_obj._tipo}: {e}")
			raise ValueError(f"Erro ao salvar usuário no banco de dados: {e}")
		
	def salvar_escola(self, escola_obj):
		try:
			dados = escola_obj.to_dict()
			codigo_SQL = ('''INSERT INTO escola(nome, id_localizacao, id_escola, id_gestor, verba_disponivel_escola, id_municipio, capacidade_infraestrutura) VALUES (:nome, :id_localizacao, :id_escola, :id_gestor, :verba_disponivel_escola, :id_municipio, :capacidade_infraestrutura)''')
			self.cursor.execute(codigo_SQL, dados)
			escola_obj._id_escola = self.cursor.lastrowid
			if escola_obj._id_endereco:
				dados_endereco = escola_obj._endereco.to_dict()
				dados_endereco["id_escola"] = escola_obj._id_endereco
				dados_endereco["id_localizacao"] = 1
				sql_endereco = ('''INSERT INTO escola_endereco(id_escola, id_localizacao, cep, rua, numero, bairro) VALUES (:id_escola, :id_localizacao, :cep, :rua, :numero, :bairro)''')
				self.cursor.execute(sql_endereco, dados_endereco)
				escola_obj._id_endereco._id_localizacao = 1
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao salvar escola no banco de dados.")

	def salvar_turma(self, turma_obj):
		try:
			dados = turma_obj.to_dict()
			dados["id_escola"] = self._limpar_id(dados.get("id_escola"))
			codigo_SQL = ('''INSERT INTO turma(nome, ano_letivo, id_escola, turno, capacidade_maxima) VALUES (:nome, :ano_letivo, :id_escola, :turno, :capacidade_maxima)''')
			self.cursor.execute(codigo_SQL, dados)
			turma_obj._id_turma = self.cursor.lastrowid
			self.connect.commit()
		except Exception as e:
			self.connect.rollback()
			print(f"❌ Erro no banco ao salvar turma {turma_obj.nome}: {e}")
			raise ValueError(f"Erro ao salvar turma no banco de dados: {e}")
		
	def salvar_nota(self, nota_obj):
		try:
			dados = nota_obj.to_dict()
			dados["id_aluno"] = self._limpar_id(dados.get("id_aluno"))
			dados["id_turma"] = self._limpar_id(dados.get("id_turma"))
			codigo_SQL = ('''INSERT INTO nota(id_aluno, id_turma, disciplina, valor, data, tipo) VALUES (:id_aluno, :id_turma, :disciplina, :valor, :data, :tipo)''')
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
			dados["id_professor"] = self._limpar_id(dados.get("id_professor"))
			dados["id_turma"] = self._limpar_id(dados.get("id_turma"))
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
			dados["id_aluno"] = self._limpar_id(dados.get("id_aluno"))
			dados["id_diario"] = self._limpar_id(dados.get("id_diario"))
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
			dados["id_solicitante"] = self._limpar_id(dados.get("id_solicitante"))
			dados["id_municipio"] = self._limpar_id(dados.get("id_municipio"))
			codigo_SQL = ('''INSERT INTO demanda(descricao, prioridade, id_solicitante, id_municipio, tipo, status, data_criacao, ultimo_editor, data_alteracao, alerta_auditoria) VALUES (:descricao, :prioridade, :id_solicitante, :id_municipio, :tipo, :status, :data_criacao, :ultimo_editor, :data_alteracao, :alerta_auditoria)''')
			self.cursor.execute(codigo_SQL, dados)
			demanda_obj._id_demanda = self.cursor.lastrowid
			dados_especificos = demanda_obj._to_dict_especifico()
			dados_especificos["id_demanda"] = demanda_obj._id_demanda
			chaves_filhas = ["id_escola", "id_turma", "id_professor"]
			for chave in chaves_filhas:
				if chave in dados_especificos:
					dados_especificos[chave] = self._limpar_id(dados_especificos[chave])
			SQL_filha = None
			if demanda_obj._tipo == "INFRAESTRUTURA":
				SQL_filha = ('''INSERT INTO demanda_infraestrutura(id_demanda, custo_estimado, id_escola) VALUES (:id_demanda, :custo_estimado, :id_escola)''')
			elif demanda_obj._tipo =="PEDAGOGICA":
				SQL_filha = ('''INSERT INTO demanda_pedagogica(id_demanda, id_turma, frequencia_apurada,  disciplina_alvo, id_professor, relatorio_alunos, indice_lacuna) VALUES (:id_demanda, :id_turma, :frequencia_apurada, :disciplina_alvo, :id_professor, :relatorio_alunos, :indice_lacuna)''')
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
			busca_tupla_sql = ('''
				SELECT * FROM usuario 
                LEFT JOIN secretario ON usuario.id_usuario = secretario.id_usuario
                LEFT JOIN gestor ON usuario.id_usuario = gestor.id_usuario
                LEFT JOIN professor ON usuario.id_usuario = professor.id_usuario
                LEFT JOIN aluno ON usuario.id_usuario = aluno.id_usuario
                WHERE usuario.cpf = (:cpf)
			''')
			self.cursor.execute(busca_tupla_sql, {"cpf": cpf_busca})
			tupla_sql = self.cursor.fetchone()
			if not tupla_sql:
				return None
			
			tipo = tupla_sql[7]
			if tipo == "SECRETARIO":
				return Secretario(tupla_sql[0], tupla_sql[1], tupla_sql[2], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[7], tupla_sql[8], tupla_sql[9], tupla_sql[11], tupla_sql[12])
			elif tipo == "GESTOR":
				return Gestor(tupla_sql[0], tupla_sql[1], tupla_sql[2], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[7], tupla_sql[8], tupla_sql[9], tupla_sql[14])
			elif tipo == "PROFESSOR":
				return Professor(tupla_sql[0], tupla_sql[1], tupla_sql[2], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[7], tupla_sql[8], tupla_sql[9], tupla_sql[16], tupla_sql[17], tupla_sql[18], tupla_sql[19], tupla_sql[20])
			elif tipo == "ALUNO":
				return Aluno(tupla_sql[0], tupla_sql[1], tupla_sql[2], tupla_sql[3], tupla_sql[4], tupla_sql[5], tupla_sql[6], tupla_sql[7], tupla_sql[8], tupla_sql[9], tupla_sql[22], tupla_sql[23])
			
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
		
	def buscar_diario_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM diario JOIN professor ON diario.id_professor = professor.id_usuario JOIN usuario ON professor.id_usuario = usuario.id_usuario WHERE diario.id_diario = (:id_diario)''')
			self.cursor.execute(busca_tupla_sql, {"id_diario": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				diario_obj = Diario(tupla_sql[0], tupla_sql[4], tupla_sql[14], tupla_sql[5], tupla_sql[1], tupla_sql[2], tupla_sql[3])
				return diario_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar diário no banco de dados.")

	def listar_diario_por_turma(self, id_turma):
		try:
			lista_diarios_sql = ('''SELECT * FROM diario JOIN professor ON diario.id_professor = professor.id_usuario JOIN usuario ON professor.id_usuario = usuario.id_usuario JOIN turma ON diario.id_turma = turma.id_turma WHERE turma.id_turma = (:id_turma)''')
			self.cursor.execute(lista_diarios_sql, {"id_turma": id_turma})
			tuplas_diario = self.cursor.fetchall()
			diarios_obj = []
			for tupla in tuplas_diario:
				diario_obj = Diario(tupla[0], tupla[4], tupla[14], tupla[5], tupla[1], tupla[2], tupla[3])
				diarios_obj.append(diario_obj)
			return diarios_obj
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar diário por turma no banco de dados.")	
	def listar_diario_por_professor(self, id_professor):
		try:
			lista_diarios_sql = ('''SELECT * FROM diario JOIN professor ON diario.id_professor = professor.id_usuario JOIN usuario ON professor.id_usuario = usuario.id_usuario WHERE professor.id_usuario = (:id_professor)''')
			self.cursor.execute(lista_diarios_sql, {"id_professor": id_professor})
			tuplas_diario = self.cursor.fetchall()
			diarios_obj = []
			for tupla in tuplas_diario:
				diario_obj = Diario(tupla[0], tupla[4], tupla[14], tupla[5], tupla[1], tupla[2], tupla[3])
				diarios_obj.append(diario_obj)
			return diarios_obj
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar diário por professor no banco de dados.")
		
	def buscar_frequencia_por_id(self, id_busca):
		try:
			busca_tupla_sql = ('''SELECT * FROM frequencia JOIN aluno ON frequencia.id_aluno = aluno.id_usuario JOIN usuario ON aluno.id_usuario = usuario.id_usuario JOIN diario ON frequencia.id_diario = diario.id_diario WHERE frequencia.id_frequencia = (:id_frequencia)''')
			self.cursor.execute(busca_tupla_sql, {"id_frequencia": id_busca})
			tupla_sql = self.cursor.fetchone()
			if tupla_sql:
				frequencia_obj = Frequencia(tupla_sql[0], tupla_sql[2], tupla_sql[9], tupla_sql[3], tupla_sql[1])
				return frequencia_obj
			else:
				return None
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao buscar frequência no banco de dados.")
	
	def listar_frequencia_por_aluno(self, id_aluno):
		try:
			lista_frequencias_sql = ('''SELECT * FROM frequencia JOIN aluno ON frequencia.id_aluno = aluno.id_usuario JOIN usuario ON aluno.id_usuario = usuario.id_usuario JOIN diario ON frequencia.id_diario = diario.id_diario WHERE aluno.id_usuario = (:id_aluno)''')
			self.cursor.execute(lista_frequencias_sql, {"id_aluno": id_aluno})
			tuplas_frequencia = self.cursor.fetchall()
			frequencias_obj = []
			for tupla in tuplas_frequencia:
				frequencia_obj = Frequencia(tupla[0], tupla[2], tupla[9], tupla[3], tupla[1])
				frequencias_obj.append(frequencia_obj)
			return frequencias_obj
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar frequência por aluno no banco de dados.")
	
	def listar_frequencia_por_diario(self, id_diario):
		try:
			lista_frequencias_sql = ('''SELECT * FROM frequencia JOIN aluno ON frequencia.id_aluno = aluno.id_usuario JOIN usuario ON aluno.id_usuario = usuario.id_usuario JOIN diario ON frequencia.id_diario = diario.id_diario WHERE diario.id_diario = (:id_diario)''')
			self.cursor.execute(lista_frequencias_sql, {"id_diario": id_diario})
			tuplas_frequencia = self.cursor.fetchall()
			frequencias_obj = []
			for tupla in tuplas_frequencia:
				frequencia_obj = Frequencia(tupla[0], tupla[2], tupla[9], tupla[3], tupla[1])
				frequencias_obj.append(frequencia_obj)
			return frequencias_obj
		except Exception as e:
			print(f"❌ Erro no banco: {e}")
			raise ValueError("Erro ao listar frequência por diário no banco de dados.")