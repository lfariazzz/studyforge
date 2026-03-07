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
| **id_localizacao** | INTEGER | PK, ON DELETE CASCADE |Identificador único do endereço. |
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
| **frequencia_minima**| REAL | NOT NULL, DEFAULT 0.75, CHECK(frequencia_minima >= 0 AND frequencia_minima <= 1) | Limite para alerta de abandono (0.0 a 1.0). |
| **indice_lacuna_maximo**| REAL | NOT NULL, DEFAULT 0.3, CHECK(indice_lacuna_maximo >= 0) | Diferença máxima permitida
| **limite_custo_demanda** | REAL | NOT NULL, DEFAULT 15000.0, CHECK(limite_custo_demanda > 0) | Teto orçamentário
| **id_municipio** | INTEGER | FK(municipio), UNIQUE | **Unicidade Multiton (1:1).** |


## 👥 2. Identidade e Acesso (Herança: Subclasse)

### Tabela: `usuario` (Tabela Pai)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, AUTOINCREMENT | Identificador base para todos os perfis. |
| **cpf** | TEXT | UNIQUE, NOT NULL | CPF do usuário. |
| **nome** | TEXT | NOT NULL | Nome completo. |
| **email** | TEXT | UNIQUE, NOT NULL | E-mail institucional ou pessoal. |
| **senha_hash** | TEXT | NOT NULL | Hash seguro da senha (BCrypt/Argon2). |
| **telefone** | TEXT | NOT NULL CHECK (length(telefone) IN (10, 11))| Número de contato (formato com DDD). |
| **data_nasc** | TEXT | NOT NULL | Data de nascimento (Formato YYYY-MM-DD). |
| **status** | TEXT | DEFAULT 'ATIVO', CHECK(status IN ('ATIVO', 'INATIVO')) | Controle de acesso ao sistema. |
| **login** | TEXT | UNIQUE, NOT NULL | Nome de usuário único para acesso. |
| **perfil** | TEXT | CHECK(perfil IN ('SEC','GES','PRO','ALU')) | Discriminador para lógica RBAC. |


### Tabela: `secretario` (Tabela filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, FK(usuario.id_usuario) | Identificador vinculado ao usuário. |
| **departamento** | TEXT | NOT NULL | Setor específico da secretaria (ex: "Financeiro", "Pedagógico"). |
| **id_municipio** | INTEGER | FK(municipio.id_municipio) | Município onde o secretário atua. |

### Tabela: `gestor` (Tabela filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, FK(usuario.id_usuario) | Identificador vinculado ao usuário. |

### Tabela: `professor` (Tabela filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, FK(usuario.id_usuario) | Identificador vinculado ao usuário. |
| **salario** | REAL | NOT NULL, CHECK(salario > 0) | Valor da remuneração mensal. |
| **titulacao** | TEXT | NOT NULL | Grau acadêmico. |
| **area_atuacao** | TEXT | NOT NULL | Disciplina ou área. |
| **registro_funcao** | TEXT | UNIQUE, NOT NULL | Matrícula ou número de registro no estado/município. |

### Tabela: `aluno` (Tabela filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, FK(usuario.id_usuario) | Identificador vinculado ao usuário. |
| **matricula** | TEXT | UNIQUE, NOT NULL | Registro de matrícula único do aluno na rede. |
| **id_turma** | INTEGER | FK(turma.id_turma), ON DELETE RESTRICT | Turma atual onde o aluno frequenta as aulas. |

## 📝 3. Registros e Avaliações

### Tabela: `nota`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_nota** | INTEGER | PK, AUTOINCREMENT | Identificador do registro de nota. |
| **disciplina** | TEXT | NOT NULL | Nome da matéria. |
| **valor** | REAL | NOT NULL, CHECK(valor >= 0 AND valor <= 10) | Valor numérico da avaliação. |
| **data** | TEXT | NOT NULL | Data da realização da avaliação a qual teve a nota atribuída. |
| **tipo** | TEXT | NOT NULL | Tipo de avaliação à qual a nota foi atribuída. |
| **id_aluno** | INTEGER | FK(aluno.id_usuario), ON DELETE RESTRICT | Aluno avaliado. |
| **id_turma** | INTEGER | FK(turma) | Contexto para cálculo de média da turma. |

