# apps/users/urls/auth.py
"""
URLs de autenticacion.

/api/auth/register/              POST   Registro con verificacion
/api/auth/verify-email/          POST   Verificar codigo
/api/auth/resend-verification/   POST   Reenviar codigo
/api/auth/google/                POST   Google OAuth
/api/auth/login/                 POST   Login
/api/auth/logout/                POST   Logout
/api/auth/profile/               GET/PUT Perfil
/api/auth/token/refresh/         POST   Refresh JWT
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import (
    register,
    verify_email,
    resend_verification,
    google_auth,
    login,
    logout,
    profile,
)

urlpatterns = [
    path('register/', register, name='register'),
    path('verify-email/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification, name='resend_verification'),
    path('google/', google_auth, name='google_auth'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='profile'),
    
    # JWT token refresh (viene de simplejwt)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
