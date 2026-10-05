import logging
import uuid
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models, transaction
from django.db.models import F, Count, OuterRef, Subquery, Q, TextChoices, Sum, Value, BooleanField, Case, When, \
    UUIDField
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from utils import _, get_user_model

from apps.voxum_base.utils import timeit
from apps.creditor.models import Creditor

from apps.meetings.models import Meeting, Classe, RepresentativeMeeting
from apps.voting.big_number.models import ClasseResult, ChoiceResult
from apps.web_sockets.signals import update_creditor_detail, update_voting_list, voting_end, \
    update_voting_by_meeting_list, voting_start, started_update_voting_progress_detail
from support.schedule.models import SCHEDULER


class TypeVotingChoices(TextChoices):
    ASSUNTO = 'S', _('Assunto')
    ESCOLHA = 'C', _('Escolha')


class StatusVotingChoice(TextChoices):
    AGENDADA = 'A', 'Agendada'
    INICIADA = 'I', 'Iniciada'
    ENCERRADA = 'E', 'Encerrada'
    ATRASADA = 'D', 'Atrasada'
    REAGENDADA = 'R', 'Reagendada'


class DefaultEscolhaChoices(TextChoices):
    ABSTENCAO = 'A', 'Abstenção'


class DefaultAssuntoChoices(TextChoices):
    SIM = 'S', 'Sim'
    NAO = 'N', 'Não'
    ABSTENCAO = 'A', 'Abstenção'


ORDER_MAPPING_CHOICES = {
    DefaultAssuntoChoices.SIM.value: 1,
    DefaultAssuntoChoices.NAO.value: 2,
    DefaultAssuntoChoices.ABSTENCAO.value: 4
}


def map_value_choice(value):
    return str(value).strip().title()


