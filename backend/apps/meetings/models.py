import uuid
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.abstract.models import AbstractDescription, AbstractModel
from apps.guest.models import UserGuest


class StatusMeetingChoices(models.TextChoices):
    SCHEDULED = 'S', _('Agendada')
    INITIALIZED = 'I', _('Iniciada')
    SUSPENDED = 'P', _('Suspensa')
    FINISHED = 'F', _('Encerrada')


class StatusQuorum(models.TextChoices):
    FIRST_CALL = 'F', _('Primeira convocação')
    SECOND_CALL = 'S', _('Segunda convocação')
    REACHED = 'R', _('Quórum atingido')
    NOT_REACHED = 'N', _('Quórum não atingido')


class SituationMeetingChoices(models.TextChoices):
    REGULAR = 'R', _('Regular')
    SUSPENDED = 'S', _('Suspensa')


class Classe(AbstractDescription):
    class Meta:
        ordering = ('description',)

    def __str__(self):
        return self.description


class MeetingGroup(AbstractModel):
    name = models.CharField(max_length=255)

    def count_meetings(self):
        return self.meetings.count()

    def __str__(self):
        return self.name


class Meeting(AbstractModel):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(
        'location.Location',
        on_delete=models.PROTECT,
        related_name='meetings',
    )
    start_date = models.DateTimeField()
    description = models.TextField(blank=True)
    zoom_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=1,
        choices=StatusMeetingChoices.choices,
        default=StatusMeetingChoices.SCHEDULED,
    )
    status_quorum = models.CharField(
        max_length=1,
        choices=StatusQuorum.choices,
        default=StatusQuorum.FIRST_CALL,
    )
    situation = models.CharField(
        max_length=1,
        choices=SituationMeetingChoices.choices,
        default=SituationMeetingChoices.REGULAR,
    )
    meeting_group = models.ForeignKey(
        MeetingGroup,
        on_delete=models.SET_NULL,
        related_name='meetings',
        null=True,
        blank=True,
    )
    meeting_reference = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='follow_up_meetings',
        null=True,
        blank=True,
    )
    order = models.PositiveIntegerField(default=1)
    installed = models.BooleanField(default=False)
    presence_registration_started_at = models.DateTimeField(null=True, blank=True)
    presence_registration_deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-start_date', '-created_at')

    def __str__(self):
        return self.name

    @property
    def creditors(self):
        return self.creditor_set.all()

    @property
    def count_creditors(self):
        return self.creditors.count()

    @property
    def count_representatives(self):
        return self.representativemeeting_set.count()

    @property
    def total_credit(self):
        return self.creditors.aggregate(total=models.Sum('credit_value'))['total'] or 0

    @property
    def has_quorum(self):
        return self.total_credit > 0 and self.creditors.filter(presence__is_present=True).exists()

    @property
    def creditors_presence_status(self):
        return []

    @property
    def creditors_credit(self):
        return []

    @property
    def situation_display(self):
        return self.get_situation_display()

    @property
    def available_to_enter(self):
        deadline = self.presence_registration_deadline
        return deadline is not None and timezone.now() <= deadline

    def get_meeting_group(self):
        if self.meeting_group_id:
            return self.meeting_group
        group = MeetingGroup.objects.create(name=self.name)
        self.meeting_group = group
        self.save(update_fields=('meeting_group', 'updated_at'))
        return group

    def start_register_presence_voting(self, duration):
        now = timezone.now()
        self.presence_registration_started_at = now
        self.presence_registration_deadline = timezone.make_aware(
            datetime.combine(now.date(), duration),
            timezone.get_current_timezone(),
        )
        if self.presence_registration_deadline <= now:
            self.presence_registration_deadline += timedelta(days=1)
        self.status = StatusMeetingChoices.INITIALIZED
        self.save()

    def extend_register_presence_voting(self, duration):
        now = timezone.now()
        self.presence_registration_deadline = timezone.make_aware(
            datetime.combine(now.date(), duration),
            timezone.get_current_timezone(),
        )
        if self.presence_registration_deadline <= now:
            self.presence_registration_deadline += timedelta(days=1)
        self.save(update_fields=('presence_registration_deadline', 'updated_at'))

    def end_register_presence_voting(self):
        self.presence_registration_deadline = timezone.now()
        self.save(update_fields=('presence_registration_deadline', 'updated_at'))

    def get_is_ability_to_create_voting_errors(self):
        errors = []
        if self.status != StatusMeetingChoices.INITIALIZED:
            errors.append(_('A assembleia não está em andamento.'))
        if not self.has_quorum:
            errors.append(_('A assembleia ainda não atingiu quórum.'))
        return errors

    def finish(self):
        self.status = StatusMeetingChoices.FINISHED
        self.save(update_fields=('status', 'updated_at'))

    def suspend(self):
        self.status = StatusMeetingChoices.SUSPENDED
        self.situation = SituationMeetingChoices.SUSPENDED
        self.save(update_fields=('status', 'situation', 'updated_at'))

    def duplicate_meeting(self):
        return self


def get_new_representative_code():
    from apps.meetings.models import RepresentativeMeeting

    for _attempt in range(5):
        code = 100000 + uuid.uuid4().int % 900000
        if not RepresentativeMeeting.objects.filter(code=code).exists():
            return code
    raise RuntimeError('Could not generate a unique representative code.')


class RepresentativeMeeting(AbstractModel):
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='representativemeeting_set',
    )
    guest = models.ForeignKey(
        UserGuest,
        on_delete=models.CASCADE,
        related_name='meeting_representatives',
    )
    code = models.PositiveIntegerField(default=get_new_representative_code, unique=True)
    doc_ok = models.BooleanField(default=False)
    meeting_invited = models.BooleanField(default=False)

    class Meta:
        unique_together = ('meeting', 'guest')
        ordering = ('guest__user__first_name', 'created_at')

    def __str__(self):
        return str(self.guest)

    @property
    def online(self):
        return self.get_representative_by_meeting_id(self.meeting_id).online

    @property
    def is_accredited(self):
        representative = self.get_representative_by_meeting_id(self.meeting_id)
        return bool(representative and representative.creditor.is_accredited)

    def get_representatives(self):
        from apps.creditor.models import Representative

        return Representative.objects.filter(representative=self)

    def get_representative_by_meeting_id(self, meeting_id):
        return self.get_representatives().filter(creditor__meeting_id=meeting_id).first()

    def get_big_numbers(self, voting_id):
        creditors = self.get_representatives().values_list('creditor_id', flat=True)
        total = len(creditors)
        from apps.voting.models import VotingResult

        voted = VotingResult.objects.filter(
            voting_id=voting_id,
            creditor_id__in=creditors,
        ).count()
        return {
            'count_voters': voted,
            'count_not_voted': max(total - voted, 0),
            'total_credit_value': 0,
            'total_voters_credit_value': 0,
            'percentage_voters': (voted / total * 100) if total else 0,
            'total_percentage_voters': (voted / total * 100) if total else 0,
        }


class UserMeeting(AbstractModel):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='user_meetings')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='meeting_roles')
    groups = models.ManyToManyField(Group, blank=True, related_name='meeting_roles')

    class Meta:
        unique_together = ('meeting', 'user')

    def __str__(self):
        return f'{self.user} - {self.meeting}'
