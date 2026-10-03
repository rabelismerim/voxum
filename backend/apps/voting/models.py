from django.db import models
from apps.meetings.models import Meeting
from apps.creditors.models import Creditor, Representative, CreditorClass


class PollStatus(models.TextChoices):
    NOT_STARTED = 'NOT_STARTED', 'Não Iniciada'
    OPEN = 'OPEN', 'Em Andamento'
    CLOSED = 'CLOSED', 'Encerrada'
    CANCELLED = 'CANCELLED', 'Cancelada'


class VoteChoice(models.TextChoices):
    YES = 'YES', 'Sim / A favor'
    NO = 'NO', 'Não / Contra'
    ABSTAIN = 'ABSTAIN', 'Abstenção'


class Poll(models.Model):
    """Votação / Deliberação criada dentro de uma assembleia."""
    meeting = models.ForeignKey(
        Meeting, 
        on_delete=models.CASCADE, 
        related_name='polls'
    )
    title = models.CharField("Título / Objeto da Votação", max_length=255)
    description = models.TextField("Descrição / Detalhes", blank=True, null=True)
    status = models.CharField("Status", max_length=20, choices=PollStatus.choices, default=PollStatus.NOT_STARTED)
    
    opened_at = models.DateTimeField("Abertura", null=True, blank=True)
    closed_at = models.DateTimeField("Encerramento", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Votação"
        verbose_name_plural = "Votações"

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class Vote(models.Model):
    """Registo individual do voto de um credor."""
    poll = models.ForeignKey(
        Poll, 
        on_delete=models.CASCADE, 
        related_name='votes'
    )
    creditor = models.ForeignKey(
        Creditor, 
        on_delete=models.CASCADE, 
        related_name='votes'
    )
    representative = models.ForeignKey(
        Representative, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='votes'
    )
    
    choice = models.CharField("Opção de Voto", max_length=10, choices=VoteChoice.choices)
    
    # Snapshot dos dados do credor no momento do voto para auditoria
    creditor_class = models.CharField("Classe no Momento do Voto", max_length=20, choices=CreditorClass.choices)
    credit_value = models.DecimalField("Valor do Crédito no Momento", max_digits=15, decimal_places=2)
    
    voted_at = models.DateTimeField("Data/Hora do Voto", auto_now_add=True)

    class Meta:
        verbose_name = "Voto"
        verbose_name_plural = "Votos"
        unique_together = ('poll', 'creditor')

    def __str__(self):
        return f"{self.creditor.name} - {self.get_choice_display()} ({self.poll.title})"