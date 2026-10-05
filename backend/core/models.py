from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


STATUS_CHOICES = (
    ('A', _('Ativo')),
    ('I', _('Inativo')),
    ('P', _('Pendente')),
    ('R', _('Rejeitado')),
    ('V', _('Férias')),
)


class User(AbstractUser):
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    userpicture = models.URLField(blank=True)
    user_img = models.ImageField(upload_to='users/', blank=True)
    login_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_img_url(self):
        if self.user_img:
            return self.user_img.url
        return self.userpicture

    def dict_update(self, **values):
        for field, value in values.items():
            setattr(self, field, value)
        self.save()
        return self