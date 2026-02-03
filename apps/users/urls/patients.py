# apps/users/urls/patients.py
"""
URLs de pacientes.

/api/patients/profile/      GET/POST/PUT    Mi perfil de paciente
"""

from django.urls import path

from apps.users.views import patient_profile

urlpatterns = [
    path('profile/', patient_profile, name='patient_profile'),
]