class Voting(models.Model):
    """
    Model class for a voting instance.

    Attributes:
        meeting: A ForeignKey to the Meeting model for the meeting of the voting.
        type: A CharField for the type of the voting.
        end_date: A DateTimeField for the end date of the voting.
        status: A CharField for the status of the voting.

    Methods:
        is_ability_to_create_choice(): Returns True if the status of the voting is not 'E', False otherwise.
        choice: Returns a QuerySet of all Choice instances associated with the voting.
        class_choice: Returns a list of dictionaries, each containing the class description and the choices associated
        with it.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TypeVotingChoices.choices)
    start_date = models.DateTimeField(_('Data de inicio'), null=True, blank=True)
    end_date = models.DateTimeField(_('Data de fim'), null=True, blank=True)
    status = models.CharField('Status', max_length=1, choices=StatusVotingChoice.choices,
                              default=StatusVotingChoice.AGENDADA, db_index=True)

    class Meta:
        ordering = ('-start_date', '-created_at', '-updated_at')

    def delete(self, *args, **kwargs):
        # Antes de deletar o Voting, exclua as Choices associadas
        self.choice_set.all().annotate(
            state_deleting_voting=Value(True, output_field=BooleanField())
        ).delete()

        # Agora, chame o delete original para o Voting
        super().delete(*args, **kwargs)

    @property
    def situation(self) -> bool:
        """Indica a situation of the voting."""
        return self.meeting.situation

    @property
    def situation_display(self) -> bool:
        """Indica the display situation of the voting."""
        return self.meeting.get_situation_display()

    @property
    def in_progress(self) -> bool:
        """Indica se a votação está em progresso"""
        return self.status == StatusVotingChoice.INICIADA

    def validate_unique(self, exclude=None):

        if self.status == StatusVotingChoice.INICIADA:
            voting_exists = Voting.objects.filter(meeting=self.meeting, status=StatusVotingChoice.INICIADA).exclude(
                id=self.id).exists()
            if voting_exists:
                raise ValidationError({
                    'status': _("Existe outra votação em andamento. Aguarde a finalização dela para iniciar uma nova.")
                })

        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        if self.status == StatusVotingChoice.INICIADA:
            self.scheduler_finish_voting()
        return super().save(args, kwargs)

    def create_default_choices(self, classes_ids):

        if self.type == TypeVotingChoices.ESCOLHA:
            default_choices = DefaultEscolhaChoices
        else:
            default_choices = DefaultAssuntoChoices

        choices_bulk = []

        choices = self.choice.filter(value__in=default_choices.labels)

        for char, label in default_choices.choices:
            choice = map_value_choice(label)
            for classe in classes_ids:
                if not choices.filter(value=choice, classe_id=classe, voting=self).exists():
                    order = ORDER_MAPPING_CHOICES.get(char, 3)
                    new_choice = Choice(value=choice, classe_id=classe, voting=self, order=order)
                    choices_bulk.append(new_choice)
        Choice.objects.bulk_create(choices_bulk)

    def is_ability_to_create_choice(self) -> bool:
        """
        Returns True if the status of the voting is not 'E', False otherwise.
        """
        return self.status != 'E'

    @property
    def choice(self):
        """
        Returns a QuerySet of all Choice instances associated with the voting.
        """
        return self.choice_set.all().distinct().select_related('classe')

    @property
    def class_choice(self) -> list:
        """
        Returns a list of dictionaries, each containing the class description and the choices associated with it.
        """
        all_choices = self.choice
        choices = all_choices.values('classe__description', 'classe_id').annotate(
            choice_count=Count('classe_id')).distinct()
        list_choices = []
        class_included = []
        for choice in choices:
            class_name = choice['classe__description']

            if class_name not in class_included:
                class_included.append(class_name)
                choice_obj = {'classe': class_name,
                              'choices': all_choices.filter(classe_id=choice['classe_id'])}
                list_choices.append(choice_obj)
        return list_choices

    @property
    def results(self) -> list:
        """
        retrieve the results of the voting, including the total number of voters
        and the number of qualified creditors for each choice.
        """
        return self.classeresult_set.all()

    def get_classes(self):
        return Classe.objects.filter(id__in=self.choice.values_list('classe_id', flat=True).distinct())

    @timeit
    def set_results(self):
        """
        Calculate and retrieve the results of the voting.
        """
        classes = self.get_classes()
        voting_classe_results = self.classeresult_set.all().select_related('classe')
        result_bulk_create = []
        result_bulk_update = []

        choice_bulk_create = []
        choice_bulk_update = []
        voting_classe_results_ids = []

        classes_processor = []

        for classe in classes:
            processor = ClasseProcessor(classe=classe, voting=self).get_data()
            classes_processor.append(processor.copy())
            classe_id = processor.pop('classe')
            processor.pop('name')
            classe_choices = processor.pop('choices')

            voting_classe_result = voting_classe_results.filter(voting=self, classe_id=classe_id).first()
            if not voting_classe_result:
                voting_classe_result = ClasseResult(voting=self, classe_id=classe_id, **processor)
                result_bulk_create.append(voting_classe_result)
            else:
                voting_classe_result.dict_update(commit=False, **processor)
                result_bulk_update.append(voting_classe_result)

            voting_classe_results_ids.append(voting_classe_result.id)

            for classe_choice in classe_choices:
                classe_choice_id = classe_choice.pop('choice_id')
                classe_choice.pop('value')
                choice_result = voting_classe_result.choiceresult_set.filter(choice_id=classe_choice_id).first()

                if not choice_result:
                    choice_result = ChoiceResult(classe_result=voting_classe_result, choice_id=classe_choice_id,
                                                 **classe_choice)
                    choice_bulk_create.append(choice_result)
                else:
                    choice_result.dict_update(commit=False, **classe_choice)
                    choice_bulk_update.append(choice_result)

        voting_classe_results.exclude(id__in=voting_classe_results_ids).delete()
        ClasseResult.objects.bulk_create(result_bulk_create)
        ClasseResult.objects.bulk_update(result_bulk_update, fields=(
            'count_voters', 'count_qualified_creditors', 'count_remaining', 'percentage_voters', 'percentage_remaining',
            'total_credit_value', 'total_voters_credit_value', 'total_remaining', 'total_percentage_voters',
            'total_percentage_remaining', 'count_accredited_creditors', 'total_accredited_credit_value'))

        ChoiceResult.objects.bulk_create(choice_bulk_create)
        ChoiceResult.objects.bulk_update(choice_bulk_update,
                                         fields=('count_voters', 'percentage_voters', 'count_qualified_creditors',
                                                 'total_voters_credit_value', 'total_percentage_voters',))
        return classes_processor

    @property
    def count_qualified_creditors(self):
        return self.count_qualified_creditors_from_query(self.meeting.creditors)

    @property
    def qualified_creditors(self):
        return self.parse_qualified_creditors_from_query(self.meeting.creditors)

    def count_qualified_creditors_from_query(self, creditors) -> int:
        return self.annotate_voting_id_creditors(creditors).count()

    @timeit
    def parse_qualified_creditors_from_query(self, creditors) -> list:
        choices = self.choice.values('classe', name=F('classe__description')).order_by('classe')
        for choice in choices:
            choice['choices'] = self.choice.filter(classe_id=choice['classe'])
            creditors_annotated = self.annotate_voting_id_creditors(creditors)
            choice['creditors'] = creditors_annotated.filter(classe_id=choice['classe'])
        return choices

    @timeit
    def parse_qualified_creditors_to_representative(self, creditors) -> list:
        choices = self.choice.values('classe', name=F('classe__description')).order_by('classe')
        for choice in choices:
            choice['choices'] = self.choice.filter(classe_id=choice['classe'])

            creditors_annotated = creditors.annotate(
                voting_id=Case(
                    When(votingresult__vote__voting__id=self.id, then=F('votingresult__vote__voting__id')),
                    default=Value(None),
                    output_field=UUIDField()
                )
            )
            creditors_annotated_ids = list(
                creditors_annotated.filter(voting_id=self.id).distinct().values_list('id', flat=True))

            creditors_annotated_null = list(creditors_annotated.filter(voting_id__isnull=True).exclude(
                id__in=creditors_annotated_ids).distinct().values_list('id', flat=True))

            choice['creditors'] = creditors_annotated.filter(classe_id=choice['classe']).exclude(
                id__in=creditors_annotated_ids).filter(
                Q(id__in=creditors_annotated_null, voting_id__isnull=True)).distinct()
        return choices

    def annotate_voting_id_creditors(self, creditors):
        creditors_annotated = creditors.annotate(
            voting_id=Case(
                When(votingresult__vote__voting__id=self.id, then=F('votingresult__vote__voting__id')),
                default=Value(None),
                output_field=UUIDField()
            )
        )
        creditors_annotated_ids = list(
            creditors_annotated.filter(voting_id=self.id).distinct().values_list('id', flat=True))

        creditors_annotated_null = list(creditors_annotated.filter(voting_id__isnull=True).exclude(
            id__in=creditors_annotated_ids).distinct().values_list('id', flat=True))

        return creditors_annotated.filter(
            Q(id__in=creditors_annotated_ids, voting_id=self.id) | Q(id__in=creditors_annotated_null,
                                                                     voting_id__isnull=True)).distinct()

    def get_creditors(self):
        return self.meeting.creditors.filter(classe=OuterRef('classe')).select_related('classe')

    def qualified_creditors_subquery(self):
        return Subquery(self.get_creditors()
                        .values('classe')
                        .annotate(count_qualified_creditors=Count('id')).values('count_qualified_creditors'))

    @property
    def count_qualified_representatives(self):
        return RepresentativeMeeting.objects.filter(meeting_id=self.meeting.id, representative__isnull=False).count()

    @property
    def qualified_representatives(self):
        representatives = RepresentativeMeeting.objects.filter(meeting_id=self.meeting.id, representative__isnull=False)
        creditors = self.meeting.creditors.filter(meeting__voting=self,
                                                  representative__representative__in=representatives)

        already_registered_creditors_ids = []
        for representative in representatives:
            creditors_by_representative = creditors.filter(representative__representative=representative).exclude(
                id__in=already_registered_creditors_ids)
            representative.qualified_creditors = self.parse_qualified_creditors_from_query(creditors_by_representative)
            already_registered_creditors_ids.extend(list(creditors_by_representative.values_list('id', flat=True)))

        return representatives

    def check_able_to_start_voting(self):
        ability, message = self.meeting.is_ability_to_start_voting()
        if not ability:
            raise ValidationError(message)

    def check_started_voting(self):
        if self.status != StatusVotingChoice.INICIADA:
            raise ValidationError({
                'status': _('A votação não está em progresso.')
            })
        return True

    def start_voting(self, time_extension):
        self.check_able_to_start_voting()

        if self.status == StatusVotingChoice.INICIADA:
            raise ValidationError({
                'status': _('A votação já está em progresso.')
            })

        end_date = datetime.now() + timedelta(hours=time_extension.hour, minutes=time_extension.minute,
                                              seconds=time_extension.second)

        self.status = StatusVotingChoice.INICIADA
        self.start_date = datetime.now()
        self.end_date = end_date

        Voting.objects.filter(id=self.id).update(status=StatusVotingChoice.INICIADA, start_date=datetime.now(),
                                                 end_date=end_date)
        self.scheduler_finish_voting()
        voting_start.send(sender=Voting, instance=self)
        started_update_voting_progress_detail.send(sender=Voting, instance=self)

    def extend_voting(self, time_extension):
        self.check_started_voting()
        end_date = self.end_date + timedelta(hours=time_extension.hour, minutes=time_extension.minute,
                                             seconds=time_extension.second)

        self.end_date = end_date
        self.save()
        self.scheduler_finish_voting()

    def end_voting(self):
        self.check_started_voting()
        self.status = StatusVotingChoice.ENCERRADA
        self.end_date = datetime.now()
        self.save()
        voting_end.send(sender=Voting, instance=self)

    def scheduler_finish_voting(self):
        return SCHEDULER.at(f'{self.id}-end-date', self.end_voting, self.end_date)

    def qualified_creditor(self, creditor):
        if not creditor or self.choice.filter(classe=creditor.classe).exists() is False:
            return

        creditors_voting = self.meeting.creditors.filter(id=creditor.id).select_related('classe').annotate(
            voting_id=Case(
                When(votingresult__vote__voting__id=self.id, then=F('votingresult__vote__voting__id')),
                default=Value(None),
                output_field=UUIDField()
            ))

        creditor_voting = creditors_voting.filter(voting_id=self.id).first()
        if creditor_voting:
            return creditor_voting

        return creditors_voting.first()

    def guest_choices(self, creditor):
        if creditor:
            return {'classe': creditor.classe, 'choices': self.choice.filter(classe=creditor.classe)}

    def qualified_representative(self, representative_meeting):
        creditors = []
        if representative_meeting:
            for representative in representative_meeting.get_representatives().prefetch_related('creditor'):
                if representative.able_to_vote:
                    creditors.append(representative.creditor.id)
        return self.parse_qualified_creditors_to_representative(self.meeting.creditors.filter(id__in=creditors))

    @property
    def vote_by_creditors(self):
        return VotingResult.objects.filter(vote__voting=self)

    def run_task_set_result(self):
        from apps.voting.big_number.tasks import ProcessVotingResultByIdsTask
        ProcessVotingResultByIdsTask.delay([self.id])


class Choice(models.Model):
    """
    Represents a choice option for a voting.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT)
    value = models.CharField(_('Value'), max_length=100, db_index=True)
    order = models.PositiveIntegerField(default=3, editable=False)

    def save(self, *args, **kwargs):
        self.value = map_value_choice(self.value)
        return super().save(args, kwargs)

    class Meta:
        ordering = ('order', 'created_at')
        constraints = [
            models.UniqueConstraint(fields=('value', 'voting', 'classe'), name='unique_value_choice',
                                    violation_error_message=_(
                                        "Já existe um registro com o mesmo valor da opção para essa votação."))
        ]

    def __str__(self):
        return self.value

    @property
    def qualified_creditors(self) -> int:
        return self.voting.meeting.creditors.filter(classe=self.classe).count()


