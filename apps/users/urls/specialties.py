# apps/users/urls/specialties.py
"""
URLs de especialidades.

/api/specialties/               GET     Listar especialidades
/api/specialties/<uuid:id>/     GET     Detalle de especialidad
"""

from django.urls import path

from apps.users.views import specialty_list, specialty_detail

urlpatterns = [
    path('', specialty_list, name='specialty_list'),
    path('<uuid:specialty_id>/', specialty_detail, name='specialty_detail'),
]
