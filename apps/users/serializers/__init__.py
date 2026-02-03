# apps/users/serializers/__init__.py

from .user import UserSerializer, UserCreateSerializer
from .auth import RegisterSerializer, LoginSerializer
from .doctor import DoctorSerializer, DoctorCreateSerializer, DoctorUpdateSerializer
from .patient import PatientSerializer, PatientCreateSerializer, PatientUpdateSerializer
from .specialty import SpecialtySerializer

__all__ = [
    'UserSerializer',
    'UserCreateSerializer',
    'RegisterSerializer',
    'LoginSerializer',
    'DoctorSerializer',
    'DoctorCreateSerializer',
    'DoctorUpdateSerializer',
    'PatientSerializer',
    'PatientCreateSerializer',
    'PatientUpdateSerializer',
    'SpecialtySerializer',
]
