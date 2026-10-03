from django.db import models
from apps.meetings.models import Meeting
from apps.creditors.models import Creditor, Representative


class Attendance(models.Model):
    """Registro de quórum/presença de um credor numa assembleia."""
    meeting = models.ForeignKey(
        Meeting, 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    creditor = models.ForeignKey(
        Creditor, 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    representative = models.ForeignKey(
        Representative, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='attendances'
    )
    
    is_present = models.BooleanField("Presente", default=True)
    signed_in_at = models.DateTimeField("Data/Hora de Entrada", auto_now_add=True)
    signed_out_at = models.DateTimeField("Data/Hora de Saída", null=True, blank=True)

    class Meta:
        verbose_name = "Presença"
        verbose_name_plural = "Presenças"
        unique_together = ('meeting', 'creditor')

    def __str__(self):
        status = "Presente" if self.is_present else "Ausente"
        return f"{self.creditor.name} na {self.meeting.title} - {status}"