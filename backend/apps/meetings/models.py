from django.db import models
from apps.creditors.models import RecoveringCompany


class MeetingType(models.TextChoices):
    FIRST_CALL = '1_CALL', '1ª Convocação'
    SECOND_CALL = '2_CALL', '2ª Convocação'
    CONTINUATION = 'CONTINUATION', 'Continuação'


class MeetingStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Agendada'
    IN_PROGRESS = 'IN_PROGRESS', 'Em Andamento'
    PAUSED = 'PAUSED', 'Suspensa / Pausada'
    FINISHED = 'FINISHED', 'Encerrada'
    CANCELLED = 'CANCELLED', 'Cancelada'


class Meeting(models.Model):
    """Assembleia Geral de Credores (AGC)."""
    recovering_company = models.ForeignKey(
        RecoveringCompany, 
        on_delete=models.CASCADE, 
        related_name='meetings'
    )
    title = models.CharField("Título da Assembleia", max_length=255)
    call_type = models.CharField("Convocação", max_length=20, choices=MeetingType.choices)
    status = models.CharField("Status", max_length=20, choices=MeetingStatus.choices, default=MeetingStatus.SCHEDULED)
    
    start_date = models.DateTimeField("Data / Hora de Início")
    end_date = models.DateTimeField("Data / Hora do Encerramento", null=True, blank=True)
    
    # Integrações externas (ex: Zoom / Videoconferência)
    meeting_link = models.URLField("Link da Transmissão", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Assembleia"
        verbose_name_plural = "Assembleias"

    def __str__(self):
        return f"{self.title} - {self.get_call_type_display()} ({self.get_status_display()})"