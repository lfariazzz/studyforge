import sqlite3
import os

class RepositorioGeral:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.connect = sqlite3.connect("data/studyforge.db")
        self.cursor = self.connect.cursor()
        self._criar_tabelas()

    def _criar_tabelas(self):
        codigo_SQL =    ('''
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
	"tipo"	TEXT CHECK("tipo" IN ('SECRETÁRIO', 'GESTOR', 'PROFESSOR', 'ALUNO'))
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
    "tipo" TEXT CHECK("tipo" IN('INFRAESTRUTURA', 'PEDAGÓGICA'),
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
                         
    CREATE TABLE IF NOT EXISTS endereco_demanda_infra(
	"id_demanda"	INTEGER,
	"id_localizacao"	INTEGER,
	"cep"	TEXT NOT NULL,
	"rua"	TEXT NOT NULL,
	"numero"	TEXT NOT NULL,
	"bairro"	TEXT NOT NULL,
	PRIMARY KEY("id_demanda","id_localizacao"),
	FOREIGN KEY("id_demanda") REFERENCES "demanda"("id_demanda") ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS demanda_pedagogica(
	"id_demanda"	INTEGER PRIMARY KEY,
	"indice_lacuna"	REAL NOT NULL CHECK("indice_lacuna" >= 0.0 AND "indice_lacuna" <= 1.0),
	"frequencia_alvo"	REAL NOT NULL CHECK("frequencia_alvo" <= 1.0 AND "frequencia_alvo" >= 0),
	"id_turma"	INTEGER,
	FOREIGN KEY("id_demanda") REFERENCES "demanda"("id_demanda"),
	FOREIGN KEY("id_turma") REFERENCES "turma"("id_turma") ON DELETE RESTRICT
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
	"id_diario"	INTEGER,
	"disciplina"	TEXT NOT NULL,
	"data"	TEXT NOT NULL,
	"conteudo"	TEXT NOT NULL,
	"id_professor"	INTEGER,
	"id_turma"	INTEGER,
	PRIMARY KEY("id_diario" AUTOINCREMENT),
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

    def salvar_municipio(self, municipio_obj):
        dados = municipio_obj.to_dict()
        codigo_SQL = ('''INSERT INTO municipio (nome, uf, verba_disponivel) VALUES (?,?,?)''')
        self.cursor.execute(codigo_SQL, (dados["nome"], dados["estado"], dados["verba_disponivel_municipio"]))
        self.connect.commit()

