# Módulo Presence

## Descrição

O módulo `presence` é responsável por gerenciar informações e funcionalidades relacionadas à presença de usuários dentro do sistema. Ele permite que os usuários do sistema registrem, atualizem e consultem dados de presença.

### Modelos

- **Presence**: Representa a presença de um usuário com propriedades como `user` e `status`.

  - **Campos**:
    - `user`: (`ForeignKey`) Referência para o usuário associado à presença.
    - `status`: (`CharField`) Status da presença do usuário.

## Integração com Outros Módulos

O módulo `presence` se integra com outros módulos fornecendo dados de presença que podem ser utilizados em relatórios de frequência e análises de participação.

## Funcionalidades

O módulo `presence` fornece uma API para gerenciar dados de presença, permitindo que os usuários do sistema acessem e modifiquem informações de presença conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Presença**:
   - Permite registrar a presença de usuários no sistema.
   - Permite atualizar informações de presença existentes.
   - Permite consultar dados de presença.

### Exemplo de Uso da API

#### Listar todas as presenças:

```bash
GET /api/v1/presences/
```

- **Resposta**: Retorna um JSON com a lista de presenças, incluindo campos como `id`, `user`, `status`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "user": "user1",
        "status": "Presente"
      },
      {
        "id": 2,
        "user": "user2",
        "status": "Ausente"
      }
    ]
  }
  ```

#### Registrar uma nova presença:

```bash
POST /api/v1/presences/
```

- **Corpo da Requisição**: JSON com os detalhes da presença.
  ```json
  {
    "user": "user3",
    "status": "Presente"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes da presença registrada, incluindo o `id` da presença e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "user": "user3",
    "status": "Presente"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `presence`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de presença. As rotas permitem gerenciar presenças com base em IDs específicos, facilitando a administração de informações de presença no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de presenças:
  - `user`: Filtrar por usuário associado à presença.
  - `status`: Filtrar por status da presença.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/presences/?status=Presente&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de presenças filtradas pelo status 'Presente', limitado a 10 resultados por página.