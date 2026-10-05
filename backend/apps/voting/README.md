# Módulo Voting

## Descrição

O módulo `voting` é responsável por gerenciar informações e funcionalidades relacionadas a votações dentro do sistema. Ele permite que os usuários do sistema criem, atualizem e participem de votações.

### Modelos

- **Vote**: Representa uma votação com propriedades como `title` e `options`.

  - **Campos**:
    - `title`: (`CharField`) Título da votação.
    - `options`: (`TextField`) Opções disponíveis na votação.

- **Voting**: Representa uma instância de votação.
  - **Atributos**:
    - `meeting`: (`ForeignKey`) Referência para o modelo `Meeting`.
    - `type`: (`CharField`) Tipo da votação.
    - `start_date`: (`DateTimeField`) Data de início da votação.
    - `end_date`: (`DateTimeField`) Data de término da votação.
    - `status`: (`CharField`) Status da votação.
  - **Métodos**:
    - `is_ability_to_create_choice()`: Retorna `True` se o status da votação não for 'E', caso contrário, `False`.
    - `choice`: Retorna um `QuerySet` de todas as instâncias de `Choice` associadas à votação.
    - `class_choice`: Retorna uma lista de dicionários, cada um contendo a descrição da classe e as escolhas associadas a ela.

- **Choice**: Representa uma opção de escolha para uma votação.
  - **Atributos**:
    - `voting`: (`ForeignKey`) A votação associada a esta escolha.
    - `classe`: (`ProtectedFK`) A classe associada a esta escolha.
    - `value`: (`CharField`) O valor da opção de escolha.
  - **Métodos**:
    - `__str__`: Retorna a representação em string da escolha.
    - `qualified_creditors`: Retorna a contagem de credores qualificados com base na classe associada e na reunião da votação.

- **VotingResult**: Representa um resultado de votação, associando um voto a um credor.
  - **Atributos**:
    - `vote`: (`ForeignKey`) A opção de escolha selecionada para a votação.
    - `creditor`: (`ForeignKey`) O credor que votou.
  - **Métodos**:
    - `__str__`: Retorna a representação em string do resultado da votação.
    - `save`: Sobrescreve o método de salvamento padrão para adicionar lógica de validação personalizada.

## Integração com Outros Módulos

O módulo `voting` se integra com outros módulos fornecendo dados de votações que podem ser utilizados em relatórios e análises de resultados.

## Funcionalidades

O módulo `voting` fornece uma API para gerenciar dados de votações, permitindo que os usuários do sistema acessem e modifiquem informações de votações conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Votações**:
   - Permite criar novas votações no sistema.
   - Permite atualizar informações de votações existentes.
   - Permite participar de votações.

### Exemplo de Uso da API

#### Listar todas as votações:

```bash
GET /api/v1/votes/
```

