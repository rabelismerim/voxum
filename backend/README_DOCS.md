# Estrutura do backend

O backend está organizado em módulos Django sob `apps/`, com funcionalidades compartilhadas e autenticação/autorizações no pacote `core/`.

| Módulo | Responsabilidade |
| --- | --- |
| `apps/creditor` | Credores e representantes |
| `apps/guest` | Convidados e operações relacionadas ao acesso |
| `apps/location` | Estados e municípios |
| `apps/meetings` | Assembleias e reuniões |
| `apps/presence` | Presença e quórum |
| `apps/recovering` | Recuperação de acesso |
| `apps/report` | Relatórios |
| `apps/voting` | Pautas, deliberações e votações |
| `apps/voxum_base` | Funcionalidades compartilhadas e comandos da plataforma |
| `apps/web_sockets` | Consumers e roteamento WebSocket |
| `core` | Usuários internos, permissões e abstrações reutilizadas pelos módulos |

As rotas e os contratos da API devem ser consultados na documentação OpenAPI em `/voxum/api/v1/docs/` ou no arquivo [`swagger.json`](./swagger.json).
