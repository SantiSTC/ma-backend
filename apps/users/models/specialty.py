from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Specialty(models.Model):
    """Especialidades médicas"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('nombre'), max_length=100, unique=True)
    description = models.TextField(_('descripción'), blank=True)
    
    doctors = models.ManyToManyField(
        'users.Doctor',
        related_name='specialties',
        verbose_name=_('doctores'),
        blank=True
    )
    
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('especialidad')
        verbose_name_plural = _('especialidades')
        ordering = ['name']
    
    def __str__(self):
        return self.name