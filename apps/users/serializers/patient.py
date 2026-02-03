"""
Serializers para el modelo Patient.

PatientSerializer: Ver perfil de paciente
PatientCreateSerializer: Crear perfil de paciente
"""

from rest_framework import serializers
from apps.users.models import Patient
from .user import UserSerializer


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer para VER perfil de paciente.
    
    Incluye:
    - Datos del paciente
    - Datos del usuario (anidado)
    - Edad calculada
    """
    
    # Anidamos los datos del usuario
    user = UserSerializer(read_only=True)
    
    # Campo calculado
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'user',              # Datos del usuario anidados
            'dni',
            'birth_date',
            'age',               # Calculado automáticamente
            'insurance_provider',
            'insurance_plan',
            'insurance_number',
            'image_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para CREAR perfil de paciente.
    
    Se usa cuando un usuario ya registrado quiere
    completar su perfil como paciente.
    
    NOTA: El usuario ya debe existir y estar autenticado.
    """
    
    class Meta:
        model = Patient
        fields = [
            'dni',
            'birth_date',
            'insurance_provider',
            'insurance_plan',
            'insurance_number',
            'image_url',
        ]
    
    def validate_dni(self, value):
        """Verifica que el DNI no exista"""
        if Patient.objects.filter(dni=value).exists():
            raise serializers.ValidationError(
                "Ya existe un paciente con este DNI."
            )
        return value
    
    def validate(self, data):
        """Valida que el usuario pueda crear perfil de paciente"""
        user = self.context['request'].user
        
        can_create, message = user.can_create_patient_profile()
        if not can_create:
            raise serializers.ValidationError(message)
        
        return data
    
    def create(self, validated_data):
        """Crea el perfil de paciente"""
        user = self.context['request'].user
        return Patient.objects.create(user=user, **validated_data)


class PatientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para ACTUALIZAR perfil de paciente.
    
    No permite cambiar: user, dni
    """
    
    class Meta:
        model = Patient
        fields = [
            'birth_date',
            'insurance_provider',
            'insurance_plan',
            'insurance_number',
            'image_url',
        ]
