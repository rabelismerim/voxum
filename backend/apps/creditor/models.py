import datetime
import logging

from apps.voxum_base.exceptions import ValidationErrorAdapter
from apps.voxum_base.models import AbstractModel
from django.db import models, transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template.defaultfilters import capfirst
from rest_framework.exceptions import ValidationError

from utils import _

from apps.voxum_base.models import Coin
from apps.voxum_base.utils import get_new_code, receiver_commit, get_legal_number
from apps.guest.schemas import generate_unique_number
from apps.recovering.models import Recovering
from apps.guest.models import UserGuest
from apps.web_sockets.signals import user_connected, user_disconnected, signal_meeting_detail


CHOICES_TYPE_PERSON = (('F', _('Física')), ('J', _('Jurídica')), ('O', _('Outro')))


def get_new_creditor_code(additional_legal_number=None):
    creditors = Creditor.objects.all()
    for count in range(1, 6):
        new_code = get_new_code()

        if additional_legal_number:
            new_code = f'{new_code}{generate_unique_number(get_legal_number(additional_legal_number))}'

        if not creditors.filter(code=new_code).exists():
            return new_code


class NonDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Creditor(AbstractModel):
    objects = NonDeletedManager()
    objects_admin = models.Manager()
    meeting = models.ForeignKey('meetings.Meeting', on_delete=models.CASCADE)
    guest = models.ForeignKey(UserGuest, on_delete=models.CASCADE)
    recovering = models.ForeignKey(Recovering, on_delete=models.CASCADE)
    classe = models.ForeignKey('meetings.Classe', on_delete=models.PROTECT, db_index=True)
    coin = models.ForeignKey(Coin, on_delete=models.PROTECT)

    type_person = models.CharField(max_length=1, choices=CHOICES_TYPE_PERSON)
    credit_value = models.FloatField()
    converted_value = models.FloatField(default=0)
    exchange_tax = models.FloatField(default=0)
    contested_value = models.FloatField(default=0)
    online = models.BooleanField(_('Está online?'), default=False)
    priority = models.PositiveIntegerField(_('Priority'), default=0)

    code = models.BigIntegerField(unique=True, default=get_new_creditor_code, editable=False)

    meeting_invited = models.BooleanField(default=False)
    doc_ok = models.BooleanField(_('Documentação ok?'), default=False)
    is_deleted = models.BooleanField(_('Soft delete'), default=False)

    def __str__(self):
        return str(self.guest)

    def save(self, *args, **kwargs):
        retries = 5
        for i in range(retries):
            try:
                return super().save(*args, **kwargs)
            except Exception as e:
                if str(e).count('creditor_creditor_code_key') > 0 or str(e).count(
                        'creditor_creditor.code') > 0:
                    code = f'{get_new_creditor_code(self.legal_number)}'
                    self.code = code
                else:
                    raise e

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == ('meeting', 'guest', 'classe'):
            opts = model_class._meta
            params = {
                "model": self,
                "model_class": model_class,
                "model_name": capfirst(opts.verbose_name),
                "unique_check": unique_check,
            }
            return ValidationErrorAdapter(
                message=_('Um Credor para esse Usuário convidado, classe e Assembleia já foi registrado'),
                code="unique_together",
                params=params,
            )
        return super().unique_error_message(model_class, unique_check)

    class Meta:
        unique_together = ('meeting', 'guest', 'classe')
        ordering = ('guest__user__first_name', 'created_at')

    def get_presence(self):
        return getattr(self, 'presence', None)

    def get_accredited_name(self):
        if self.presence_ and self.presence_.accredited_by:
            return self.presence_.accredited_by.get_full_name()
        return '-'

    @property
    def legal_number(self):
        return self.guest.entity.legal_number

    @property
    def result(self):
        return self.get_result()

    def get_result_by_id(self, voting_id):
        vt = self.votingresult_set.filter(vote__voting__id=voting_id).first()
        return vt

    def get_votes(self):
        return self.votingresult_set.all().select_related()

    @property
    def representatives(self):
        return self.representative_set.all().select_related()

    def get_representatives_meeting(self, **kwargs):
        representatives = self.representative_set.filter(**kwargs).select_related('representative')
        return {rep.representative for rep in representatives}

    def change_status(self, status: bool):
        if self.online != status:
            self.online = status
            if not self.online:
                self.register_departure_date()
            else:
                self.register_connection_date()
            self.save()

    def reset_meeting_invite(self):
        self.meeting_invited = False
        self.save()
        representative = self.representatives.filter(representative__meeting=self.meeting_id).first()
        if representative:
            representative_meeting = representative.representative
            representative_meeting.meeting_invited = False
            representative_meeting.save()

    @property
    def presence_(self):
        return self.get_presence()

    @property
    def is_presente(self) -> bool:
        presence = self.get_presence()
        if not presence:
            return False
        return presence.is_present

    @property
    def has_account(self):
        return True if self.guest.user.email else False

    @property
    def is_accredited(self) -> bool:
        presence = self.get_presence()
        return presence.is_accredited if presence else False

    def register_departure_date(self):
        try:
            self.presence_.register_departure_date()
        except (ValidationError, AttributeError, ValidationErrorAdapter) as e:
            logging.error(e, exc_info=True)

    def register_connection_date(self):
        if not self.get_presence():
            from apps.presence.models import Presence
            Presence.objects.update_or_create(creditor=self,
                                              defaults={'is_present': True, 'arrival_date': datetime.datetime.now()})

    @property
    def able_to_vote(self) -> bool:
        if not self.is_accredited or not self.has_account or not self.online:
            return False

        lowest_representative_priority = self.representatives.filter(online=True).order_by('priority').first()

        if lowest_representative_priority:
            return self.priority <= lowest_representative_priority.priority
        return True

    def dispatch_signal_representatives(self, not_representative_id=None):
        representatives = self.representatives
        if not_representative_id:
            representatives = representatives.exclude(id=not_representative_id)
        for representative in representatives:
            post_save.send(sender=Representative, instance=representative)

    def get_votings(self):
        return self.meeting.voting_set.all()

    @property
    def value_to_update_change(self):
        return ['credit_value', 'classe']

    def get_available_representatives_receive_meeting_link(self):
        return self.representative_set.filter(is_deleted=False, representative__doc_ok=True).distinct()


