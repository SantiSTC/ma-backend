from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class Doctor(models.Model):
    """Perfil de Doctor"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        'users.User',  # ← String reference
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name=_('usuario')
    )
    
    license_number = models.CharField(
        _('número de matrícula'),
        max_length=50,
        unique=True,
        help_text=_('Número de matrícula profesional')
    )
    
    university = models.CharField(_('universidad'), max_length=200, blank=True)
    bio = models.TextField(_('biografía'), blank=True)
    
    # Ubicación
    address = models.CharField(_('dirección'), max_length=255, blank=True)
    latitude = models.DecimalField(
        _('latitud'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text=_('Ej: -34.6037')
    )
    longitude = models.DecimalField(
        _('longitud'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text=_('Ej: -58.3816')
    )
    
    image_url = models.URLField(_('foto de perfil'), max_length=500, blank=True)
    is_active = models.BooleanField(_('activo'), default=True)
    deleted_at = models.DateTimeField(_('fecha de eliminación'), null=True, blank=True)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('última actualización'), auto_now=True)
    
    class Meta:
        verbose_name = _('doctor')
        verbose_name_plural = _('doctores')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['license_number']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"