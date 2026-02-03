# apps/users/serializers/user.py
"""
Serializers para el modelo User.

UserSerializer: Para VER datos del usuario (GET)
UserCreateSerializer: Para CREAR usuarios (POST) - usado internamente
"""

from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para VER datos del usuario.
    
    Se usa cuando:
    - El usuario ve su perfil
    - Un doctor ve datos de un paciente
    - Listados de usuarios
    
    IMPORTANTE: Nunca exponemos el password
    """
    
    # Campos calculados (read-only)
    full_name = serializers.CharField(read_only=True)
    is_doctor = serializers.BooleanField(read_only=True)
    is_patient = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',      # Propiedad calculada
            'phone',
            'is_active',
            'is_doctor',      # Propiedad: tiene perfil de doctor?
            'is_patient',     # Propiedad: tiene perfil de paciente?
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'email',          # No se puede cambiar el email después de crear
            'is_active',
            'created_at',
            'updated_at',
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para CREAR usuarios (uso interno).
    
    Este serializer se usa dentro de RegisterSerializer.
    Maneja la creación del password de forma segura.
    """
    
    # El password se escribe pero NUNCA se lee/devuelve
    password = serializers.CharField(
        write_only=True,      # Solo escritura, no aparece en respuestas
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
            'phone',
        ]
    
    def validate_email(self, value):
        """Normaliza el email a minúsculas"""
        return value.lower()
    
    def create(self, validated_data):
        """
        Crea el usuario usando el manager personalizado.
        Esto asegura que el password se hashee correctamente.
        """
        return User.objects.create_user(**validated_data)
