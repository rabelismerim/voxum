# Módulo Works

## Descrição

O módulo `works` é responsável por gerenciar informações e funcionalidades relacionadas a trabalhos ou tarefas dentro do sistema. Ele permite que os usuários do sistema criem, atualizem e consultem dados de trabalhos.

### Modelos

- **Work**: Representa um trabalho ou tarefa com propriedades como `title` e `description`.

  - **Campos**:
    - `title`: (`CharField`) Título do trabalho.
    - `description`: (`TextField`) Descrição detalhada do trabalho.

## Integração com Outros Módulos

O módulo `works` se integra com outros módulos fornecendo dados de trabalhos que podem ser utilizados em relatórios de produtividade e análises de desempenho.

## Funcionalidades

O módulo `works` fornece uma API para gerenciar dados de trabalhos, permitindo que os usuários do sistema acessem e modifiquem informações de trabalhos conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Trabalhos**:
   - Permite criar novos trabalhos no sistema.
   - Permite atualizar informações de trabalhos existentes.
   - Permite consultar dados de trabalhos.

### Exemplo de Uso da API

#### Listar todos os trabalhos:

```bash
GET /api/v1/works/
```

- **Resposta**: Retorna um JSON com a lista de trabalhos, incluindo campos como `id`, `title`, `description`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Trabalho A",
        "description": "Descrição do Trabalho A"
      },
      {
        "id": 2,
        "title": "Trabalho B",
        "description": "Descrição do Trabalho B"
      }
    ]
  }
  ```

#### Criar um novo trabalho:

```bash
POST /api/v1/works/
```

- **Corpo da Requisição**: JSON com os detalhes do trabalho.
  ```json
  {
    "title": "Trabalho C",
    "description": "Descrição do Trabalho C"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes do trabalho criado, incluindo o `id` do trabalho e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "title": "Trabalho C",
    "description": "Descrição do Trabalho C"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `works`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de trabalhos. As rotas permitem gerenciar trabalhos com base em IDs específicos, facilitando a administração de informações de trabalhos no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de trabalhos:
  - `title`: Filtrar por título do trabalho.
  - `description`: Filtrar por descrição do trabalho.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/works/?title=Trabalho A&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de trabalhos filtrados pelo título 'Trabalho A', limitado a 10 resultados por página.

## Sinais

O módulo `works` utiliza os seguintes sinais para gerenciar eventos:

- **post_save**: A função `start_callback_worker` é um receptor deste sinal para o modelo `ExcelWorker`. Ela verifica se a instância do `ExcelWorker` é de um tipo de conteúdo específico e, se for, processa a instância chamando o método `process_callback` da subclasse correspondente de `ParseTitle`.