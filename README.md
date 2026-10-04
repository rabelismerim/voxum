# 🏛️ Voxum - Plataforma de Gestão de Assembleias Gerais de Credores (AGC)

> Plataforma Full-Stack modular para gerenciamento completo de Assembleias Gerais de Credores em tempo real, com suporte a cálculo automático de quórum, deliberações por classe de crédito e comunicação via WebSockets.

---

## 📌 Sobre o Projeto

O **Voxum** foi concebido para resolver a complexidade operacional da realização de Assembleias Gerais de Credores (AGC). A aplicação oferece controle rigoroso de presença/quórum, registro automatizado de votos segregados por classe (Trabalhista, Garantia Real, Quirografário e ME/EPP) e atualização ao vivo do andamento da reunião via comunicação bidirecional em tempo real.

---

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **Python 3.11+ / Django 5** - Arquitetura de negócios e ORM robusto.
- **Django REST Framework (DRF)** - Construção de APIs RESTful estruturadas.
- **SimpleJWT** - Autenticação baseada em tokens JWT.
- **Django Channels & Daphne** - Infraestrutura assíncrona para WebSockets.

### **Frontend**
- **Vue 3 (Composition API)** - Framework reativo para interfaces modernas.
- **Quasar Framework** - Componentes UI responsivos e padronizados.
- **Tailwind CSS** - Estilização customizada e utilitária.
- **Axios** - Cliente HTTP para comunicação com a API.

---

## 🏗️ Arquitetura do Sistema

```text
voxum/
├── backend/
│   ├── apps/
│   │   ├── authentication/  # Autenticação e gestão de permissões (JWT)
│   │   ├── creditors/       # Cadastro de credores, valores e classes de crédito
│   │   ├── meetings/        # Agendamento e gestão de status de assembleias
│   │   ├── presence/        # Controle de entrada, saída e apuração de quórum
│   │   ├── voting/          # Criação de pautas, deliberações e contagem de votos
│   │   ├── reports/         # Geração de atas e relatórios operacionais
│   │   └── websockets/      # Routing e Consumers para comunicação em tempo real
│   └── config/              # Configurações globais (settings, urls, asgi)
└── frontend/                # Aplicação Vue 3 / Quasar SPA
```

---

## 🚀 Guia de Instalação e Execução

### 📋 Pré-requisitos
- **Python 3.10+** (recomendado Python 3.11+)
- **Node.js 18+** e **npm**
- **Git**

---

### 🐍 1. Configuração do Backend (Django REST & Channels)

1. **Acesse a pasta do backend e clone o projeto:**
   ```bash
   git clone [https://github.com/rabelismerim/voxum.git](https://github.com/rabelismerim/voxum.git)
   cd voxum/backend
   ```

2. **Crie e ative o Ambiente Virtual (`venv`):**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instale as dependências:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Aplique as migrações do banco de dados:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crie um superusuário (Opcional - para acessar o Admin):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Inicie o servidor do backend:**
   ```bash
   python manage.py runserver
   ```
   > O servidor estará rodando em: `http://127.0.0.1:8000/`

---

### 💻 2. Configuração do Frontend (Vue 3 / Quasar)

Abra um **novo terminal** para rodar a aplicação frontend.

1. **Acesse a pasta do frontend:**
   ```bash
   cd voxum/frontend
   ```

2. **Instale as dependências Node.js:**
   ```bash
   npm install
   ```

3. **Execute o servidor de desenvolvimento (Vite/Quasar):**
   ```bash
   npm run dev
   ```
   > A aplicação estará acessível em: `http://localhost:5173/`

---

## 🔐 Endpoints Principais da API

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/token/` | Autenticação e geração de tokens JWT |
| `POST` | `/api/token/refresh/` | Atualização de acesso JWT |
| `GET/POST` | `/api/creditors/` | Gestão de credores e representações |
| `GET/POST` | `/api/meetings/` | Listagem e criação de assembleias |
| `GET/POST` | `/api/presence/` | Registro de presença/quórum de credores |
| `GET/POST` | `/api/voting/polls/` | Criação e encerramento de votações |
| `WS` | `/ws/meeting/{id}/` | Canal WebSocket para eventos ao vivo |

