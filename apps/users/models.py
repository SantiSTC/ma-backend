from django.contrib.auth.models import AbstractUser, BaseUserManager
# from django.contrib.gis.db import models # PostGIS
from django.db import models # Sin PostGIS
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
    
    Campos del ER:
    - id (UUID)
    - name (first_name + last_name de AbstractUser)
    - email (unique)
    - phone
    - passwordHash (password de AbstractUser)
    - isActive (is_active de AbstractUser)
    - deletedAt (para soft delete)
    - createdAt
    
    NOTA: NO incluimos 'role' porque es redundante.
    El rol se determina por la existencia de Doctor o Patient profile.
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
    
    # Override username (no lo usamos, usamos email)
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
    REQUIRED_FIELDS = ['username']  # Requerido para createsuperuser
    
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
        """
        Verifica si puede crear perfil de doctor
        
        REGLA DE NEGOCIO: Un usuario NO puede ser doctor Y paciente
        Si ya es paciente, debe crear una cuenta separada para ser doctor.
        """
        if self.is_patient:
            return False, "Ya tienes un perfil de paciente. Crea una cuenta separada para ser doctor."
        if self.is_doctor:
            return False, "Ya tienes un perfil de doctor."
        return True, "Puedes crear perfil de doctor."
    
    def can_create_patient_profile(self):
        """
        Verifica si puede crear perfil de paciente
        
        REGLA DE NEGOCIO: Un usuario NO puede ser doctor Y paciente
        Si ya es doctor, debe crear una cuenta separada para ser paciente.
        """
        if self.is_doctor:
            return False, "Ya tienes un perfil de doctor. Crea una cuenta separada para ser paciente."
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


class Doctor(models.Model):
    """
    Perfil de Doctor
    
    Campos del ER:
    - id (UUID)
    - userId (FK a User)
    - licenseNumber (número de matrícula)
    - university
    - bio
    - location (se divide en address + lat/lon para PostGIS)
    - imageUrl
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.OneToOneField(
        User,
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
    
    university = models.CharField(
        _('universidad'),
        max_length=200,
        blank=True
    )
    
    bio = models.TextField(
        _('biografía'),
        blank=True,
        help_text=_('Descripción profesional del médico')
    )
    
    # Ubicación del consultorio
    address = models.CharField(
        _('dirección'),
        max_length=255,
        blank=True
    )
    
    # PostGIS para geolocalización
    # location = models.PointField(
    #     _('ubicación geográfica'),
    #     geography=True,
    #     null=True,
    #     blank=True,
    #     help_text=_('Coordenadas del consultorio')
    # )
    
    image_url = models.URLField(
        _('foto de perfil'),
        max_length=500,
        blank=True
    )
    
    # Control de estado
    is_active = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Indica si el doctor está actualmente disponible')
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
    
    # @property
    # def rating(self):
    #     """Calcula el rating promedio del doctor"""
    #     from apps.appointments.models import Review
    #     reviews = Review.objects.filter(doctor=self)
    #     if reviews.exists():
    #         return reviews.aggregate(models.Avg('rating'))['rating__avg']
    #     return 0.0


class Patient(models.Model):
    """
    Perfil de Paciente
    
    Campos del ER:
    - id (UUID)
    - userId (FK a User)
    - dni
    - birthDate
    - insuranceProvider (obra social/prepaga)
    - insurancePlan
    - imageUrl
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        verbose_name=_('usuario')
    )
    
    dni = models.CharField(
        _('DNI'),
        max_length=20,
        unique=True,
        help_text=_('Documento Nacional de Identidad')
    )
    
    birth_date = models.DateField(
        _('fecha de nacimiento'),
        null=True,
        blank=True
    )
    
    insurance_provider = models.CharField(
        _('obra social/prepaga'),
        max_length=100,
        blank=True,
        help_text=_('Ej: OSDE, Swiss Medical, IOMA')
    )
    
    insurance_plan = models.CharField(
        _('plan'),
        max_length=100,
        blank=True,
        help_text=_('Ej: 310, 410, Premium')
    )
    
    insurance_number = models.CharField(
        _('número de afiliado'),
        max_length=50,
        blank=True
    )
    
    image_url = models.URLField(
        _('foto de perfil'),
        max_length=500,
        blank=True
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
    
    class Meta:
        verbose_name = _('paciente')
        verbose_name_plural = _('pacientes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dni']),
        ]
    
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


class Specialty(models.Model):
    """
    Especialidades médicas
    
    Campos del ER:
    - id (UUID)
    - name
    - description
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        _('nombre'),
        max_length=100,
        unique=True,
        help_text=_('Ej: Cardiología, Pediatría, Traumatología')
    )
    
    description = models.TextField(
        _('descripción'),
        blank=True
    )
    
    # Many-to-Many con Doctor
    doctors = models.ManyToManyField(
        Doctor,
        related_name='specialties',
        verbose_name=_('doctores'),
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('fecha de creación'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('especialidad')
        verbose_name_plural = _('especialidades')
        ordering = ['name']
    
    def __str__(self):
        return self.name