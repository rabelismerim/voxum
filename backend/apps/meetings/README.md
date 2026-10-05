# Módulo Meeting

## Descrição

O módulo `meeting` é responsável por gerenciar informações e funcionalidades relacionadas a reuniões dentro do sistema. Ele permite que os usuários do sistema agendem, atualizem e consultem dados de reuniões.

### Modelos

- **Meeting**: Representa uma reunião com propriedades como `name`, `location`, `start_date`, `status`, `has_quorum`, `start_register_presence`, `end_register_presence`, `able_to_register_presence`, `meeting_reference`, `meeting_group`, e `order`.

- **RepresentativeMeeting**: Representa um representante atrelado a uma assembleia com propriedades como `meeting`, `guest`, `code`, `is_accredited`, `accredited_by`, `accredited_date`, e `meeting_invited`.

- **UserMeeting**: Representa a associação entre usuários e reuniões com propriedades como `groups`, `user`, e `meeting`.

## Integração com Outros Módulos

O módulo `meeting` se integra com outros módulos fornecendo dados de reuniões que podem ser utilizados em calendários e notificações.

## Funcionalidades

O módulo `meeting` fornece uma API para gerenciar dados de reuniões, permitindo que os usuários do sistema acessem e modifiquem informações de reuniões conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Reuniões**:
   - Permite agendar novas reuniões no sistema.
   - Permite atualizar informações de reuniões existentes.
   - Permite consultar dados de reuniões.

### Exemplo de Uso da API

#### Listar todas as reuniões:

```bash
GET /api/v1/meetings/
```

- **Resposta**: Retorna um JSON com a lista de reuniões, incluindo campos como `id`, `title`, `date`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Reunião A",
        "date": "2023-01-01T10:00:00Z"
      },
      {
        "id": 2,
        "title": "Reunião B",
        "date": "2023-01-02T14:00:00Z"
      }
    ]
  }
  ```

#### Criar uma nova reunião:

```bash
POST /api/v1/meetings/
```

- **Corpo da Requisição**: JSON com os detalhes da reunião.
  ```json
  {
    "title": "Reunião C",
    "date": "2023-01-03T16:00:00Z"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes da reunião criada, incluindo o `id` da reunião e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "title": "Reunião C",
    "date": "2023-01-03T16:00:00Z"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `meeting`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de reuniões. As rotas permitem gerenciar reuniões com base em IDs específicos, facilitando a administração de informações de reuniões no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de reuniões:
  - `title`: Filtrar por título da reunião.
  - `date`: Filtrar por data da reunião.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/meetings/?title=Reunião A&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de reuniões filtradas pelo título 'Reunião A', limitado a 10 resultados por página.

## URLs

- **`/meetings/`**: Lista todas as reuniões.
- **`/meetings/big_numbers/<uuid:id>/`**: Detalhes de números grandes de uma reunião.
- **`/meetings/<uuid:id>/`**: Obtém, atualiza ou deleta uma reunião específica com base no ID.
- **`/meetings/guest/detail/<uuid:id>/`**: Detalhes de um convidado em uma reunião.
- **`/meetings/class/`**: Gerencia classes.
- **`/meetings/options/`**: Gerencia opções de escolha.
- **`/meetings/suspend/<uuid:id>/`**: Suspende uma reunião.
- **`/meetings/group/`**: Gerencia grupos de reuniões.
- **`/meetings/representatives/`**: Cria representantes para reuniões.
- **`/meetings/representatives/<uuid:meeting_id>/`**: Lista representantes de uma reunião.
- **`/meetings/dispatch_link_ciam/<uuid:id>/`**: Inicia o envio de link CIAM.
- **`/meetings/dispatch_link_meeting/<uuid:id>/`**: Inicia o envio de link de reunião.
- **`/meetings/register_presence/start/<uuid:id>/`**: Inicia o registro de presença.
- **`/meetings/register_presence/extend/<uuid:id>/`**: Estende o registro de presença.
- **`/meetings/register_presence/end/<uuid:id>/`**: Encerra o registro de presença.