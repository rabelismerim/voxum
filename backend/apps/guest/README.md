# Módulo Guest

## Descrição

O módulo `guest` é responsável por gerenciar informações e funcionalidades relacionadas a convidados dentro do sistema. Ele permite que os usuários do sistema adicionem, atualizem e consultem dados de convidados.

### Modelos

- **UserGuest**: Representa um perfil de convidado com propriedades como `entity` e `is_representative`.

## Integração com Outros Módulos

O módulo `guest` se integra com outros módulos fornecendo dados de convidados que podem ser utilizados em eventos e reuniões.

## Funcionalidades

O módulo `guest` fornece uma API para gerenciar dados de convidados, permitindo que os usuários do sistema acessem e modifiquem informações de convidados conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Convidados**:
   - Permite adicionar novos convidados ao sistema.
   - Permite atualizar informações de convidados existentes.
   - Permite consultar dados de convidados.

### Exemplo de Uso da API

#### Listar todos os convidados:

```bash
GET /api/v1/guests/
```

- **Resposta**: Retorna um JSON com a lista de convidados, incluindo campos como `id`, `name`, `email`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Convidado A",
        "email": "convidadoa@example.com"
      },
      {
        "id": 2,
        "name": "Convidado B",
        "email": "convidadob@example.com"
      }
    ]
  }
  ```

#### Criar um novo convidado:

```bash
POST /api/v1/guests/
```

- **Corpo da Requisição**: JSON com os detalhes do convidado.
  ```json
  {
    "name": "Convidado C",
    "email": "convidadoc@example.com"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes do convidado criado, incluindo o `id` do convidado e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "name": "Convidado C",
    "email": "convidadoc@example.com"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `guest`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de convidados. As rotas permitem gerenciar convidados com base em IDs específicos, facilitando a administração de informações de convidados no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de convidados:
  - `name`: Filtrar por nome do convidado.
  - `email`: Filtrar por e-mail do convidado.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/guests/?name=Convidado A&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de convidados filtrados pelo nome 'Convidado A', limitado a 10 resultados por página.

## URLs

- **`/guests/`**: Lista todos os convidados.
- **`/guests/<uuid:id>/`**: Obtém, atualiza ou deleta um convidado específico com base no ID.
- **`/guests/detail/`**: Obtém detalhes de um convidado.
- **`/guests/ciam/reset_otp/<uuid:id>/`**: Reseta o OTP de um convidado.
- **`/guests/ciam/revoke_otp/<uuid:id>/`**: Revoga o OTP de um convidado.
- **`/guests/ciam/reset_password/<uuid:id>/`**: Reseta a senha de um convidado.
- **`/guests/ciam/send_invite/<uuid:id>/`**: Envia um convite CIAM para um convidado.
- **`/guests/ciam/resend_invite/<uuid:id>/`**: Reenvia um convite CIAM para um convidado.