class Representative(AbstractModel):
    objects = NonDeletedManager()
    objects_admin = models.Manager()

    priority = models.PositiveIntegerField(_('Priority'))
    representative = models.ForeignKey('meetings.RepresentativeMeeting', on_delete=models.CASCADE)
    creditor = models.ForeignKey(Creditor, on_delete=models.CASCADE)
    online = models.BooleanField(_('Está online?'), default=False)
    is_deleted = models.BooleanField(_('Soft delete'), default=False)

    @property
    def doc_ok(self):
        return self.representative.doc_ok

    @property
    def able_to_vote(self):
        if not self.online or not self.creditor.is_accredited or not self.doc_ok:
            return False

        lowest_representative = Representative.objects.filter(creditor=self.creditor, online=True,
                                                              representative__meeting=self.representative.meeting).exclude(
            id=self.id).order_by('priority').first()

        return ((self.priority <= self.creditor.priority or not self.creditor.online)
                and (not lowest_representative or self.priority <= lowest_representative.priority))

    class Meta:
        unique_together = ('representative', 'creditor')
        ordering = ('representative__guest__user__first_name', 'created_at')

    @property
    def legal_number(self):
        return self.representative.guest.entity.legal_number

    def validate_unique(self, exclude=None):
        if self.representative.meeting.id != self.creditor.meeting.id:
            raise ValidationErrorAdapter(
                {'creditor': _('Este representante não está cadastrado na mesma Assembleia do credor')})

        if self.creditor.guest.entity.legal_number == self.legal_number:
            raise ValidationErrorAdapter(_('O Usuário convidado não pode ser representante dele mesmo'))

        return super().validate_unique(exclude)

    def __str__(self):
        return str(self.representative.guest)

    @property
    def presence_(self):
        return self.get_presence()

    def get_presence(self):
        return getattr(self, 'presencerepresentative', None)

    def register_departure_date(self):
        try:
            self.presence_.register_departure_date()
        except (ValidationError, AttributeError, ValidationErrorAdapter) as e:
            logging.error(e, exc_info=True)

    def register_connection_date(self):
        if not self.get_presence():
            from apps.presence.models import PresenceRepresentative
            now = datetime.datetime.now()
            PresenceRepresentative.objects.update_or_create(representative=self, defaults={'is_present': True,
                                                                                           'arrival_date': now})

    def change_status(self, status: bool):
        if self.online != status:
            self.online = status
            if not self.online:
                self.register_departure_date()
            else:
                self.register_connection_date()
            self.save()

    def dispatch_signal_creditor(self):
        post_save.send(sender=Creditor, instance=self.creditor)

    def qualified_creditors(self):
        pass


