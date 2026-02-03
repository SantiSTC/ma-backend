# apps/users/urls/__init__.py
"""
URLs de la app users.

Se dividen en:
- auth: registro, login, logout, perfil
- doctors: perfil de doctor, listado, detalle
- patients: perfil de paciente
- specialties: listado y detalle de especialidades
"""

from django.urls import path, include

app_name = 'users'

urlpatterns = [
    path('auth/', include('apps.users.urls.auth')),
    path('doctors/', include('apps.users.urls.doctors')),
    path('patients/', include('apps.users.urls.patients')),
    path('specialties/', include('apps.users.urls.specialties')),
]
