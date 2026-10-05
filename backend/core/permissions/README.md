# Módulo Core.Permissions

## Descrição

O módulo `core.permissions` é responsável por gerenciar as permissões de acesso dentro do sistema. Ele fornece funcionalidades para definir e verificar permissões de usuários em diferentes partes do sistema.

### Modelos

- **Permission**: Representa uma permissão específica que pode ser atribuída a um usuário ou grupo.

  - **Campos**:
    - `name`: (`CharField`) Nome da permissão.
    - `codename`: (`CharField`) Código único para identificação da permissão.

## Integração com Outros Módulos

O módulo `core.permissions` se integra com outros módulos fornecendo um sistema de controle de acesso que pode ser utilizado em todo o sistema.

## Funcionalidades

O módulo `core.permissions` fornece uma API para gerenciar permissões, permitindo que os administradores do sistema definam e atribuam permissões a usuários e grupos.

### Principais Funcionalidades:

1. **Rotas Definidas**:
   - **`/permissions/`**:
     - **GET**: Lista todas as permissões disponíveis.
     - **POST**: Cria uma nova permissão.

   - **`/permissions/<int:id>/`**:
     - **GET**: Recupera os detalhes de uma permissão específica pelo seu ID.
     - **PUT**: Atualiza os detalhes de uma permissão específica.

### Exemplo de Uso da API

#### Listar todas as permissões:

```bash
GET /api/v1/permissions/
```

- **Resposta**: Retorna um JSON com a lista de permissões, incluindo campos como `id`, `name`, `codename`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Admin",
        "codename": "admin"
      },
      {
        "id": 2,
        "name": "User",
        "codename": "user"
      }
    ]
  }
  ```

#### Criar uma nova permissão:

```bash
POST /api/v1/permissions/
```

- **Corpo da Requisição**: JSON com os detalhes da permissão.
  ```json
  {
    "name": "Editor",
    "codename": "editor"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes da permissão criada, incluindo o `id` da permissão e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "name": "Editor",
    "codename": "editor"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `core.permissions`, é necessário que o usuário tenha permissões administrativas. As rotas permitem gerenciar permissões com base em IDs específicos, facilitando a administração de acessos no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de permissões:
  - `name`: Filtrar por nome da permissão.
  - `codename`: Filtrar por código da permissão.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/permissions/?name=admin&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de permissões filtradas pelo nome 'admin', limitado a 10 resultados por página.