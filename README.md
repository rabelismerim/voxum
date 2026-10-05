# Voxum

Plataforma web para apoiar a gestão de Assembleias Gerais de Credores (AGCs), desde o cadastro e credenciamento de participantes até a condução de votações e a consulta de resultados. O Voxum é o nome do produto; AGC continua sendo a sigla do domínio de negócio.

O repositório contém uma API em Django e Django REST Framework e uma aplicação web em Vue. A interface oferece fluxos de gestão de assembleias, votação e acesso de convidados, com atualizações em tempo real por WebSocket.

## Funcionalidades

- Cadastro e consulta de assembleias, credores, representantes, convidados e localidades.
- Credenciamento e acompanhamento de presença.
- Configuração e condução de pautas e votações, incluindo registro de votos por credor ou representante.
- Consulta de resultados e geração de relatórios.
- Interface de gestão e páginas de acesso para convidados.
- Atualizações de listas e eventos da assembleia em tempo real.
- Documentação interativa da API.

## Tecnologias

| Área | Tecnologias principais |
| --- | --- |
| Backend | Python, Django, Django REST Framework, Django Channels, Daphne |
| Processamento e dados | SQLite para desenvolvimento local; Redis e Celery para configurações de execução não locais |
| Frontend | Vue 3, Vite, Quasar, UnoCSS, Vue Router, Axios |

As dependências completas e as versões declaradas estão em [backend/requirements.txt](./backend/requirements.txt) e [frontend/package.json](./frontend/package.json).

## Estrutura do repositório

```text
.
├── backend/
│   ├── apps/
│   │   ├── creditor/       # Credores e representantes
│   │   ├── guest/          # Convidados e acesso externo
│   │   ├── location/       # Localidades
│   │   ├── meetings/       # Assembleias, classes e credenciamento
│   │   ├── presence/       # Registro e consulta de presença
│   │   ├── recovering/     # Recuperação de acesso
│   │   ├── report/         # Relatórios de assembleia e votação
│   │   ├── voting/         # Pautas, votos e resultados
│   │   ├── voxum_base/     # Funcionalidades compartilhadas e processamento
│   │   ├── web_sockets/    # Comunicação em tempo real
│   │   └── works/          # Funcionalidades auxiliares
│   ├── config/             # Configurações Django, URLs e ASGI
│   ├── core/               # Usuários e permissões
│   ├── manage.py
│   └── swagger.json        # Snapshot da especificação da API
└── frontend/
    ├── src/pages/          # Páginas de gestão, assembleia, votação e convidado
    ├── src/services/       # Integração HTTP com a API
    └── vite.config.js
```

## Requisitos

- Python 3.10 ou superior.
- Node.js 18 ou superior e npm.
- Git.

O backend também declara `pywin32` entre as dependências. O caminho de instalação descrito abaixo é destinado ao Windows; em outros sistemas operacionais, essa dependência específica pode exigir tratamento conforme o ambiente.

## Execução local

### 1. Backend

No Windows, abra o PowerShell na raiz do repositório:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py create_voxum_groups
python manage.py createsuperuser
python manage.py runserver
```

Crie o usuário e a senha quando `createsuperuser` solicitar os dados. Use essas credenciais no formulário de entrada da página inicial local; não existe senha padrão no projeto.

Se a política do PowerShell impedir a ativação do ambiente virtual, consulte a documentação do Python/Windows ou execute os comandos usando o interpretador em `backend\.venv\Scripts\python.exe`.

Por padrão, o modo de desenvolvimento usa SQLite em `backend/voxum.sqlite3`, cache local e camada de canais em memória. As tarefas Celery são executadas em modo eager nesse ambiente; portanto, a configuração local básica não exige iniciar Redis ou um worker Celery. O servidor da API fica em `http://127.0.0.1:8000`.

### 2. Frontend

Em outro terminal, na raiz do repositório:

```powershell
cd frontend
npm install
npm run dev:local
```

O Vite informa no terminal o endereço local disponível. A base de navegação configurada para o frontend é `/voxum/`; use o endereço exibido pelo Vite com esse caminho quando necessário. O servidor local está configurado para HTTPS por padrão; para usar HTTP, defina `VITE_HTTPS=false` no ambiente do Vite.

