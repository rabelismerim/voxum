from django.core.management.base import BaseCommand
from django.db import IntegrityError

from apps.creditor.models import Creditor
from apps.meetings.models import ClasseChoices, Classe
from apps.voting.big_number.models import ClasseResult
from apps.voting.models import Choice


class Command(BaseCommand):

    def clear_classes(self):
        creditors = Creditor.objects.exclude(classe__description__in=ClasseChoices)
        classes_valid = Classe.objects.filter(description__in=ClasseChoices)

        for c in creditors:
            for classe in classes_valid:
                try:
                    c.classe_id = classe
                    c.save()
                    print('changed')
                    break
                except IntegrityError:
                    print('not changed')

        Classe.objects.exclude(description__in=ClasseChoices).delete()

    def clear_classes_choices(self):
        Choice.objects.exclude(classe__description__in=ClasseChoices).delete()

    def clear_classes_result__choices(self):
        ClasseResult.objects.exclude(classe__description__in=ClasseChoices).delete()

    def handle(self, *args, **kwargs):
        self.clear_classes_result__choices()
        self.clear_classes()
        self.clear_classes_choices()