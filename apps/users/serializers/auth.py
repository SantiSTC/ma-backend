"""
Serializers para autenticación: Registro y Login.

RegisterSerializer: Crear cuenta nueva (User + Doctor o Patient)
LoginSerializer: Validar credenciales y devolver tokens
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class RegisterSerializer(serializers.Serializer):
    """
    Serializer para REGISTRO de nuevos usuarios.
    
    Flujo:
    1. Usuario envía datos + tipo de cuenta (doctor/patient)
    2. Se crea el User
    3. Se devuelven los tokens JWT para login automático
    
    NOTA: El perfil de Doctor/Patient se crea después
    con los datos específicos de cada uno.
    """
    
    # Datos del usuario
    email = serializers.EmailField()
    username = serializers.CharField(min_length=3, max_length=150)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=17, required=False, allow_blank=True)
    
    # Tipo de cuenta
    account_type = serializers.ChoiceField(
        choices=['doctor', 'patient'],
        help_text="Tipo de cuenta: 'doctor' o 'patient'"
    )
    
    def validate_email(self, value):
        """Verifica que el email no exista y lo normaliza"""
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este email.")
        return email
    
    def validate_username(self, value):
        """Verifica que el username no exista"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value
    
    def validate(self, data):
        """Validaciones que involucran múltiples campos"""
        # Verificar que las contraseñas coincidan
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return data
    
    def create(self, validated_data):
        """
        Crea el usuario y devuelve los tokens.
        
        NOTA: No creamos el perfil Doctor/Patient aquí.
        Eso se hace en un endpoint separado con los datos específicos.
        """
        # Removemos campos que no van al modelo User
        validated_data.pop('password_confirm')
        account_type = validated_data.pop('account_type')
        
        # Crear usuario
        user = User.objects.create_user(**validated_data)
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'account_type': account_type,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


class LoginSerializer(serializers.Serializer):
    """
    Serializer para LOGIN.
    
    Recibe email y password, devuelve tokens JWT si son válidos.
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """Valida las credenciales"""
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        # Buscar usuario por email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No existe una cuenta con este email.'
            })
        
        # Verificar si está activo
        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'Esta cuenta está desactivada.'
            })
        
        # Verificar password
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': 'Contraseña incorrecta.'
            })
        
        # Generar tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }
