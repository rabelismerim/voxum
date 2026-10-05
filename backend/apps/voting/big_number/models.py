from apps.voxum_base.models import AbstractModel
from django.db import models

from apps.meetings.models import Classe


class ClasseResult(AbstractModel):
    voting = models.ForeignKey('voting.Voting', on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT)
    count_voters = models.PositiveIntegerField(default=0)
    count_qualified_creditors = models.PositiveIntegerField(default=0)
    count_accredited_creditors = models.PositiveIntegerField(default=0)
    count_remaining = models.PositiveIntegerField(default=0)
    percentage_voters = models.FloatField(default=0)
    percentage_remaining = models.FloatField(default=0)
    total_credit_value = models.FloatField(default=0)
    total_accredited_credit_value = models.FloatField(default=0)
    total_voters_credit_value = models.FloatField(default=0)
    total_remaining = models.FloatField(default=0)
    total_percentage_voters = models.FloatField(default=0)
    total_percentage_remaining = models.FloatField(default=0)

    def __str__(self):
        return f'Result for class {self.classe} in voting {self.voting.id}'

    @property
    def name(self):
        return self.classe.description

    @property
    def choices(self):
        return self.choiceresult_set.all()


class ChoiceResult(AbstractModel):
    classe_result = models.ForeignKey(ClasseResult, on_delete=models.CASCADE)
    choice = models.ForeignKey('voting.Choice', on_delete=models.CASCADE)
    count_voters = models.PositiveIntegerField(default=0)
    percentage_voters = models.FloatField(default=0)
    count_qualified_creditors = models.IntegerField(default=0)
    total_voters_credit_value = models.FloatField(default=0)
    total_percentage_voters = models.FloatField(default=0)

    def __str__(self):
        return f'Choice {self.value} result in class result {self.classe_result.id}'

    @property
    def value(self):
        return self.choice.value