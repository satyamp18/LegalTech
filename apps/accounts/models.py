from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        LAWYER = 'LAWYER', _('Lawyer')
        PARALEGAL = 'PARALEGAL', _('Paralegal')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.LAWYER,
        help_text=_('Designates the access role and authority of the user within LexVision AI.')
    )
    department = models.CharField(max_length=100, blank=True, null=True, default='Legal Department')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_lawyer(self):
        return self.role == self.Role.LAWYER or self.is_admin

    @property
    def is_paralegal(self):
        return self.role == self.Role.PARALEGAL or self.is_lawyer or self.is_admin

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
