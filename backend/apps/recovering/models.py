from core.abstract.models import AbstractModel
from django.db import models
from utils import _


class Recovering(AbstractModel):
    name = models.CharField(_('Name'), max_length=150, unique=True, db_index=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        return super().save(*args, **kwargs)