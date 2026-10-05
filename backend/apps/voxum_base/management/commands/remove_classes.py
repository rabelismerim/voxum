from django.core.management import BaseCommand

from apps.voxum_base.utils import get_new_code  # Atualizado para a nova app base
from apps.meetings.models import Classe


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for classe in Classe.objects.exclude(description__istartswith='classe'):
            classe.description = f'Classe {get_new_code()}'
            classe.save()