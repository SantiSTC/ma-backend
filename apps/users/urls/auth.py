# apps/users/urls/auth.py
"""
URLs de autenticación.

/api/auth/register/     POST    Crear cuenta
/api/auth/login/        POST    Iniciar sesión
/api/auth/logout/       POST    Cerrar sesión
/api/auth/profile/      GET/PUT Ver/editar perfil
/api/auth/token/refresh/ POST   Refrescar token JWT
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import register, login, logout, profile

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='profile'),
    
    # JWT token refresh (viene de simplejwt)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
