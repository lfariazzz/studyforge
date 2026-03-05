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
| **uf** | TEXT | NOT NULL, CHECK(length(uf)=2) | Sigla do estado (ex: "CE"). |
| **verba_disponivel**| REAL | DEFAULT 0.0 | Saldo total para demandas de infraestrutura. |

### Tabela: `escola`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_escola** | INTEGER | PK, AUTOINCREMENT | Identificador da unidade. |
| **nome** | TEXT | NOT NULL | Nome da instituição escolar. |
| **verba_disponivel** | REAL | DEFAULT 0.0 | Saldo total para demandas escolares. |
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
| **indice_lacuna_maximo**| REAL | NOT NULL, DEFAULT 0.3, CHECK(indice_lacuna_maximo >= 0) | Diferença máxima permitida
| **limite_custo_demanda** | REAL | NOT NULL, DEFAULT 15000.0, CHECK(limite_custo_demanda > 0) | Teto orçamentário

## 👥 2. Identidade e Acesso (Herança: Subclasse)

### Tabela: `usuario` (Tabela Pai)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, AUTOINCREMENT | Identificador base para todos os perfis. |
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



---

---

## 📝 4. Registros e Avaliações

### Tabela: `nota`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_nota** | INTEGER | PK | Identificador do registro de nota. |
| **valor** | REAL | CHECK(valor >= 0 AND valor <= 10) | Valor numérico da avaliação. |
| **id_aluno** | INTEGER | FK(aluno) | Aluno avaliado. |
| **id_turma** | INTEGER | FK(turma) | Contexto para cálculo de média da turma. |

### Tabela: `diario`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_diario** | INTEGER | PK | Identificador do registro diário. |
| **data** | TEXT | NOT NULL | Data da aula (Formato ISO: YYYY-MM-DD). |
| **conteudo** | TEXT | NOT NULL | Descrição do que foi lecionado. |
| **id_professor** | INTEGER | FK(professor) | Docente que realizou o registro. |
| **id_turma** | INTEGER | FK(turma) | Turma que recebeu a aula. |

### Tabela: `frequencia`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_frequencia** | INTEGER | PK | Identificador da presença. |
| **status** | INTEGER | CHECK(status IN (0,1)) | 1 para Presente, 0 para Ausente. |
| **id_aluno** | INTEGER | FK(aluno) | Aluno em questão. |
| **id_diario** | INTEGER | FK(diario) | Vínculo com a aula registrada. |

---

## 🚨 5. Demandas e Monitoramento

### Tabela: `demanda` (Pai)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK | Identificador do chamado. |
| **status** | TEXT | DEFAULT 'PENDENTE' | PENDENTE, APROVADO, RECUSADO. |
| **id_solicitante** | INTEGER | FK(usuario) | Usuário que abriu a demanda. |
| **id_municipio** | INTEGER | FK(municipio) | Município responsável pela resolução. |

### Tabela: `demanda_infraestrutura` (Filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda) | Identificador e vínculo de herança. |
| **custo_estimado** | REAL | NOT NULL | Valor solicitado para o reparo. |
| **id_escola** | INTEGER | FK(escola) | Escola alvo da melhoria. |

### Tabela: `demanda_pedagogica` (Filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda) | Identificador e vínculo de herança. |
| **indice_lacuna** | REAL | NOT NULL | Valor da lacuna calculada pela IA. |
| **id_turma** | INTEGER | FK(turma) | Turma alvo da intervenção. |

---

## 🔗 6. Relacionamentos Muitos-para-Muitos (N:N)

### Tabela: `professor_escola_alocado`
Associação entre docentes e unidades escolares.
| Campo | Tipo | Restrições |
| :--- | :--- | :--- |
| **id_professor** | INTEGER | PK, FK(professor.id_usuario) |
| **id_escola** | INTEGER | PK, FK(escola.id_escola) |

### Tabela: `professor_turma_alocado`
Associação entre docentes e turmas lecionadas.
| Campo | Tipo | Restrições |
| :--- | :--- | :--- |
| **id_professor** | INTEGER | PK, FK(professor.id_usuario) |
| **id_turma** | INTEGER | PK, FK(turma.id_turma) |

---

## 🛡️ 7. Políticas de Integridade Referencial

1.  **Segurança de Deleção:**
    * `municipio`: **ON DELETE RESTRICT**. Impede a deleção de cidades com dados ativos.
    * `usuario`: **ON DELETE CASCADE**. Remove perfis especializados ao apagar a conta base.
    * `aluno`: **ON DELETE CASCADE**. Limpa notas e frequências se o aluno for removido.
2.  **Segurança de Dados:**
    * `usuario.senha_hash`: Armazenamento obrigatório em formato HASH. Texto puro proibido.
3.  **Restrição Multiton:**
    * `configuracoes.id_municipio`: Deve ser `UNIQUE` para garantir uma única regra por cidade.