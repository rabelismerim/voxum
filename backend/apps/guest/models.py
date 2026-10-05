from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import TextChoices

from core.abstract.models import AbstractModel
from utils import _
from apps.voxum_base.models import Entity


class MsalGuestStatusChoices(TextChoices):
    IN_LINE = 'L', _('Aguardando processamento')
    ACTIVE = 'A', _('Ativo')


class UserGuest(AbstractModel):
    """
    Model representing a guest profile.

    Attributes:
        user (OneToOneField): The associated user object.
        entity (ForeignKey): The associated entity object.
        is_representative (BooleanField): If user is representative.
    """
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, verbose_name=_('Usuário'))
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT, verbose_name=_('Entidade'))
    is_representative = models.BooleanField(_('Pode ser representante?'), default=False)
    status = models.CharField(_('Status'), max_length=50, blank=True, null=True)
    invitation_link = models.URLField(_('Link de convite'), blank=True, null=True)

    def __str__(self):
        return str(self.user)


@receiver(pre_save, sender=UserGuest)
def check_status_change(**kwargs):
    """
    Signal handler that checks for changes in the UserGuest instance
    before it is saved.
    """
    instance = kwargs['instance']
    created = kwargs.get('created', instance.id is None)

    if not created:
        previous_instance = UserGuest.objects.filter(id=instance.id).first()
        if not previous_instance:
            return

        if previous_instance.status != instance.status or previous_instance.invitation_link != instance.invitation_link:
            transaction.on_commit(lambda: execute_action_on_status_change(instance))


def execute_action_on_status_change(instance):
    """
    Executes an action when the status or invitation link of the
    UserGuest instance changes.
    """
    from apps.creditor.tasks import GuestUpdateCreditorRepresentativesDetailTask
    GuestUpdateCreditorRepresentativesDetailTask.delay(str(instance.id))