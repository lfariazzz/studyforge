# 🗄️ Dicionário de Dados - StudyForge

Este documento descreve a estrutura técnica do banco de dados SQLite do projeto StudyForge, detalhando tipos de dados, restrições e políticas de integridade.

---

## 🗺️ Referências Visuais
* **MER (Conceitual):** `studyforge-poo/docs/diagrams/mer_conceitual.png`
* **DER (Lógico):** `studyforge-poo/docs/diagrams/der_conceitual.png`
* **Mapeamento (Relacional):** `studyforge-poo/docs/diagrams/mapeamento_relacional.png`

---

## 🏛️ 1. Núcleo Institucional (Multiton & Espaços Estruturais)

### Tabela: `municipio`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_municipio** | INTEGER | PK, AUTOINCREMENT | Identificador único da instância municipal. |
| **nome** | TEXT | NOT NULL | Nome oficial da cidade. |

| **uf(->estado)** | TEXT | NOT NULL, CHECK(length(uf)=2) | Sigla do estado (ex: "CE"). |
| **verba_disponivel (->verba_disponivel_municipio)**| REAL | DEFAULT 0.0 | Saldo total para demandas de infraestrutura. |
**(media_frequencia)**
**(lacuna_maxima_permitida)**
**(nota_de_corte)**


### Tabela: `escola`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_escola** | INTEGER | PK, AUTOINCREMENT | Identificador da unidade. |
| **nome** | TEXT | NOT NULL | Nome da instituição escolar. |
| **verba_disponivel(->verba_disponivel_escola)** | REAL | DEFAULT 0.0 | Saldo total para demandas escolares. |
| **id_municipio** | INTEGER | FK(municipio) | Município mantenedor. |
| **id_gestor** | INTEGER | FK(gestor) | Gestor responsável. |

### Tabela: `endereco_escola`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_escola** | INTEGER | PK,FK(escola.id_escola) | Identificador único da escola dona do endereço. |
| **id_localizacao** | INTEGER | PK |Identificador único do endereço. |
| **cep** | TEXT | NOT NULL | Código de Endereçamento Postal. |
| **rua** | TEXT | NOT NULL | Nome da rua/avenida. |
| **numero** | TEXT | NOT NULL | Número (ou "S/N"). |
| **bairro** | TEXT | NOT NULL | Bairro da unidade. |

### Tabela: `turma`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_turma** | INTEGER | PK, AUTOINCREMENT | Identificador da turma. |
| **nome** | TEXT | NOT NULL | Identificação da sala. |
| **ano_letivo** | INTEGER | NOT NULL | Ano de vigência dos registros. |
| **turno** | TEXT | NOT NULL, CHECK(turno IN ('MATUTINO', 'VESPERTINO', 'NOTURNO', 'INTEGRAL')) | Período das aulas. |
| **capacidade_maxima** | INTEGER | NOT NULL | Quantidade máxima de alunos suportada. |
| **id_escola** | INTEGER | FK(escola.id_escola), ON DELETE RESTRICT | Escola de lotação da turma. |


### Tabela: `configuracoes`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_config** | INTEGER | PK, AUTOINCREMENT | Identificador da configuração. |
| **id_municipio** | INTEGER | FK(municipio), UNIQUE | **Unicidade Multiton (1:1).** |
| **frequencia_minima**| REAL | NOT NULL, DEFAULT 0.75, CHECK(frequencia_minima >= 0 AND frequencia_minima <= 1) | Limite para alerta de abandono (0.0 a 1.0). |
| **indice_lacuna_minimo**| REAL | NOT NULL, DEFAULT 0.3, CHECK(indice_lacuna_maximo >= 0) | Diferença máxima permitida
| **limite_custo_demanda** | REAL | NOT NULL, DEFAULT 15000.0, CHECK(limite_custo_demanda > 0) | Teto orçamentário

## 👥 2. Identidade e Acesso (Herança: Subclasse)

### Tabela: `usuario` (Tabela Pai)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario**(renomear no python) | INTEGER | PK, AUTOINCREMENT | Identificador base para todos os perfis. |
| **cpf** | TEXT | UNIQUE, NOT NULL | CPF do usuário. |
| **nome** | TEXT | NOT NULL | Nome completo. |
| **email** | TEXT | UNIQUE, NOT NULL | E-mail institucional ou pessoal. |
| **senha_hash** | TEXT | NOT NULL | Hash seguro da senha (BCrypt/Argon2). |
| **telefone** | TEXT | NOT NULL | Número de contato (formato com DDD). |
| **data_nasc** | TEXT | NOT NULL | Data de nascimento (Formato YYYY-MM-DD). |
| **status** | TEXT | DEFAULT 'ATIVO', CHECK(status IN ('ATIVO', 'INATIVO')) | Controle de acesso ao sistema. |
| **login** | TEXT | UNIQUE, NOT NULL | Nome de usuário único para acesso. |
| **perfil** | TEXT | CHECK(perfil IN ('SEC','GES','PRO','ALU')) | Discriminador para lógica RBAC. |