def update_status_creditor(instance, status: bool, **kwargs):
    meeting_id = kwargs.get('meeting_id')
    creditors = Creditor.objects.filter(guest__user=instance, meeting_id=meeting_id)

    for creditor in creditors:
        creditor.change_status(status)
        creditor.guest.register_access()
        creditor.dispatch_signal_representatives()


def update_status_representative(instance, status: bool, **kwargs):
    meeting_id = kwargs.get('meeting_id')
    representatives = Representative.objects.filter(representative__guest__user=instance,
                                                    representative__meeting_id=meeting_id)

    for representative in representatives:
        representative.change_status(status)
        representative.representative.guest.register_access()
        representative.creditor.dispatch_signal_representatives(representative.id)
        representative.dispatch_signal_creditor()


@receiver(user_connected)
def dispatch_user_connected(instance, **kwargs):
    update_status_creditor(instance, True, **kwargs)
    update_status_representative(instance, True, **kwargs)

    from apps.voting.tasks import SendVotingUserDetailTask
    from apps.creditor.tasks import SendCreditorUserGuestDetailTask
    SendVotingUserDetailTask.delay(instance.id, kwargs.get('meeting_id'))
    SendCreditorUserGuestDetailTask.delay(instance.id, kwargs.get('meeting_id'))


@receiver(user_disconnected)
def dispatch_user_disconnected(instance, **kwargs):
    update_status_creditor(instance, False, **kwargs)
    update_status_representative(instance, False, **kwargs)
    from apps.voting.tasks import SendVotingUserDetailTask
    from apps.creditor.tasks import SendCreditorUserGuestDetailTask
    SendVotingUserDetailTask.delay(instance.id, kwargs.get('meeting_id'))
    SendCreditorUserGuestDetailTask.delay(instance.id, kwargs.get('meeting_id'))


@receiver_commit(post_save, sender=Creditor)
def dispatch_creditor_save(instance, **kwargs):
    from apps.creditor.tasks import SendCreditorUserGuestDetailTask
    from apps.voting.big_number.tasks import ProcessVotingResultTask

    fields_changed = instance.diff

    SendCreditorUserGuestDetailTask.delay(instance.guest.user.id, instance.meeting.id)

    if kwargs.get('created'):
        ProcessVotingResultTask.delay(str(instance.id))
        signal_meeting_detail.send(instance=instance.meeting, sender=instance.meeting.__class__)
        return

    for field in instance.value_to_update_change:
        if field in fields_changed:
            ProcessVotingResultTask.delay(str(instance.id))
            break


@receiver(post_delete, sender=Creditor)
def process_after_delete(sender, instance: Creditor, **kwargs):
    if instance.is_accredited:
        raise ValidationErrorAdapter(_('Não é possível remover o Credor quando ele já está credenciado.'))

    from apps.voting.big_number.tasks import ProcessVotingResultByIdsTask
    votings_ids = instance.get_votings().values_list('id', flat=True)
    meeting = instance.meeting

    transaction.on_commit(lambda: (
        signal_meeting_detail.send(instance=meeting, sender=meeting.__class__),
        ProcessVotingResultByIdsTask.delay(list(votings_ids))
    ))