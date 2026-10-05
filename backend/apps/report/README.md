# Módulo Report

## Descrição

O módulo `report` é responsável por gerenciar a geração e o gerenciamento de relatórios dentro do sistema. Ele permite que os usuários do sistema criem, atualizem e consultem relatórios.

### Modelos

- **Report**: Representa um relatório com propriedades como `title` e `content`.

  - **Campos**:
    - `title`: (`CharField`) Título do relatório.
    - `content`: (`TextField`) Conteúdo detalhado do relatório.

## Integração com Outros Módulos

O módulo `report` se integra com outros módulos fornecendo dados de relatórios que podem ser utilizados em análises e apresentações de resultados.

## Funcionalidades

O módulo `report` fornece uma API para gerenciar dados de relatórios, permitindo que os usuários do sistema acessem e modifiquem informações de relatórios conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Relatórios**:
   - Permite criar novos relatórios no sistema.
   - Permite atualizar informações de relatórios existentes.
   - Permite consultar dados de relatórios.

### Exemplo de Uso da API

#### Listar todos os relatórios:

```bash
GET /api/v1/reports/
```

- **Resposta**: Retorna um JSON com a lista de relatórios, incluindo campos como `id`, `title`, `content`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Relatório A",
        "content": "Conteúdo do Relatório A"
      },
      {
        "id": 2,
        "title": "Relatório B",
        "content": "Conteúdo do Relatório B"
      }
    ]
  }
  ```

#### Criar um novo relatório:

```bash
POST /api/v1/reports/
```

- **Corpo da Requisição**: JSON com os detalhes do relatório.
  ```json
  {
    "title": "Relatório C",
    "content": "Conteúdo do Relatório C"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes do relatório criado, incluindo o `id` do relatório e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "title": "Relatório C",
    "content": "Conteúdo do Relatório C"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `report`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de relatórios. As rotas permitem gerenciar relatórios com base em IDs específicos, facilitando a administração de informações de relatórios no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de relatórios:
  - `title`: Filtrar por título do relatório.
  - `content`: Filtrar por conteúdo do relatório.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/reports/?title=Relatório A&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de relatórios filtrados pelo título 'Relatório A', limitado a 10 resultados por página.

## Sinais

O módulo `report` utiliza os seguintes sinais para gerenciar eventos:

- **pre_delete**: Executa ações antes de um objeto ser deletado.
- **post_save**: Executa ações após um objeto ser salvo.
- **post_delete**: Executa ações após um objeto ser deletado.
- **pre_delete**: A função `remove_task_id` é um receptor deste sinal para o modelo `TaskResult`. Ela dissocia o `task_id` de relatórios (`ReportMeeting` ou `ReportVoting`) associados ao `TaskResult` que está sendo deletado, definindo o `task_id` como `None` e salvando o relatório.

## Detalhamento dos Arquivos

### Arquivo `conversor.py`

O arquivo `conversor.py` no módulo `report` é responsável por converter dados de relatórios em diferentes formatos. Ele define funções e classes que lidam com a transformação de dados para exportação e apresentação.

### Arquivo `sockets.py`

O arquivo `sockets.py` define classes de esquema para comunicação em tempo real relacionada a relatórios, utilizando WebSockets. As principais classes incluem:

- **ReportList**: Gerencia a lista de relatórios, utilizando o `ReportAdminSchema` e o canal `report_list`.
- **ReportDetail**: Fornece detalhes de um relatório específico, utilizando sinais para atualizações em tempo real.

Essas classes integram-se com outros módulos, como `apps.web_sockets`, para gerenciar dados de relatórios e sinais de WebSocket, garantindo que as atualizações sejam refletidas em tempo real para todos os clientes conectados.

### Arquivo `tasks.py`

O arquivo `tasks.py` é responsável por gerenciar tarefas relacionadas a funcionalidades de mensagens usando Celery e Redis no contexto de relatórios. As principais classes e funções incluem:

- **SendReportList**: Tarefa para enviar detalhes da lista de relatórios para usuários qualificados.
- **SendReportUserDetail**: Gerencia o envio de detalhes de relatório para usuários conectados.
- **ProcessReport**: Lida com o processamento de dados de relatório recebidos.

Essas tarefas utilizam conexões Redis para comunicação e são integradas com sinais do Django para disparar ações específicas, como o envio de detalhes de progresso de relatório ao salvar instâncias do modelo `Report`. Elas garantem que as informações de relatório sejam processadas e distribuídas corretamente entre os usuários envolvidos.