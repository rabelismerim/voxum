import datetime

from core.abstract.exceptions import ValidationErrorAdapter
from core.abstract.models import AbstractModel
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils import timezone
from utils import _, get_user_model

from apps.voxum_base.utils import receiver_commit
from apps.creditor.models import Creditor, Representative
from apps.web_sockets.signals import update_creditor_detail, signal_meeting_detail


class AbstractPresence(AbstractModel):
    arrival_date = models.DateTimeField(_('Data e hora de chegada'), blank=True, null=True)
    departure_date = models.DateTimeField(_('Data e hora de saída'), blank=True, null=True)
    departure_reason = models.TextField(_('Motivo da saída'), blank=True, null=True)
    is_present = models.BooleanField(_('Está presente'), default=False)

    def register_departure_date(self, departure_reason=None):
        if not self.arrival_date:
            raise ValidationErrorAdapter({'arrival_date': _('Chegada não registrada')})
        if self.departure_date:
            raise ValidationErrorAdapter({'departure_date': _('Saida já registrada')})
        self.departure_date = timezone.now()
        self.departure_reason = departure_reason
        self.is_present = True
        self.save()

    class Meta:
        abstract = True


class Presence(AbstractPresence):
    creditor = models.OneToOneField(Creditor, on_delete=models.CASCADE)
    is_accredited = models.BooleanField(_('O Credor está está credenciado'), default=False)
    accredited_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True)
    accredited_date = models.DateTimeField(_('Data e hora do credenciamento'), null=True, blank=True)

    def __str__(self):
        return f"{self.creditor} - {self.is_present} - {self.is_accredited}"

    def validate_unique(self, exclude=None):
        if Presence.objects.filter(creditor=self.creditor).exclude(id=self.id).exists():
            raise ValidationErrorAdapter(_('Presença já registrada'))

        if self.arrival_date and self.departure_date and self.departure_date < self.arrival_date:
            raise ValidationErrorAdapter(
                {'arrival_date': _('A data de saida não pode ser menor do que a data de chegada')})

        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        save = super().save(*args, **kwargs)
        signal_meeting_detail.send(instance=self.creditor.meeting, sender=self.creditor.meeting.__class__)
        return save

    def register_accreditation(self, user):
        self.creditor.meeting.check_able_to_register_presence()
        if self.is_accredited:
            raise ValidationErrorAdapter({'is_accredited': _('Credenciamento já realizado')})
        self.is_accredited = True
        self.accredited_date = datetime.datetime.now()
        self.accredited_by = user
        self.save()


class PresenceRepresentative(AbstractPresence):
    representative = models.OneToOneField(Representative, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.representative} - {self.is_present}"

    def validate_unique(self, exclude=None):
        if self.arrival_date and self.departure_date and self.departure_date < self.arrival_date:
            raise ValidationErrorAdapter(
                {'arrival_date': _('A data de saida não pode ser menor do que a data de chegada')})

        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        if PresenceRepresentative.objects.filter(representative_id=self.representative.id).exclude(id=self.id).exists():
            raise ValidationErrorAdapter(_('Presença já registrada'))

        return super().save(*args, **kwargs)

    def register_departure_date(self, departure_reason=None):
        if not self.arrival_date:
            raise ValidationErrorAdapter({'arrival_date': _('Chegada não registrada')})
        if self.departure_date:
            raise ValidationErrorAdapter({'departure_date': _('Saida já registrada')})
        self.departure_date = timezone.now()
        self.departure_reason = departure_reason
        self.is_present = True
        self.save()


@receiver_commit(post_save, sender=Presence)
@receiver_commit(post_delete, sender=Presence)
def dispatch_presence(instance, **kwargs):
    update_creditor_detail.send(instance=instance.creditor, sender=Creditor)
    from apps.creditor.tasks import SendCreditorUserGuestDetailTask
    SendCreditorUserGuestDetailTask.delay(instance.creditor.guest.user.id, instance.creditor.meeting.id)