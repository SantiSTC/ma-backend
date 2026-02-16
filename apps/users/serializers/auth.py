"""
Serializers para autenticacion: registro con verificacion, login y Google OAuth.
"""

import re
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import EmailVerification
from apps.users.services import send_verification_code, send_welcome_email


User = get_user_model()


def _normalize_email(value):
    return value.lower().strip()


def _generate_unique_username(base):
    base = re.sub(r'[^a-zA-Z0-9_]+', '', base) or 'user'
    base = base[:20]
    candidate = base
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}{suffix}"
        suffix += 1
    return candidate


class RegisterVerifiedSerializer(serializers.Serializer):
    """
    Registro con email y password.
    Crea el usuario INACTIVO y envia codigo de verificacion.
    """

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
    account_type = serializers.ChoiceField(
        choices=['doctor', 'patient'],
        help_text="Tipo de cuenta: 'doctor' o 'patient'"
    )

    def validate_email(self, value):
        email = _normalize_email(value)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este email.")
        return email

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya esta en uso.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contrasenas no coinciden.'
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        account_type = validated_data.pop('account_type')
        
        # Crear usuario inactivo con account_type guardado
        validated_data['is_active'] = False
        validated_data['account_type'] = account_type
        user = User.objects.create_user(**validated_data)

        # Enviar codigo de verificacion
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else None
        send_verification_code(user, ip_address=ip_address)

        return {
            'user': user,
            'account_type': account_type,
        }


class VerifyEmailSerializer(serializers.Serializer):
    """
    Verifica codigo de 6 digitos y activa el usuario.
    """

    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, data):
        email = _normalize_email(data.get('email', ''))
        code = data.get('code', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No existe una cuenta con este email.'
            })

        if user.is_active:
            raise serializers.ValidationError({
                'email': 'Esta cuenta ya esta verificada.'
            })

        ok, message = EmailVerification.verify_code(user, code)
        if not ok:
            raise serializers.ValidationError({'code': message})

        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        user.is_active = True
        user.save(update_fields=['is_active'])

        try:
            send_welcome_email(user)
        except Exception:
            pass

        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


class ResendVerificationSerializer(serializers.Serializer):
    """
    Reenvia codigo de verificacion.
    """

    email = serializers.EmailField()

    def validate(self, data):
        email = _normalize_email(data.get('email', ''))
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No existe una cuenta con este email.'
            })

        if user.is_active:
            raise serializers.ValidationError({
                'email': 'Esta cuenta ya esta verificada.'
            })

        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else None
        send_verification_code(user, ip_address=ip_address)
        return {'user': user}


class GoogleAuthSerializer(serializers.Serializer):
    """
    Autenticacion con Google usando id_token.
    """

    id_token = serializers.CharField()
    account_type = serializers.ChoiceField(
        choices=['doctor', 'patient'],
        required=False,
        allow_null=True
    )

    def validate_id_token(self, value):
        try:
            response = requests.get(
                'https://oauth2.googleapis.com/tokeninfo',
                params={'id_token': value},
                timeout=10
            )
        except requests.RequestException:
            raise serializers.ValidationError('No se pudo validar el token con Google.')

        if response.status_code != 200:
            raise serializers.ValidationError('Token de Google invalido.')

        payload = response.json()
        client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
        if client_id and payload.get('aud') != client_id:
            raise serializers.ValidationError('Token de Google invalido para este cliente.')

        if str(payload.get('email_verified', '')).lower() != 'true':
            raise serializers.ValidationError('Google no verifico el email.')

        self.context['google_payload'] = payload
        return value

    def create(self, validated_data):
        payload = self.context.get('google_payload', {})
        email = _normalize_email(payload.get('email', ''))

        if not email:
            raise serializers.ValidationError('No se pudo obtener el email de Google.')

        user = User.objects.filter(email=email).first()
        is_new_user = False

        if not user:
            local_part = email.split('@')[0]
            username = _generate_unique_username(local_part)
            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=payload.get('given_name', '') or '',
                last_name=payload.get('family_name', '') or ''
            )
            user.set_unusable_password()
            user.is_active = True
            user.save(update_fields=['password', 'is_active'])
            is_new_user = True
        elif not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])

        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'is_new_user': is_new_user,
            'account_type': validated_data.get('account_type'),
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


class LoginSerializer(serializers.Serializer):
    """
    Login con email y password, solo para usuarios activos.
    """

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        email = _normalize_email(data.get('email', ''))
        password = data.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No existe una cuenta con este email.'
            })

        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'Debes verificar tu email antes de iniciar sesion.'
            })

        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': 'Contrasena incorrecta.'
            })

        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }
