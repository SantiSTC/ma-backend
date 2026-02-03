from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid


class UserManager(BaseUserManager):
    """
    Custom manager para User con email como username
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model
    """
    
    # UUID como primary key
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    # Email como username
    email = models.EmailField(
        _('email'), 
        unique=True,
        error_messages={
            'unique': _('Ya existe un usuario con este email.'),
        }
    )
    
    # Phone con validación
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Formato: '+999999999'. Hasta 15 dígitos."
    )
    phone = models.CharField(
        _('teléfono'),
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Requerido. 150 caracteres o menos.'),
        error_messages={
            'unique': _('Ya existe un usuario con este username.'),
        }
    )
    
    # Soft delete
    deleted_at = models.DateTimeField(
        _('fecha de eliminación'),
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('fecha de creación'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('última actualización'),
        auto_now=True
    )
    
    # Manager personalizado
    objects = UserManager()
    
    # Configuración
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['deleted_at']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Retorna nombre completo"""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    @property
    def is_doctor(self):
        """Verifica si el usuario es doctor"""
        return hasattr(self, 'doctor_profile')
    
    @property
    def is_patient(self):
        """Verifica si el usuario es paciente"""
        return hasattr(self, 'patient_profile')
    
    def can_create_doctor_profile(self):
        """Verifica si puede crear perfil de doctor"""
        if self.is_patient:
            return False, "Ya tienes un perfil de paciente."
        if self.is_doctor:
            return False, "Ya tienes un perfil de doctor."
        return True, "Puedes crear perfil de doctor."
    
    def can_create_patient_profile(self):
        """Verifica si puede crear perfil de paciente"""
        if self.is_doctor:
            return False, "Ya tienes un perfil de doctor."
        if self.is_patient:
            return False, "Ya tienes un perfil de paciente."
        return True, "Puedes crear perfil de paciente."
    
    def soft_delete(self):
        """Soft delete del usuario"""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaurar usuario soft deleted"""
        self.deleted_at = None
        self.is_active = True
        self.save()