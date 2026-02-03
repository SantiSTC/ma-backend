from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Patient(models.Model):
    """Perfil de Paciente"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='patient_profile',
        verbose_name=_('usuario')
    )
    
    dni = models.CharField(_('DNI'), max_length=20, unique=True)
    birth_date = models.DateField(_('fecha de nacimiento'), null=True, blank=True)
    insurance_provider = models.CharField(_('obra social/prepaga'), max_length=100, blank=True)
    insurance_plan = models.CharField(_('plan'), max_length=100, blank=True)
    insurance_number = models.CharField(_('número de afiliado'), max_length=50, blank=True)
    image_url = models.URLField(_('foto de perfil'), max_length=500, blank=True)
    deleted_at = models.DateTimeField(_('fecha de eliminación'), null=True, blank=True)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('última actualización'), auto_now=True)
    
    class Meta:
        verbose_name = _('paciente')
        verbose_name_plural = _('pacientes')
        ordering = ['-created_at']
        indexes = [models.Index(fields=['dni'])]
    
    def __str__(self):
        return f"Paciente: {self.user.get_full_name()}"
    
    @property
    def age(self):
        """Calcula la edad del paciente"""
        if not self.birth_date:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )