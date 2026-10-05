from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from core.permissions.models import TypeGroups, CUSTOM_PERMISSIONS, TypeRoles


class Command(BaseCommand):

    def create(self, type_create):
        bulk_create = []
        bulk_update = []
        for group_code, group_name, _group_type in type_create:
            group = Group.objects.filter(name=group_name).first()
            if group:
                self.stdout.write(self.style.NOTICE(f'Group "{group_name}" already exists'))
            else:
                group = Group(name=group_name)
                bulk_create.append(group)
                self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created successfully'))

        Group.objects.bulk_create(bulk_create)

    def create_groups(self):
        self.create(TypeGroups)

    def create_roles(self):
        self.create(TypeRoles)

    def handle(self, *args, **kwargs):
        self.create_groups()
        self.create_roles()
        self.create_permissions()

    def create_permissions(self):
        groups = Group.objects.all()
        for perm in CUSTOM_PERMISSIONS:
            content_type = ContentType.objects.filter(app_label=perm['app_label'], model=perm['model']).first()

            if not content_type:
                raise ValueError('Content Type de custom permission não encontrada')

            perm_obj = Permission.objects.filter(codename=perm['codename'], name=perm['name'],
                                                 content_type=content_type).first()
            if not perm_obj:
                perm_obj = Permission.objects.create(codename=perm['codename'], name=perm['name'],
                                                     content_type=content_type)
                self.stdout.write(self.style.SUCCESS(f'Permission "{perm["codename"]}" created successfully'))

            for group_name in perm['groups']:
                group = groups.filter(name=group_name).first()
                if not group:
                    raise ValueError(f'Grupo({group_name}) de custom permission não encontrada')
                group.permissions.add(perm_obj)