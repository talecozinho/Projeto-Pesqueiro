# 🎣 Pesqueiro Manager - Sistema de Gestão de Consumo

## Status da Aplicação
| Módulo | Status | Descrição |
| :--- | :--- | :--- |
| **Backend (API)** | ✅ Funcional | FastAPI com lógica de consumo e cálculo. |
| **Banco de Dados** | ✅ Persistente | SQLite + SQLAlchemy. |
| **Frontend (Web)** | ✅ Funcional | Interface simples em HTML/JS para simular o uso. |
| **Testes** | ✅ OK | Testes unitários (Pytest) validando o fluxo de consumo. |
| **CI/CD** | ⚙️ Configurado | Pipeline configurada para o CircleCI. |

---

## 💻 1. Arquitetura e Tecnologia (O Core do Projeto)

O sistema segue o modelo de camadas para garantir as boas práticas de engenharia:
* **API Framework:** **FastAPI** (Python)
* **Gerenciamento de Dependências:** **Poetry**
* **ORM:** **SQLAlchemy** (para gestão das tabelas Clientes, Comandas e Itens)
* **CI/CD:** **CircleCI** (configurado para rodar testes e linting no `.circleci/config.yml`)

### Regras de Negócio Testadas:
* Bloqueio de cadastro com CPF duplicado.
* Validação de Comanda Aberta antes de lançar consumo.
* Cálculo automático e acumulação do `valor_total` da comanda.

---

## 🚀 2. Instalação e Execução

### Pré-requisitos
- Python 3.10+
- Poetry

### Comandos de Início
1. Instalar as dependências do `pyproject.toml`:
   ```bash
   poetry install
