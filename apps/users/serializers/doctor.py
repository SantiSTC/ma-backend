"""
Serializers para el modelo Doctor.

DoctorSerializer: Ver perfil de doctor
DoctorCreateSerializer: Crear perfil de doctor
"""

from rest_framework import serializers
from apps.users.models import Doctor, Specialty
from .user import UserSerializer


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer para VER perfil de doctor.
    
    Incluye:
    - Datos del doctor
    - Datos del usuario (anidado)
    - Lista de especialidades
    """
    
    # Anidamos los datos del usuario
    user = UserSerializer(read_only=True)
    
    # Mostramos las especialidades como lista de nombres
    specialties = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id',
            'user',              # Datos del usuario anidados
            'license_number',
            'university',
            'bio',
            'address',
            'latitude',
            'longitude',
            'image_url',
            'specialties',       # Lista de especialidades
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_specialties(self, obj):
        """Devuelve lista de especialidades con id y nombre"""
        return [
            {'id': str(s.id), 'name': s.name}
            for s in obj.specialties.all()
        ]


class DoctorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para CREAR perfil de doctor.
    
    Se usa cuando un usuario ya registrado quiere
    completar su perfil como doctor.
    
    NOTA: El usuario ya debe existir y estar autenticado.
    """
    
    # IDs de especialidades a asignar
    specialty_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="Lista de IDs de especialidades"
    )
    
    class Meta:
        model = Doctor
        fields = [
            'license_number',
            'university',
            'bio',
            'address',
            'latitude',
            'longitude',
            'image_url',
            'specialty_ids',
        ]
    
    def validate_license_number(self, value):
        """Verifica que la matrícula no exista"""
        if Doctor.objects.filter(license_number=value).exists():
            raise serializers.ValidationError(
                "Ya existe un doctor con este número de matrícula."
            )
        return value
    
    def validate(self, data):
        """Valida que el usuario pueda crear perfil de doctor"""
        user = self.context['request'].user
        
        can_create, message = user.can_create_doctor_profile()
        if not can_create:
            raise serializers.ValidationError(message)
        
        return data
    
    def create(self, validated_data):
        """Crea el perfil de doctor"""
        user = self.context['request'].user
        specialty_ids = validated_data.pop('specialty_ids', [])
        
        # Crear doctor
        doctor = Doctor.objects.create(user=user, **validated_data)
        
        # Asignar especialidades
        if specialty_ids:
            specialties = Specialty.objects.filter(id__in=specialty_ids)
            for specialty in specialties:
                specialty.doctors.add(doctor)
        
        return doctor


class DoctorUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para ACTUALIZAR perfil de doctor.
    
    No permite cambiar: user, license_number
    """
    
    specialty_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Doctor
        fields = [
            'university',
            'bio',
            'address',
            'latitude',
            'longitude',
            'image_url',
            'is_active',
            'specialty_ids',
        ]
    
    def update(self, instance, validated_data):
        """Actualiza el doctor y sus especialidades"""
        specialty_ids = validated_data.pop('specialty_ids', None)
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar especialidades si se enviaron
        if specialty_ids is not None:
            # Quitar de todas las especialidades actuales
            for specialty in instance.specialties.all():
                specialty.doctors.remove(instance)
            
            # Agregar a las nuevas especialidades
            specialties = Specialty.objects.filter(id__in=specialty_ids)
            for specialty in specialties:
                specialty.doctors.add(instance)
        
        return instance