### Tabela: `secretario` (Tabela filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, FK(usuario.id_usuario) | Identificador vinculado ao usuário. |
| **id_municipio** | INTEGER | FK(municipio.id_municipio) | Município onde o secretário atua. |
| **departamento** | TEXT | NOT NULL | Setor específico da secretaria (ex: "Financeiro", "Pedagógico"). |

### Tabela: `gestor` (Tabela filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, FK(usuario.id_usuario) | Identificador vinculado ao usuário. |

### Tabela: `professor` (Tabela filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, FK(usuario.id_usuario) | Identificador vinculado ao usuário. |
| **salario** | REAL | NOT NULL, CHECK(salario > 0) | SValor da remuneração mensal. |
| **titulacao** | TEXT | NOT NULL | Grau acadêmico. |
| **area_atuacao** | TEXT | NOT NULL | Disciplina ou área. |
| **registro_funcao** | TEXT | UNIQUE, NOT NULL | Matrícula ou número de registro no estado/município. |

### Tabela: `aluno` (Tabela filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, FK(usuario.id_usuario) | Identificador vinculado ao usuário. |
| **id_turma** | INTEGER | FK(turma.id_turma), ON DELETE RESTRICT | Turma atual onde o aluno frequenta as aulas. |
| **matricula** | TEXT | UNIQUE, NOT NULL | Registro de matrícula único do aluno na rede. |

## 📝 3. Registros e Avaliações

### Tabela: `nota`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_nota** | INTEGER | PK, AUTOINCREMENT | Identificador do registro de nota. |
| **id_aluno** | INTEGER | FK(aluno.id_usuario), ON DELETE RESTRICT | Aluno avaliado. |
| **id_turma** | INTEGER | FK(turma) | Contexto para cálculo de média da turma. |
| **disciplina** | TEXT | NOT NULL | Nome da matéria. |
| **valor** | REAL | NOT NULL, CHECK(valor >= 0 AND valor <= 10) | Valor numérico da avaliação. |
| **data** | TEXT | NOT NULL | Data da realização da avaliação a qual teve a nota atribuída. |
| **tipo** | TEXT | NOT NULL | Tipo de avaliação à qual a nota foi atribuída. |

### Tabela: `diario`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_diario** | INTEGER | PK, AUTOINCREMENT | Identificador do registro diário. |
| **id_professor** | INTEGER | FK(professor.id_usuario), ON DELETE RESTRICT | Docente que realizou o registro. |
| **id_turma** | INTEGER | FK(turma.id_turma), ON DELETE RESTRICT | Turma que recebeu a aula. |
| **disciplina** | TEXT | NOT NULL | Nome da matéria. |
| **data** | TEXT | NOT NULL | Data da aula (Formato ISO: YYYY-MM-DD). |
| **conteudo** | TEXT | NOT NULL | Descrição do que foi lecionado. |


### Tabela: `frequencia`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_frequencia** | INTEGER | PK, AUTOINCREMENT | Identificador da presença. |
| **id_aluno** | INTEGER | FK(aluno.id_usuario), ON DELETE RESTRICT | Aluno em questão. |
| **id_diario** | INTEGER | FK(diario.id_diario), ON DELETE CASCADE | Vínculo com a aula registrada. |
| **status** | TEXT | NOT NULL, CHECK(status IN ('PRESENTE', 'AUSENTE')) | Indica se o aluno compareceu ou faltou. |

## 🚨 4. Demandas e Monitoramento

### Tabela: `demanda` (Pai)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, AUTOINCREMENT | Identificador do chamado. |
| **id_solicitante** | INTEGER | FK(usuario.id_usuario) | Usuário que abriu a demanda. |
| **id_municipio** | INTEGER | FK(municipio.id_municipio) | Município responsável pela resolução. |
| **descricao** | TEXT | NOT NULL | Detalhamento completo da necessidade. |
| **status** | TEXT | DEFAULT 'PENDENTE', CHECK(status IN ('PENDENTE', 'APROVADO', 'RECUSADO', 'EM_EXECUCAO', 'CONCLUIDO')) | Estado atual do processo. |
| **prioridade** | TEXT | NOT NULL, CHECK(prioridade IN ('BAIXA', 'MEDIA', 'ALTA', 'URGENTE')) | Nível de criticidade da demanda. |

### Tabela: `demanda_infraestrutura` (Filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda.id_demanda) | Identificador e vínculo de herança. |
| **id_escola** | INTEGER | FK(escola.id_escola), ON DELETE RESTRICT | Escola alvo da melhoria. |
| **custo_estimado** | REAL | NOT NULL, CHECK(custo_estimado >= 0) | Valor solicitado para o reparo. |