O arquivo [frontend/.env](./frontend/.env) contém os padrões locais. No modo `dev:local`, o Vite encaminha as rotas `/voxum/api` e `/voxum/ws` para o backend em `http://127.0.0.1:8000`, evitando chamadas entre origens diferentes. Se o backend estiver em outro endereço, ajuste o destino do proxy em [frontend/vite.config.js](./frontend/vite.config.js). Mantenha `VITE_API_HOST`, `VITE_SOCKET_HOST` e `VITE_SOCKET_PORT` vazios para usar esse proxy. Não coloque tokens ou credenciais reais nesse arquivo nem os publique no repositório.

### 3. Verificações

Execute os comandos a partir do diretório indicado:

```powershell
# backend/
python manage.py check
python manage.py test apps.voxum_base.tests
```

```powershell
# frontend/
npm run lint
npm run build
```

## API e comunicação em tempo real

A base local da API REST é:

```text
http://127.0.0.1:8000/voxum/api/v1/
```

Os principais grupos de rotas são:

| Recurso | Prefixo |
| --- | --- |
| Assembleias | `meeting/` |
| Credores | `creditor/` |
| Convidados | `guest/` |
| Presença | `presence/` |
| Votações | `voting/` |
| Relatórios | `report/` |
| Localidades | `location/` |
| Usuários | `core/user/` |
| Processamento de arquivos | `process_file/` |
| Endpoints auxiliares de sockets | `sockets/` |

As rotas completas, métodos HTTP, parâmetros e formatos de resposta podem ser consultados na documentação gerada pelo backend:

- Swagger UI: `http://127.0.0.1:8000/voxum/api/v1/docs/`
- ReDoc: `http://127.0.0.1:8000/voxum/api/v1/docs/redoc/`
- Esquema JSON: `http://127.0.0.1:8000/voxum/api/v1/docs.json`
- Esquema YAML: `http://127.0.0.1:8000/voxum/api/v1/docs.yaml`

O arquivo [backend/swagger.json](./backend/swagger.json) também está incluído no repositório como snapshot da especificação.

Os WebSockets são servidos pelo backend ASGI no prefixo `/voxum/ws/V1/`. Os caminhos implementados incluem:

```text
/voxum/ws/V1/meetings/<meeting_id>/
/voxum/ws/V1/guest/meetings/<meeting_id>/
/voxum/ws/V1/general/
```

O `meeting_id` deve ser o UUID da assembleia. A autenticação e as permissões dependem da configuração do backend e da rota utilizada.

## Configuração

As configurações Django são definidas em `backend/config/` e podem ser parametrizadas por variáveis de ambiente. Algumas configurações também leem um arquivo `.env` local; como a leitura varia conforme a configuração, use variáveis de ambiente para garantir que todos os valores sejam aplicados. Entre as variáveis usadas estão:

| Variável | Finalidade |
| --- | --- |
| `ENVIRONMENT` | Seleciona o ambiente; `development` é o padrão local |
| `DEBUG` | Habilita ou desabilita o modo de depuração |
| `SECRET_KEY` | Chave secreta do Django; obrigatória fora do desenvolvimento local |
| `APP_NAME` | Prefixo da aplicação; o padrão é `voxum` |
| `BASE_API_URL` | Prefixo das rotas REST; o padrão é `voxum/api/v1/` |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Configuração do banco de dados |
| `REDIS_URL` | Conexão usada por canais, cache e broker em ambientes não locais |
| `FERNET_KEY` | Chave de criptografia obrigatória fora do desenvolvimento local |
| `ENABLE_TOKEN` | Controla o uso de autenticação por token nos WebSockets |
| `BASE_URL_CIAM` e variáveis `MSAL_CIAM_*` | Configuração da integração opcional de identidade CIAM |

Os padrões de desenvolvimento não são apropriados para produção. Antes de implantar, configure segredos e serviços externos fora do código-fonte, revise hosts, banco de dados, cache, Redis, filas, HTTPS e permissões de acesso. Os fluxos que enviam convites ou dependem do CIAM também requerem as credenciais e os serviços correspondentes.

## Autenticação e permissões

O backend registra autenticação por token e por sessão. No modo não local, as permissões padrão exigem usuário autenticado e aplicam a regra de acesso definida pelo projeto; operações específicas podem ter permissões próprias. A interface também controla a navegação com base no estado e nas permissões do usuário. Não há credenciais de demonstração incluídas neste repositório.
