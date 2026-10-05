# Backend Voxum

API REST e serviços em tempo real da plataforma Voxum, implementados com Django, Django REST Framework e Django Channels.

## Requisitos

- Python 3.10 ou superior
- pip

## Desenvolvimento local

No Windows PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py runserver
```

Em Linux ou macOS, crie e ative o ambiente com `python3 -m venv .venv` e `source .venv/bin/activate`.

Por padrão, o ambiente local usa SQLite em `backend/voxum.sqlite3` e serve a API em `http://127.0.0.1:8000/`. A configuração aceita variáveis de ambiente para banco de dados e demais opções; ambientes fora de desenvolvimento devem definir, no mínimo, `SECRET_KEY` e `FERNET_KEY`.

## API e WebSockets

- Prefixo REST padrão: `/voxum/api/v1/`
- Swagger interativo: `/voxum/api/v1/docs/`
- ReDoc: `/voxum/api/v1/docs/redoc/`
- OpenAPI JSON/YAML: `/voxum/api/v1/docs.json` e `/voxum/api/v1/docs.yaml`
- Especificação estática: `backend/swagger.json`
- Prefixo de WebSockets padrão: `/voxum/ws/V1/`

O Swagger descreve métodos, parâmetros, formatos de resposta e permissões por operação.

## Testes e verificações

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

O suporte a serviços externos, incluindo a integração CIAM, requer configuração e validação próprias; a execução local não representa uma validação desses provedores.