### Tabela: `diario`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_diario** | INTEGER | PK, AUTOINCREMENT | Identificador do registro diário. |
| **disciplina** | TEXT | NOT NULL | Nome da matéria. |
| **data** | TEXT | NOT NULL | Data da aula (Formato ISO: YYYY-MM-DD). |
| **conteudo** | TEXT | NOT NULL | Descrição do que foi lecionado. |
| **id_professor** | INTEGER | FK(professor.id_usuario), ON DELETE RESTRICT | Docente que realizou o registro. |
| **id_turma** | INTEGER | FK(turma.id_turma), ON DELETE RESTRICT | Turma que recebeu a aula. |


### Tabela: `frequencia`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_frequencia** | INTEGER | PK, AUTOINCREMENT | Identificador da presença. |
| **status** | TEXT | NOT NULL, CHECK(status IN ('PRESENTE', 'AUSENTE')) | Indica se o aluno compareceu ou faltou. |
| **id_aluno** | INTEGER | FK(aluno.id_usuario), ON DELETE RESTRICT | Aluno em questão. |
| **id_diario** | INTEGER | FK(diario.id_diario), ON DELETE CASCADE | Vínculo com a aula registrada. |

## 🚨 4. Demandas e Monitoramento

### Tabela: `demanda` (Pai)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, AUTOINCREMENT | Identificador do chamado. |
| **descricao** | TEXT | NOT NULL | Detalhamento completo da necessidade. |
| **status** | TEXT | DEFAULT 'PENDENTE', CHECK(status IN ('PENDENTE', 'APROVADO', 'RECUSADO', 'EM_EXECUCAO', 'CONCLUIDO')) | Estado atual do processo. |
| **prioridade** | TEXT | NOT NULL, CHECK(prioridade IN ('BAIXA', 'MEDIA', 'ALTA', 'URGENTE')) | Nível de criticidade da demanda. |
| **id_solicitante** | INTEGER | FK(usuario.id_usuario) | Usuário que abriu a demanda. |
| **id_municipio** | INTEGER | FK(municipio.id_municipio) | Município responsável pela resolução. |

### Tabela: `demanda_infraestrutura` (Filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda.id_demanda) | Identificador e vínculo de herança. |
| **custo_estimado** | REAL | NOT NULL, CHECK(custo_estimado >= 0) | Valor solicitado para o reparo. |
| **id_escola** | INTEGER | FK(escola.id_escola), ON DELETE RESTRICT | Escola alvo da melhoria. |

### Tabela: `endereco_demanda_infra` (Filha)
| **id_demanda** | INTEGER | PK,FK(demanda_infraestrutura.id_demanda) ON DELETE CASCADE| Identificador da demanda à qual este endereço pertence. |
| **id_localizacao** | INTEGER | PK | Diferenciador para múltiplos endereços na mesma demanda. |
| **cep** | TEXT | NOT NULL | Código de Endereçamento Postal. |
| **rua** | TEXT | NOT NULL | Nome da rua/avenida. |
| **numero** | TEXT | NOT NULL | Número (ou "S/N"). |
| **bairro** | TEXT | NOT NULL | Bairro ou setor da obra/reparo. |

### Tabela: `demanda_pedagogica` (Filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda.id_demanda) | Identificador e vínculo de herança. |
| **indice_lacuna** | REAL | NOT NULL, CHECK(indice_lacuna >= 0 AND indice_lacuna <>= 1) | Valor da lacuna calculada. |
| **frequencia_alvo** | REAL | NOT NULL, CHECK(frequencia_alvo >= 0 AND frequencia_alvo <= 1) | Índice de frequência que disparou o alerta. |
| **id_turma** | INTEGER | FK(turma.id_turma), ON DELETE RESTRICT | Turma alvo da intervenção. |

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

---

Perdão pela confusão! Entendi agora. Você quer o conteúdo bruto para copiar e colar direto em um arquivo .md.

