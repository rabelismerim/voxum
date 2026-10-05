# Módulo Creditor

## Descrição

O módulo `creditor` é responsável por gerenciar informações relacionadas a credores dentro do sistema. Ele fornece funcionalidades para adicionar, atualizar e consultar dados de credores.

### Modelos

- **Creditor**: Representa um credor com propriedades como `meeting`, `guest`, `classe`, `recovering`, `coin`, `type_person`, `credit_value`, `converted_value`, `exchange_tax`, `contested_value`, `online`, `priority`, `code`, e `meeting_invited`.

- **Representative**: Representa um representante com propriedades como `priority`, `representative`, `creditor`, e `online`.

## Integração com Outros Módulos

O módulo `creditor` se integra com outros módulos fornecendo dados de credores que podem ser utilizados em processos financeiros e administrativos.

## Funcionalidades

O módulo `creditor` fornece uma API para gerenciar dados de credores, permitindo que os usuários do sistema acessem e modifiquem informações de credores conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Credores**:
   - Permite adicionar novos credores ao sistema.
   - Permite atualizar informações de credores existentes.
   - Permite consultar dados de credores.

### Exemplo de Uso da API

#### Listar todos os credores:

```bash
GET /api/v1/creditors/
```

- **Resposta**: Retorna um JSON com a lista de credores, incluindo campos como `id`, `name`, `amount_due`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Credor A",
        "amount_due": "1000.00"
      },
      {
        "id": 2,
        "name": "Credor B",
        "amount_due": "2000.00"
      }
    ]
  }
  ```

#### Criar um novo credor:

```bash
POST /api/v1/creditors/
```

- **Corpo da Requisição**: JSON com os detalhes do credor.
  ```json
  {
    "name": "Credor C",
    "amount_due": "1500.00"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes do credor criado, incluindo o `id` do credor e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "name": "Credor C",
    "amount_due": "1500.00"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `creditor`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de credores. As rotas permitem gerenciar credores com base em IDs específicos, facilitando a administração de informações de credores no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de credores:
  - `name`: Filtrar por nome do credor.
  - `amount_due`: Filtrar por valor devido.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/creditors/?name=Credor A&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de credores filtrados pelo nome 'Credor A', limitado a 10 resultados por página.

## URLs

- **`/creditors/`**: Lista todos os credores.
- **`/creditors/<uuid:id>/`**: Obtém, atualiza ou deleta um credor específico com base no ID.
- **`/creditors/meeting/<uuid:meeting_id>/`**: Obtém credores associados a uma reunião específica.
- **`/creditors/representative/<uuid:representative__representative__id>/`**: Obtém representantes associados a um credor específico.