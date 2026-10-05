# Core

O pacote `core` reúne o modelo de usuário da plataforma, permissões, abstrações e endpoints compartilhados pelos módulos Voxum.

## Endpoints

Os endpoints de usuário ficam sob `/voxum/api/v1/core/user/`:

- `/` — listagem de usuários;
- `/<id>/` — detalhe de usuário;
- `/detail/` — detalhe do usuário associado à sessão;
- `/group/` — grupos e permissões.

As operações disponíveis e seus requisitos de autenticação/autorização estão descritos no Swagger em `/voxum/api/v1/docs/`.
