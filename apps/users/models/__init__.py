# apps/users/models/__init__.py

from .user import User, UserManager
from .doctor import Doctor
from .patient import Patient
from .specialty import Specialty
from .verification import EmailVerification

__all__ = [
    'User',
    'UserManager',
    'Doctor',
    'Patient',
    'Specialty',
    'EmailVerification'
]