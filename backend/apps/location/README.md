# Módulo Location

## Descrição

O módulo `location` é responsável por gerenciar informações e funcionalidades relacionadas a localizações geográficas dentro do sistema. Ele permite que os usuários do sistema adicionem, atualizem e consultem dados de localização.

### Modelos

- **Location**: Representa uma localização geográfica com propriedades como `name` e `coordinates`.

  - **Campos**:
    - `name`: (`CharField`) Nome da localização.
    - `coordinates`: (`PointField`) Coordenadas geográficas da localização.

## Integração com Outros Módulos

O módulo `location` se integra com outros módulos fornecendo dados de localização que podem ser utilizados em mapas e relatórios geográficos.

## Funcionalidades

O módulo `location` fornece uma API para gerenciar dados de localização, permitindo que os usuários do sistema acessem e modifiquem informações de localização conforme necessário.

### Principais Funcionalidades:

1. **Gerenciamento de Localizações**:
   - Permite adicionar novas localizações ao sistema.
   - Permite atualizar informações de localizações existentes.
   - Permite consultar dados de localizações.

### Exemplo de Uso da API

#### Listar todas as localizações:

```bash
GET /api/v1/locations/
```

- **Resposta**: Retorna um JSON com a lista de localizações, incluindo campos como `id`, `name`, `coordinates`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Localização A",
        "coordinates": "POINT(10 20)"
      },
      {
        "id": 2,
        "name": "Localização B",
        "coordinates": "POINT(30 40)"
      }
    ]
  }
  ```

#### Criar uma nova localização:

```bash
POST /api/v1/locations/
```

- **Corpo da Requisição**: JSON com os detalhes da localização.
  ```json
  {
    "name": "Localização C",
    "coordinates": "POINT(50 60)"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes da localização criada, incluindo o `id` da localização e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "name": "Localização C",
    "coordinates": "POINT(50 60)"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `location`, é necessário que o usuário tenha permissões adequadas para acessar e modificar dados de localização. As rotas permitem gerenciar localizações com base em IDs específicos, facilitando a administração de informações de localização no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de localizações:
  - `name`: Filtrar por nome da localização.
  - `coordinates`: Filtrar por coordenadas geográficas.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/locations/?name=Localização A&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de localizações filtradas pelo nome 'Localização A', limitado a 10 resultados por página.