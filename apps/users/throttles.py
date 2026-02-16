# apps/users/throttles.py
"""
Throttles personalizados para protección contra fuerza bruta.
"""

from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache


class LoginRateThrottle(SimpleRateThrottle):
    """
    Throttle específico para login.
    5 intentos por minuto por IP.
    """
    scope = 'login'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class VerificationRateThrottle(SimpleRateThrottle):
    """
    Throttle específico para verificación de código.
    3 intentos por minuto por IP.
    """
    scope = 'verification'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class VerificationAttemptTracker:
    """
    Rastrea intentos fallidos de verificación por email.
    Bloquea temporalmente después de MAX_ATTEMPTS.
    """
    MAX_ATTEMPTS = 5
    BLOCK_DURATION = 900  # 15 minutos en segundos
    
    @staticmethod
    def _get_key(email):
        return f"verification_attempts:{email.lower()}"
    
    @classmethod
    def record_failed_attempt(cls, email):
        """Registra un intento fallido."""
        key = cls._get_key(email)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, cls.BLOCK_DURATION)
        return attempts
    
    @classmethod
    def is_blocked(cls, email):
        """Verifica si el email está bloqueado por demasiados intentos."""
        key = cls._get_key(email)
        attempts = cache.get(key, 0)
        return attempts >= cls.MAX_ATTEMPTS
    
    @classmethod
    def get_remaining_attempts(cls, email):
        """Retorna intentos restantes."""
        key = cls._get_key(email)
        attempts = cache.get(key, 0)
        return max(0, cls.MAX_ATTEMPTS - attempts)
    
    @classmethod
    def clear_attempts(cls, email):
        """Limpia intentos después de verificación exitosa."""
        key = cls._get_key(email)
        cache.delete(key)
