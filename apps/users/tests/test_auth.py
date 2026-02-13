"""
Tests para el sistema de autenticacion.

Cubre:
- Registro con verificacion de email
- Verificacion de codigo
- Reenvio de codigo
- Login (activo e inactivo)
- Google OAuth
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import EmailVerification


User = get_user_model()


class RegisterTests(APITestCase):
    """Tests para registro de usuarios."""

    def setUp(self):
        self.url = reverse('users:register')

    def test_register_creates_inactive_user(self):
        """El registro crea un usuario inactivo y envia codigo."""
        payload = {
            'email': 'nuevo@example.com',
            'username': 'nuevo123',
            'password': 'Testpass123',
            'password_confirm': 'Testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'account_type': 'patient',
        }

        with patch('apps.users.serializers.auth.send_verification_code') as mock_send:
            mock_send.side_effect = lambda u, ip_address=None: EmailVerification.create_for_user(u, ip_address)
            response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['account_type'], 'patient')

        user = User.objects.get(email='nuevo@example.com')
        self.assertFalse(user.is_active)
        mock_send.assert_called_once()

    def test_register_duplicate_email_fails(self):
        """No se puede registrar con email existente."""
        User.objects.create_user(
            email='existe@example.com',
            username='existe',
            password='Testpass123',
        )

        payload = {
            'email': 'existe@example.com',
            'username': 'nuevo',
            'password': 'Testpass123',
            'password_confirm': 'Testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'account_type': 'patient',
        }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_password_mismatch_fails(self):
        """Las contrasenas deben coincidir."""
        payload = {
            'email': 'test@example.com',
            'username': 'test123',
            'password': 'Testpass123',
            'password_confirm': 'Diferente123',
            'first_name': 'Test',
            'last_name': 'User',
            'account_type': 'doctor',
        }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)


class VerifyEmailTests(APITestCase):
    """Tests para verificacion de email."""

    def setUp(self):
        self.url = reverse('users:verify_email')
        self.user = User.objects.create_user(
            email='verificar@example.com',
            username='verificar',
            password='Testpass123',
            first_name='Test',
            last_name='User',
            is_active=False,
        )
        self.verification = EmailVerification.create_for_user(self.user)

    def test_verify_valid_code_activates_user(self):
        """Un codigo valido activa el usuario y retorna tokens."""
        payload = {
            'email': 'verificar@example.com',
            'code': self.verification.code,
        }

        with patch('apps.users.serializers.auth.send_welcome_email'):
            response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_verify_invalid_code_fails(self):
        """Un codigo invalido no activa la cuenta."""
        payload = {
            'email': 'verificar@example.com',
            'code': '000000',
        }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)

    def test_verify_already_active_fails(self):
        """No se puede verificar una cuenta ya activa."""
        self.user.is_active = True
        self.user.save(update_fields=['is_active'])

        payload = {
            'email': 'verificar@example.com',
            'code': self.verification.code,
        }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class ResendVerificationTests(APITestCase):
    """Tests para reenvio de codigo."""

    def setUp(self):
        self.url = reverse('users:resend_verification')
        self.user = User.objects.create_user(
            email='reenviar@example.com',
            username='reenviar',
            password='Testpass123',
            is_active=False,
        )

    def test_resend_creates_new_code(self):
        """Reenviar crea un nuevo codigo."""
        with patch('apps.users.serializers.auth.send_verification_code') as mock_send:
            mock_send.side_effect = lambda u, ip_address=None: EmailVerification.create_for_user(u, ip_address)
            response = self.client.post(self.url, {'email': 'reenviar@example.com'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send.assert_called_once()

    def test_resend_active_user_fails(self):
        """No se puede reenviar a usuario ya activo."""
        self.user.is_active = True
        self.user.save(update_fields=['is_active'])

        response = self.client.post(self.url, {'email': 'reenviar@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Tests para login."""

    def setUp(self):
        self.url = reverse('users:login')
        self.user = User.objects.create_user(
            email='login@example.com',
            username='login',
            password='Testpass123',
            first_name='Test',
            last_name='User',
            is_active=True,
        )

    def test_login_active_user_returns_tokens(self):
        """Login exitoso retorna tokens."""
        response = self.client.post(self.url, {
            'email': 'login@example.com',
            'password': 'Testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)

    def test_login_inactive_user_fails(self):
        """Login de usuario inactivo falla."""
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        response = self.client.post(self.url, {
            'email': 'login@example.com',
            'password': 'Testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_wrong_password_fails(self):
        """Contrasena incorrecta falla."""
        response = self.client.post(self.url, {
            'email': 'login@example.com',
            'password': 'WrongPass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_nonexistent_email_fails(self):
        """Email inexistente falla."""
        response = self.client.post(self.url, {
            'email': 'noexiste@example.com',
            'password': 'Testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class GoogleAuthTests(APITestCase):
    """Tests para Google OAuth."""

    def setUp(self):
        self.url = reverse('users:google_auth')

    def _mock_google_response(self, email='google@example.com', verified='true'):
        class FakeResponse:
            status_code = 200

            def json(inner_self):
                return {
                    'email': email,
                    'email_verified': verified,
                    'given_name': 'Google',
                    'family_name': 'User',
                    'aud': 'test-client',
                }
        return FakeResponse()

    def test_google_creates_new_user(self):
        """Google OAuth crea usuario nuevo activo."""
        with patch('apps.users.serializers.auth.requests.get', return_value=self._mock_google_response()):
            response = self.client.post(self.url, {
                'id_token': 'fake-token',
                'account_type': 'doctor',
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertTrue(response.data.get('is_new_user'))

        user = User.objects.get(email='google@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.has_usable_password())

    def test_google_logs_in_existing_user(self):
        """Google OAuth loguea usuario existente."""
        User.objects.create_user(
            email='existe.google@example.com',
            username='existegoogle',
            password='Testpass123',
            is_active=True,
        )

        with patch('apps.users.serializers.auth.requests.get', return_value=self._mock_google_response('existe.google@example.com')):
            response = self.client.post(self.url, {
                'id_token': 'fake-token',
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('is_new_user'))

    def test_google_invalid_token_fails(self):
        """Token invalido de Google falla."""
        class FakeErrorResponse:
            status_code = 400
            def json(self):
                return {'error': 'invalid_token'}

        with patch('apps.users.serializers.auth.requests.get', return_value=FakeErrorResponse()):
            response = self.client.post(self.url, {
                'id_token': 'invalid-token',
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_google_unverified_email_fails(self):
        """Email no verificado por Google falla."""
        with patch('apps.users.serializers.auth.requests.get', return_value=self._mock_google_response(verified='false')):
            response = self.client.post(self.url, {
                'id_token': 'fake-token',
            }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