### Tabela: `endereco_demanda_infra` (Filha)
| **id_demanda** | INTEGER | PK,FK(demanda_infraestrutura.id_demanda) | Identificador da demanda à qual este endereço pertence. |
| **id_localizacao** | INTEGER | PK | Diferenciador para múltiplos endereços na mesma demanda. |
| **cep** | TEXT | NOT NULL | Código de Endereçamento Postal. |
| **rua** | TEXT | NOT NULL | Nome da rua/avenida. |
| **numero** | TEXT | NOT NULL | Número (ou "S/N"). |
| **bairro** | TEXT | NOT NULL | Bairro ou setor da obra/reparo. |



### Tabela: `demanda_pedagogica` (Filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda.id_demanda) | Identificador e vínculo de herança. |
| **id_turma** | INTEGER | FK(turma.id_turma), ON DELETE RESTRICT | Turma alvo da intervenção. |
| **indice_lacuna** | REAL | NOT NULL, CHECK(indice_lacuna >= 0) | Valor da lacuna calculada. |
| **frequencia_alvo** | REAL | NOT NULL, CHECK(frequencia_alvo >= 0 AND frequencia_alvo <= 1) | Índice de frequência que disparou o alerta. |

## 🔗 5. Relacionamentos Muitos-para-Muitos (N:N)

### Tabela: `professor_escola_alocado`
| Campo | Tipo | Restrições |
| :--- | :--- | :--- |
| **id_professor** | INTEGER | PK, FK(professor.id_usuario) |
| **id_escola** | INTEGER | PK, FK(escola.id_escola) |

### Tabela: `professor_turma_alocado`
| Campo | Tipo | Restrições |
| :--- | :--- | :--- |
| **id_professor** | INTEGER | PK, FK(professor.id_usuario) |
| **id_turma** | INTEGER | PK, FK(turma.id_turma) |

## 🛡️ 6. Políticas de Integridade Referencial

### 1. Controle de Deleção (Restrições de Segurança)

* **Proteção Institucional (`ON DELETE RESTRICT`):** Impede a exclusão de registros que possuam dependentes ativos, garantindo que o histórico do sistema não seja corrompido.
    * `municipio`: Bloqueia a remoção se houver escolas ou secretários vinculados.
    * `escola`: Bloqueia a remoção se houver turmas ou demandas de infraestrutura associadas.
    * `turma`: Impede a deleção caso existam alunos matriculados, diários de aula registrados ou demandas pedagógicas ativas.
    * `usuario`: Bloqueia a remoção de Alunos ou Professores que possuam registros históricos de Notas ou Diários vinculados.

* **Limpeza Automática (`ON DELETE CASCADE`):** Garante a higienização do banco ao remover registros dependentes de forma automática.
    * `frequencia`: Caso um registro de `diario` (aula) seja removido, todos os registros de presença vinculados a essa aula específica são apagados instantaneamente.
    * **Herança (Tabelas Filhas):** A exclusão de um `id_usuario` na tabela pai (`usuario`) propaga a exclusão imediata e obrigatória nas tabelas de especialização (`secretario`, `gestor`, `professor`, `aluno`).

### 2. Unicidade e Padrão Multiton

* **Garantia Multiton:** A restrição `UNIQUE` no campo `configuracoes.id_municipio` assegura a integridade do padrão de projeto Multiton no banco de dados, impedindo a existência de mais de um conjunto de regras de negócio para o mesmo município.
* **Identidades Únicas:** Campos como `cpf`, `email`, `login`, `matricula` e `registro_funcao` possuem restrição `UNIQUE`, inviabilizando a duplicidade de perfis ou registros funcionais na rede StudyForge.

### 3. Integridade de Herança

* As tabelas filhas (`secretario`, `gestor`, `professor`, `aluno`) utilizam o `id_usuario` como Chave Primária e Chave Estrangeira simultaneamente. O sistema impõe que qualquer ID nessas tabelas deve obrigatoriamente existir na tabela pai `usuario`.

### 4. Validação de Domínio

* **Intervalos Numéricos:** O sistema valida em nível de banco de dados que as notas residam no intervalo $0 \leq n \leq 10$ e que percentuais de frequência (metas) estejam entre $0.0$ e $1.0$.
* **Integridade de Estados:** Atributos de seleção como `status` (ATIVO/INATIVO), `prioridade` (BAIXA a URGENTE) e `turno` possuem listas fechadas de valores (Enums), impedindo a inserção de dados inconsistentes por erro de digitação no backend.

### 5. Segurança de Credenciais

* O campo `usuario.senha_hash` possui obrigatoriedade de preenchimento e proíbe o armazenamento de texto puro. O banco exige que a aplicação realize o processo de hashing antes da tentativa de persistência.