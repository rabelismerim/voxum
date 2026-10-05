from django.db.models import TextChoices
from utils import _

GroupUserGuest = _('User Guest')


class TypeGroupChoices(TextChoices):
    MANAGER = 'M', _('Gerente')
    CONSULTANT = 'C', _('Consultor')


class GroupTypeGroupChoices(TextChoices):
    GROUP = 'G', _('Grupo')
    ROLES = 'R', _('Papel')


class TypeRolesChoices(TextChoices):
    GUEST = 'G', GroupUserGuest
    INTERNAL = 'I', _('User Interno')
    ADMIN = 'A', _('Admin')


"""
Represents group types available, description and Group type choice
"""
TypeGroups = (
    (TypeGroupChoices.MANAGER.value, TypeGroupChoices.MANAGER.label, GroupTypeGroupChoices.GROUP.value),
    (TypeGroupChoices.CONSULTANT.value, TypeGroupChoices.CONSULTANT.label, GroupTypeGroupChoices.GROUP.value),
)

TypeRoles = (
    (TypeRolesChoices.GUEST.value, TypeRolesChoices.GUEST.label, GroupTypeGroupChoices.ROLES.value),
    (TypeRolesChoices.INTERNAL.value, TypeRolesChoices.INTERNAL.label, GroupTypeGroupChoices.ROLES.value),
    (TypeRolesChoices.ADMIN.value, TypeRolesChoices.ADMIN.label, GroupTypeGroupChoices.ROLES.value),
)


class CustomPermissionChoices(TextChoices):
    MANAGER_PROJECT = 'can_manage_project', _('Pode Gerenciar Projeto')
    CONSULTANT_PROJECT = 'can_consult_project', _('Pode Consultar Projeto')


CUSTOM_PERMISSIONS = [
    {
        'app_label': 'core',
        'model': 'user',
        'codename': CustomPermissionChoices.MANAGER_PROJECT.value,
        'name': CustomPermissionChoices.MANAGER_PROJECT.label,
        'groups': [TypeGroupChoices.MANAGER.label]
    },
    {
        'app_label': 'core',
        'model': 'user',
        'codename': CustomPermissionChoices.CONSULTANT_PROJECT.value,
        'name': CustomPermissionChoices.CONSULTANT_PROJECT.label,
        'groups': [TypeGroupChoices.CONSULTANT.label]
    },
]