Aqui está o Dicionário de Dados completo, unindo todas as tabelas que criamos e a nova seção de Integridade, tudo dentro de um único bloco de código Markdown:

Markdown
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
| **id_municipio** | INTEGER | FK(municipio), ON DELETE RESTRICT | Município mantenedor. |

### Tabela: `endereco_escola`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_escola** | INTEGER | PK, FK(escola) | ID da escola vinculada. |
| **id_localizacao** | INTEGER | PK | Diferenciador de endereços para a mesma escola. |
| **cep** | TEXT | NOT NULL | Código Postal (8 dígitos). |
| **rua** | TEXT | NOT NULL | Logradouro. |
| **numero** | TEXT | NOT NULL | Número ou S/N. |
| **bairro** | TEXT | NOT NULL | Bairro da unidade. |

### Tabela: `turma`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_turma** | INTEGER | PK, AUTOINCREMENT | Identificador da turma. |
| **nome** | TEXT | NOT NULL | Identificação da sala. |
| **ano_letivo** | INTEGER | NOT NULL | Ano de vigência. |
| **turno** | TEXT | CHECK(turno IN ('MATUTINO', 'VESPERTINO', 'NOTURNO', 'INTEGRAL')) | Período das aulas. |
| **id_escola** | INTEGER | FK(escola), ON DELETE RESTRICT | Escola de lotação. |

### Tabela: `configuracoes`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_config** | INTEGER | PK, AUTOINCREMENT | Identificador da configuração. |
| **frequencia_minima**| REAL | CHECK(frequencia_minima BETWEEN 0 AND 1) | Limite para alerta de abandono. |
| **id_municipio** | INTEGER | FK(municipio), **UNIQUE** | Garante configuração única por cidade (Multiton). |

---

## 👥 2. Identidade e Acesso (Herança)

### Tabela: `usuario` (Tabela Pai)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_usuario** | INTEGER | PK, AUTOINCREMENT | ID base para perfis. |
| **cpf** | TEXT | UNIQUE, NOT NULL | CPF único do usuário. |
| **email** | TEXT | UNIQUE, NOT NULL | E-mail de acesso. |
| **senha_hash** | TEXT | NOT NULL | Hash da senha (armazenamento seguro). |
| **telefone** | TEXT | CHECK(length(telefone) IN (10,11)) | Contato com DDD. |
| **perfil** | TEXT | CHECK(perfil IN ('SEC','GES','PRO','ALU')) | Discriminador de tipo de usuário. |

### Tabelas Filhas (Especialização)
| Tabela | Chave Primária | FK de Herança | Atributos Específicos |
| :--- | :--- | :--- | :--- |
| **secretario** | `id_usuario` | `usuario` (CASCADE) | `departamento`, `id_municipio` |
| **gestor** | `id_usuario` | `usuario` (CASCADE) | - |
| **professor** | `id_usuario` | `usuario` (CASCADE) | `salario`, `titulacao`, `registro_funcao` |
| **aluno** | `id_usuario` | `usuario` (CASCADE) | `matricula`, `id_turma` |

---

## 📝 3. Registros Acadêmicos

### Tabela: `nota`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_nota** | INTEGER | PK, AUTOINCREMENT | Registro da avaliação. |
| **valor** | REAL | CHECK(valor >= 0 AND valor <= 10) | Nota obtida. |
| **id_aluno** | INTEGER | FK(aluno), ON DELETE RESTRICT | Aluno avaliado. |

### Tabela: `diario`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_diario** | INTEGER | PK, AUTOINCREMENT | Registro de aula. |
| **data** | TEXT | NOT NULL | Data da aula (YYYY-MM-DD). |
| **id_professor** | INTEGER | FK(professor), ON DELETE RESTRICT | Autor do registro. |
| **id_turma** | INTEGER | FK(turma), ON DELETE RESTRICT | Turma vinculada. |

### Tabela: `frequencia`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **status** | TEXT | CHECK(status IN ('PRESENTE', 'AUSENTE')) | Registro de presença. |
| **id_aluno** | INTEGER | FK(aluno), ON DELETE RESTRICT | Aluno em questão. |
| **id_diario** | INTEGER | FK(diario), **ON DELETE CASCADE** | Remove frequência se aula for apagada. |

