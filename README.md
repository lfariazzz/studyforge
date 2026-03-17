# 🏛️ StudyForge: Gestão Educacional Inteligente

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

O **StudyForge** é uma plataforma de gestão educacional desenvolvida para otimizar os fluxos administrativos e pedagógicos de municípios. O sistema utiliza o paradigma de **Orientação a Objetos** para gerenciar hierarquias complexas de usuários e automação de demandas críticas.
---
## 🚀 Como Executar

Siga estas etapas em ordem para garantir que o banco de dados e as dependências estejam prontos.

### 1. Inicializar o Banco de Dados
O primeiro passo é criar a estrutura do banco de dados SQLite. Execute o script de inicialização utilizando o modo de módulo do Python:

```bash
python -m src.database.init_db
```

### 2. Instalar Dependências
A interface de linha de comando deste projeto utiliza a biblioteca Typer. Instale-a via pip:
```bash
pip install typer
```
### 3. Executar a CLI
Com o banco inicializado e as bibliotecas instaladas, você pode rodar o programa principal.
Importante: Sempre execute o comando a partir da raiz do projeto (/studyforge) para que os imports internos funcionem corretamente:
```bash
python -m src.main
```
---

## 🚀 Principais Funcionalidades

* **Gestão de Demandas:** Fluxos distintos para infraestrutura (licitações) e pedagogia (reforço escolar).
* **Monitoramento de Evasão:** Geração automática de alertas baseada em frequência escolar.
* **Auditoria Nativa:** Rastreamento de alterações sensíveis via Mixins.
* **Comunicação Crítica:** Sistema de notificações em tempo real para urgências municipais.

---

## 🛠️ Tecnologias e Padrões

* **Linguagem:** Python 3.10+
* **Padrões de Projeto (GoF):** Factory Method, Observer, Singleton e Repository.
* **Arquitetura:** Baseada nos princípios **SOLID** para alta manutenibilidade.

---

## 📖 Documentação Completa

Para detalhes sobre regras de negócio, diagramas UML e justificativas arquiteturais, acesse nossa Wiki oficial:

👉 **[Wiki do StudyForge](https://github.com/lfariazzz/StudyForge-POO/wiki)**

---

# StudyForge 🛠️

Este projeto é uma ferramenta de linha de comando (CLI) desenvolvida em Python para gerenciamento de estudos. Siga os passos abaixo para configurar o ambiente e rodar a aplicação corretamente.

## 📋 Pré-requisitos

Antes de começar, você precisa ter o **Python 3.10 ou superior** instalado em sua máquina.

## 👥 Equipe de Desenvolvimento

| Integrante | Papel no Projeto | Usuário GitHub |
| :--- | :--- | :--- |
| **Levi Farias** | Líder Técnico / Documentador / Desenvolver Backend | [@lfariazzz](https://github.com/lfariazzz) |
| **Henrique Coimbra** | Funções à definir | [@HenriqueCoimbra12](https://github.com/HenriqueCoimbra12) |
| **André Wesley** | Funções à definir | [@andre-wesleyy](https://github.com/andre-wesleyy) |
| **Malaquias de Oliveira** | Funções à definir | [@malaquiaso841-cyber](https://github.com/malaquiaso841-cyber) |
