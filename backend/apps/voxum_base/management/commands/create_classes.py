from django.core.management.base import BaseCommand

from apps.voxum_base.utils import get_classe_format  # Atualizado para a nova app base
from apps.meetings.models import ClasseChoices, Classe


class Command(BaseCommand):

    def create_classes(self):
        bulk_create = []
        classes = Classe.objects.all()
        for classe in ClasseChoices:
            classe = get_classe_format(classe)
            if not classes.filter(description=classe).exists():
                bulk_create.append(Classe(description=classe))
                self.stdout.write(self.style.SUCCESS(f'Classe "{classe}" created successfully'))

        Classe.objects.bulk_create(bulk_create)

    def handle(self, *args, **kwargs):
        self.create_classes()