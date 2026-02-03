# apps/users/urls/doctors.py
"""
URLs de doctores.

/api/doctors/               GET         Listar doctores
/api/doctors/profile/       GET/POST/PUT Mi perfil de doctor
/api/doctors/<uuid:id>/     GET         Detalle de un doctor
"""

from django.urls import path

from apps.users.views import doctor_profile, doctor_list, doctor_detail

urlpatterns = [
    path('', doctor_list, name='doctor_list'),
    path('profile/', doctor_profile, name='doctor_profile'),
    path('<uuid:doctor_id>/', doctor_detail, name='doctor_detail'),
]