class VotedByChoices(TextChoices):
    NOT_VOTING = 'N', 'Sem votante'
    BY_USER = 'D', 'Voto por um usuário do sistema'
    BY_CREDITOR = 'C', 'Voto pelo Credor'
    BY_REPRESENTATIVE = 'R', 'Voto pelo Representante'


class VotingResult(models.Model):
    """
    Represents a voting result, associating a vote with a creditor.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vote = models.ForeignKey(Choice, on_delete=models.CASCADE)
    creditor = models.ForeignKey('creditor.Creditor', on_delete=models.CASCADE)
    has_reservations = models.BooleanField(_('Há ressalvas?'), default=False)
    voted_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True)
    type = models.CharField('Tipo de Usuário que votou', max_length=1, choices=VotedByChoices.choices,
                            default=VotedByChoices.NOT_VOTING)

    def __str__(self):
        return f'{self.creditor} - {self.vote}'

    @property
    def voted_by_id(self):
        if self.voted_by:
            return self.voted_by.id

    def set_type(self):
        voted_by = self.voted_by

        if not voted_by:
            self.type = VotedByChoices.NOT_VOTING
            return

        if voted_by.id == self.creditor.guest.user.id:
            self.type = VotedByChoices.BY_CREDITOR
            return

        if self.creditor.representatives.filter(representative__guest__user=voted_by).exists():
            self.type = VotedByChoices.BY_REPRESENTATIVE
            return

        self.type = VotedByChoices.BY_USER

    def validate_unique(self, exclude=None):
        existing_votes = VotingResult.objects.exclude(id=self.id).filter(creditor=self.creditor,
                                                                         vote__voting__id=self.vote.voting.id).exists()
        if existing_votes:
            raise ValidationError(_('O credor só pode votar uma vez.'), code='unique_together')

        if self.vote.classe.id != self.creditor.classe.id:
            raise ValidationError(_('A votação deve ser apenas para sua classe.'))

        if self.creditor.meeting.id != self.vote.voting.meeting.id:
            raise ValidationError(_('O credor não está relacionado com esta assembleia'))
        return super().validate_unique()

    def save(self, *args, **kwargs):
        self.set_type()

        if not self.creditor.is_accredited:
            raise ValidationError({'is_accredited': _('O credor não foi credenciado')})
        super().save(args, kwargs)


@receiver(post_delete, sender=Voting)
def dispatch_voting_post_delete(**kwargs):
    meeting = kwargs['instance'].meeting
    update_voting_by_meeting_list.send(instance=meeting, sender=Meeting)


@receiver(post_delete, sender=Choice)
@receiver(post_save, sender=Choice)
def dispatch_voting_choice(**kwargs):
    voting = kwargs['instance'].voting
    instance = kwargs['instance']

    state_deleting_voting = getattr(instance, 'state_deleting_voting', False)

    if state_deleting_voting:
        return

    def after_commit_dispatch_voting_choice():
        try:
            update_voting_list.send(instance=voting, sender=Voting, created=False)
        except Voting.DoesNotExist as e:
            logging.error(e, exc_info=True)

    transaction.on_commit(lambda: (
        after_commit_dispatch_voting_choice()
    ))


@receiver(post_save, sender=VotingResult)
@receiver(post_delete, sender=VotingResult)
def dispatch_voting_result(instance, **kwargs):
    voting = instance.vote.voting

    def after_commit_dispatch_voting_result():
        try:
            update_voting_list.send(instance=voting, sender=Voting, created=False)
            update_creditor_detail.send(instance=instance.creditor, sender=Creditor)

            from apps.voting.tasks import SendVotingUserDetailTask
            SendVotingUserDetailTask.delay(instance.creditor.guest.user.id, voting.meeting.id, voting.id)

            from apps.voting.big_number.tasks import ProcessVotingResultTask
            ProcessVotingResultTask.delay(str(instance.creditor.id))
        except Voting.DoesNotExist as e:
            logging.error(e, exc_info=True)

    transaction.on_commit(lambda: (
        after_commit_dispatch_voting_result()
    ))


class ClasseProcessor:
    def __init__(self, classe: Classe, voting: Voting):
        self.classe = classe
        self.voting = voting
        self.creditors = self.get_creditors()

    @property
    def accredited_creditors(self):
        return self.get_accredited_creditors()

    @property
    def name(self):
        return self.classe.description

    @property
    def count_voters(self):
        return self.voting_result.count()

    @property
    def count_qualified_creditors(self):
        return self.creditors.count()

    @property
    def count_accredited_creditors(self):
        return self.accredited_creditors.count()

    @property
    def count_remaining(self) -> float:
        return self.count_qualified_creditors - self.count_voters

    @property
    def percentage_voters(self) -> float:
        if self.count_qualified_creditors > 0:
            return self.count_voters * 100.0 / self.count_qualified_creditors
        return 0

    @property
    def percentage_remaining(self) -> float:
        if self.count_qualified_creditors > 0:
            return self.count_remaining * 100.0 / self.count_qualified_creditors
        return 0

    @property
    def total_credit_value(self) -> float:
        return self.creditors.aggregate(total=Sum('credit_value'))['total'] or 0

    @property
    def total_accredited_credit_value(self) -> float:
        return self.accredited_creditors.aggregate(total=Sum('credit_value'))['total'] or 0

    @property
    def total_voters_credit_value(self) -> float:
        return self.voting_result.aggregate(total=Sum('creditor__credit_value'))['total'] or 0

    @property
    def total_remaining(self) -> float:
        return self.total_credit_value - self.total_voters_credit_value

    @property
    def total_percentage_voters(self) -> float:
        if self.total_credit_value > 0:
            return self.total_voters_credit_value * 100.0 / self.total_credit_value
        return 0

    @property
    def total_percentage_remaining(self) -> float:
        if self.total_credit_value > 0:
            return self.total_remaining * 100.0 / self.total_credit_value
        return 0

    @property
    def voting_result(self):
        return VotingResult.objects.filter(vote__voting=self.voting, vote__classe=self.classe)

    def get_creditors(self):
        return self.voting.meeting.creditors.filter(classe=self.classe.id).select_related('classe').distinct()

    def get_accredited_creditors(self):
        return self.voting.meeting.creditors.filter(classe=self.classe.id, presence__is_accredited=True).select_related(
            'classe').distinct()

    def get_data(self):
        data = {
            'classe': self.classe.id,
            'name': self.classe.description,
            'count_voters': max(self.count_voters, 0),
            'count_qualified_creditors': max(self.count_qualified_creditors, 0),
            'count_accredited_creditors': max(self.count_accredited_creditors, 0),
            'count_remaining': max(self.count_remaining, 0),
            'percentage_voters': self.percentage_voters,
            'percentage_remaining': self.percentage_remaining,
            'total_credit_value': self.total_credit_value,
            'total_accredited_credit_value': self.total_accredited_credit_value,
            'total_voters_credit_value': self.total_voters_credit_value,
            'total_remaining': self.total_remaining,
            'total_percentage_voters': self.total_percentage_voters,
            'total_percentage_remaining': self.total_percentage_remaining,
            'choices': [ChoiceProcessor(choice=choice).get_data() for choice in
                        self.voting.choice.filter(classe=self.classe)]
        }
        return data


class ChoiceProcessor:
    def __init__(self, choice: Choice):
        self.choice = choice
        self.classe = self.choice.classe
        self.voting = self.choice.voting
        self.creditors = self.get_creditors()

    @property
    def value(self):
        return self.choice.value

    def get_creditors(self):
        return self.voting.meeting.creditors.filter(classe=self.classe).select_related('classe')

    @property
    def voting_result(self):
        return VotingResult.objects.filter(vote=self.choice, vote__classe=self.classe)

    @property
    def count_voters(self):
        return self.voting_result.count()

    @property
    def count_qualified_creditors(self):
        return self.creditors.count()

    @property
    def percentage_voters(self) -> float:
        if self.count_qualified_creditors > 0:
            return self.count_voters * 100.0 / self.count_qualified_creditors
        return 0

    @property
    def total_voters_credit_value(self) -> float:
        return self.voting_result.aggregate(total=Sum('creditor__credit_value'))['total'] or 0

    @property
    def total_credit_value(self) -> float:
        return self.creditors.aggregate(total=Sum('credit_value'))['total'] or 0

    @property
    def total_percentage_voters(self) -> float:
        if self.total_voters_credit_value > 0:
            return self.total_voters_credit_value * 100.0 / self.total_credit_value
        return 0

    def get_data(self):
        data = {
            'choice_id': self.choice.id,
            'value': self.value,
            'count_voters': self.count_voters,
            'percentage_voters': self.percentage_voters,
            'total_voters_credit_value': self.total_voters_credit_value,
            'total_percentage_voters': self.total_percentage_voters,
        }
        return data