# Módulo Voting.BigNumber

## Descrição

O sub-módulo `voting.big_number` é responsável por gerenciar funcionalidades específicas relacionadas a votações com grandes números de participantes ou opções dentro do sistema.

### Modelos

- **BigNumberVote**: Representa uma votação com grandes números com propriedades como `title` e `options`.

  - **Campos**:
    - `title`: (`CharField`) Título da votação.
    - `options`: (`TextField`) Opções disponíveis na votação.

## Integração com Outros Módulos

O sub-módulo `voting.big_number` se integra com outros módulos fornecendo dados de votações em larga escala que podem ser utilizados em análises e relatórios.

## Funcionalidades

O sub-módulo `voting.big_number` fornece uma API para gerenciar votações que envolvem grandes números, permitindo que os usuários do sistema acessem e modifiquem informações conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Votações com Grandes Números**:
   - Permite criar e gerenciar votações com um grande número de participantes.
   - Otimiza o processamento de dados para votações em larga escala.

### Exemplo de Uso da API

#### Listar todas as votações com grandes números:

```bash
GET /api/v1/big_number_votes/
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

#### Criar uma nova votação com grandes números:

```bash
POST /api/v1/big_number_votes/
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

Para utilizar o sub-módulo `voting.big_number`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de votações em larga escala. As rotas permitem gerenciar votações com base em IDs específicos, facilitando a administração de informações de votações no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de votações:
  - `title`: Filtrar por título da votação.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/big_number_votes/?title=Votação A&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de votações filtradas pelo título 'Votação A', limitado a 10 resultados por página.