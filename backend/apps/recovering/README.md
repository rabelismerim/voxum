# Módulo Recovering

## Descrição

O módulo `recovering` é responsável por gerenciar informações e funcionalidades relacionadas a processos de recuperação dentro do sistema. Ele permite que os usuários do sistema acompanhem, atualizem e consultem dados de processos de recuperação.

### Modelos

- **Recovering**: Representa um processo de recuperação com a propriedade `name`.

## Integração com Outros Módulos

O módulo `recovering` se integra com outros módulos fornecendo dados de processos de recuperação que podem ser utilizados em relatórios e análises.

## Funcionalidades

O módulo `recovering` fornece uma API para gerenciar dados de processos de recuperação, permitindo que os usuários do sistema acessem e modifiquem informações conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Processos de Recuperação**:
   - Permite acompanhar processos de recuperação no sistema.
   - Permite atualizar informações de processos de recuperação existentes.
   - Permite consultar dados de processos de recuperação.

### Exemplo de Uso da API

#### Listar todos os processos de recuperação:

```bash
GET /api/v1/recoveries/
```

- **Resposta**: Retorna um JSON com a lista de processos de recuperação, incluindo campos como `id`, `case_number`, `status`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "case_number": "REC123",
        "status": "Em andamento"
      },
      {
        "id": 2,
        "case_number": "REC456",
        "status": "Concluído"
      }
    ]
  }
  ```

#### Criar um novo processo de recuperação:

```bash
POST /api/v1/recoveries/
```

- **Corpo da Requisição**: JSON com os detalhes do processo de recuperação.
  ```json
  {
    "case_number": "REC789",
    "status": "Pendente"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes do processo de recuperação criado, incluindo o `id` do processo e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "case_number": "REC789",
    "status": "Pendente"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `recovering`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de processos de recuperação. As rotas permitem gerenciar processos com base em IDs específicos, facilitando a administração de informações de recuperação no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de processos de recuperação:
  - `case_number`: Filtrar por número do caso.
  - `status`: Filtrar por status do processo.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/recoveries/?status=Em andamento&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de processos de recuperação filtrados pelo status 'Em andamento', limitado a 10 resultados por página.

## URLs

- **`/recoveries/`**: Lista todos os processos de recuperação.