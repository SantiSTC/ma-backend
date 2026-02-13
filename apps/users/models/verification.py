from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random
import string


class EmailVerification(models.Model):
    """
    Códigos de verificación de email con código de 6 dígitos
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='email_verifications',
        verbose_name=_('usuario')
    )
    
    code = models.CharField(
        _('código'),
        max_length=6,
        help_text=_('Código de 6 dígitos')
    )
    
    # Expiración
    created_at = models.DateTimeField(
        _('fecha de creación'),
        auto_now_add=True
    )
    expires_at = models.DateTimeField(
        _('expira en')
    )
    
    # Estado
    is_used = models.BooleanField(
        _('usado'),
        default=False
    )
    used_at = models.DateTimeField(
        _('usado en'),
        null=True,
        blank=True
    )
    
    # IP (para seguridad)
    ip_address = models.GenericIPAddressField(
        _('dirección IP'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('verificación de email')
        verbose_name_plural = _('verificaciones de email')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'is_used']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.code} ({'usado' if self.is_used else 'activo'})"
    
    def save(self, *args, **kwargs):
        # Generar código si no existe
        if not self.code:
            self.code = self.generate_code()
        
        # Setear expiración si no existe
        if not self.expires_at:
            minutes = getattr(settings, 'VERIFICATION_CODE_EXPIRY_MINUTES', 15)
            self.expires_at = timezone.now() + timedelta(minutes=minutes)
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_code(length=6):
        """
        Genera código numérico de N dígitos
        """
        return ''.join(random.choices(string.digits, k=length))
    
    @property
    def is_valid(self):
        """
        Verifica si el código es válido (no usado y no expirado)
        """
        if self.is_used:
            return False
        
        if timezone.now() > self.expires_at:
            return False
        
        return True
    
    @property
    def is_expired(self):
        """
        Verifica si el código expiró
        """
        return timezone.now() > self.expires_at
    
    def verify(self):
        """
        Marca el código como usado
        """
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    @classmethod
    def create_for_user(cls, user, ip_address=None):
        """
        Crea un nuevo código de verificación para un usuario
        Invalida códigos anteriores no usados
        """
        # Invalidar códigos anteriores no usados
        cls.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)
        
        # Crear nuevo código
        return cls.objects.create(
            user=user,
            ip_address=ip_address
        )
    
    @classmethod
    def verify_code(cls, user, code):
        """
        Verifica un código para un usuario
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Buscar código más reciente
        verification = cls.objects.filter(
            user=user,
            code=code,
            is_used=False
        ).order_by('-created_at').first()
        
        if not verification:
            return False, "Código inválido"
        
        if verification.is_expired:
            return False, "Código expirado"
        
        # Marcar como usado
        verification.verify()
        
        return True, "Código verificado exitosamente"