---

## 🚨 4. Demandas e Monitoramento (Hierarquia)

### Tabela: `demanda` (Pai)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, AUTOINCREMENT | ID do chamado. |
| **status** | TEXT | DEFAULT 'PENDENTE' | Estado (PENDENTE, APROVADO, etc). |
| **prioridade** | TEXT | CHECK(prioridade IN ('BAIXA', 'MEDIA', 'ALTA', 'URGENTE')) | Urgência. |

### Tabela: `demanda_infraestrutura` (Filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda) | Herança (ON DELETE CASCADE). |
| **custo_estimado**| REAL | CHECK(custo_estimado >= 0) | Orçamento previsto. |
| **id_escola** | INTEGER | FK(escola), ON DELETE RESTRICT | Escola alvo da obra. |

### Tabela: `endereco_demanda_infra`
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda_infra) | ID da demanda vinculada. |
| **id_localizacao** | INTEGER | PK | Diferenciador de locais. |
| **cep/rua/bairro** | TEXT | NOT NULL | Dados de localização da demanda. |

### Tabela: `demanda_pedagogica` (Filha)
| Campo | Tipo | Restrições | Descrição |
| :--- | :--- | :--- | :--- |
| **id_demanda** | INTEGER | PK, FK(demanda) | Herança (ON DELETE CASCADE). |
| **indice_lacuna** | REAL | CHECK(indice_lacuna BETWEEN 0 AND 1) | Gap de aprendizado detectado. |
| **frequencia_alvo**| REAL | CHECK(frequencia_alvo BETWEEN 0 AND 1) | Meta de presença esperada. |

---

## 🔗 5. Relacionamentos Muitos-para-Muitos (N:N)

### Tabela: `professor_escola_alocado`
* **PK Composta:** `(id_professor, id_escola)`
* **FKs:** `professor` (CASCADE), `escola` (RESTRICT).

### Tabela: `professor_turma_alocado`
* **PK Composta:** `(id_professor, id_turma)`
* **FKs:** `professor` (CASCADE), `turma` (RESTRICT).

---

## 🛡️ 6. Políticas de Integridade Referencial

### 6.1. Deleção em Cascata (`ON DELETE CASCADE`)
* **Herança de Usuário:** Ao excluir um registro na tabela `usuario`, os perfis em `gestor`, `secretario`, `professor` ou `aluno` são removidos automaticamente.
* **Especialização de Demandas:** Excluir uma `demanda` genérica remove seus detalhes em `demanda_infraestrutura` ou `demanda_pedagogica`.
* **Histórico de Localização:** A remoção de uma escola ou demanda de infraestrutura limpa seus endereços vinculados automaticamente.
* **Diário e Presença:** Apagar um registro de aula (`diario`) elimina todas as listas de `frequencia` vinculadas a essa aula.

### 6.2. Restrição de Deleção (`ON DELETE RESTRICT`)
* **Segurança Municipal:** Bloqueia a exclusão de um `municipio` se houver escolas ou demandas ativas vinculadas a ele.
* **Histórico Acadêmico:** Bloqueia a exclusão de um `aluno` se existirem registros de `nota`, preservando o histórico escolar oficial.
* **Vínculo de Turma:** Impede a exclusão de uma `turma` se houver alunos matriculados ou professores alocados nela.
* **Responsabilidade Docente:** Impede a exclusão de um `professor` se ele possuir aulas registradas em seu nome no `diario`.

### 6.3. Validação de Dados e Segurança
* **Criptografia:** O campo `usuario.senha_hash` deve conter apenas hashes gerados por algoritmos seguros. Texto puro é proibido.
* **Consistência Numérica:** `CHECK constraints` impedem notas fora do intervalo [0-10] e índices (lacuna, frequência, config) fora de [0-1].
* **Lógica Multiton:** A restrição `UNIQUE` em `configuracoes.id_municipio` garante que cada cidade tenha exatamente uma regra de negócio ativa.