- **Resposta**: Retorna um JSON com a lista de votações, incluindo campos como `id`, `title`, `options`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Votação A",
        "options": "Opção 1, Opção 2"
      },
      {
        "id": 2,
        "title": "Votação B",
        "options": "Opção A, Opção B"
      }
    ]
  }
  ```

#### Criar uma nova votação:

```bash
POST /api/v1/votes/
```

- **Corpo da Requisição**: JSON com os detalhes da votação.
  ```json
  {
    "title": "Votação C",
    "options": "Opção X, Opção Y"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes da votação criada, incluindo o `id` da votação e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "title": "Votação C",
    "options": "Opção X, Opção Y"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `voting`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de votações. As rotas permitem gerenciar votações com base em IDs específicos, facilitando a administração de informações de votações no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de votações:
  - `title`: Filtrar por título da votação.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/votes/?title=Votação A&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de votações filtradas pelo título 'Votação A', limitado a 10 resultados por página.

## Sinais

O módulo `voting` utiliza os seguintes sinais para gerenciar eventos:

- **post_save**: A função `dispatch_voting_choice` é um receptor deste sinal para o modelo `Choice`. Ela despacha uma atualização para a lista de votações, enviando o sinal `update_voting_list` com a instância de votação associada.

- **post_delete**: A função `dispatch_voting_choice` é um receptor deste sinal para o modelo `Choice`. Ela despacha uma atualização para a lista de votações, enviando o sinal `update_voting_list` com a instância de votação associada.

- **post_delete**: A função `dispatch_voting_post_delete` é um receptor deste sinal para o modelo `Voting`. Ela despacha uma atualização para a lista de votações por reunião, enviando o sinal `update_voting_by_meeting_list` com a instância de reunião associada.

## Detalhamento dos Arquivos

### Arquivo `report.py`

O arquivo `report.py` no módulo `voting` é responsável por gerar relatórios de votações. Ele define a classe `AbstractVotingReport`, que utiliza o modelo `ReportVotingToPDF` para criar relatórios em PDF das votações. A classe gerencia colunas e linhas específicas para formatação dos relatórios e integra-se com o módulo `apps.report` para a geração de PDFs.

### Arquivo `sockets.py`

O arquivo `sockets.py` define classes de esquema para comunicação em tempo real relacionada a votações, utilizando WebSockets. As principais classes incluem:

- **VotingList**: Gerencia a lista de votações, utilizando o `VotingAdminSchema` e o canal `voting_list`.
- **VotingByMeetingList**: Similar ao `VotingList`, mas específico para reuniões, utilizando o sinal `update_voting_by_meeting_list`.
- **VotingDelete**: Gerencia a exclusão de votações, atualizando clientes sobre remoções.
- **VotingDetail**: Fornece detalhes de uma votação específica, utilizando sinais para atualizações em tempo real.
- **VotingProgressDetail**: Gerencia detalhes do progresso de uma votação em andamento, utilizando sinais para atualizações em tempo real.

Essas classes integram-se com outros módulos, como `apps.meeting` e `apps.web_sockets`, para gerenciar dados de reuniões e sinais de WebSocket, garantindo que as atualizações sejam refletidas em tempo real para todos os clientes conectados.

### Arquivo `tasks.py`

O arquivo `tasks.py` é responsável por gerenciar tarefas relacionadas a funcionalidades de mensagens usando Celery e Redis no contexto de votações. As principais classes e funções incluem:

- **SendVotingList**: Tarefa para enviar detalhes da lista de votações para credores qualificados.
- **SendVotingUserDetail**: Gerencia o envio de detalhes de votação para usuários conectados.
- **ProcessVoting**: Lida com o processamento de dados de votação recebidos.
- **ProcessVotingRepresentative**: Processa dados de votação para representantes.
- **ProcessVotingResultAbstention**: Gerencia abstenções de resultados de votação e envia notificações.

Essas tarefas utilizam conexões Redis para comunicação e são integradas com sinais do Django para disparar ações específicas, como o envio de detalhes de progresso de votação ao salvar instâncias do modelo `Voting`. Elas garantem que as informações de votação sejam processadas e distribuídas corretamente entre os usuários e credores envolvidos.

## URLs

- **`/`**: Cria uma nova votação.
- **`/meeting/<uuid:meeting_id>/`**: Obtém uma lista de votações com base no `meeting_id`.
- **`/<uuid:id>/`**: Obtém, atualiza ou deleta uma votação específica com base no ID.
- **`/start/<uuid:id>/`**: Inicia uma votação.
- **`/extend/<uuid:id>/`**: Estende o tempo de uma votação em andamento.
- **`/end/<uuid:id>/`**: Encerra uma votação.
- **`/qualified_creditors/<uuid:id>/`**: Obtém os credores qualificados para uma votação específica.
- **`/choice/`**: Cria uma nova escolha.
- **`/choice/<uuid:id>/`**: Obtém, atualiza ou deleta uma escolha específica com base no ID.
- **`/result/`**: Registra a escolha do credor, feito pelos usuários corporativos.
- **`/result/<uuid:id>/`**: Obtém, atualiza ou deleta um resultado de votação específico com base no ID.
- **`/representatives/<uuid:representative_id>/`**: Registra as escolhas dos credores por meio do ID do representante.