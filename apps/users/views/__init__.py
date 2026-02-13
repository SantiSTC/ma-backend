# apps/users/views/__init__.py

from .auth import (
    register,
    verify_email,
    resend_verification,
    google_auth,
    login,
    logout,
    profile,
)
from .doctor import doctor_profile, doctor_list, doctor_detail
from .patient import patient_profile
from .specialty import specialty_list, specialty_detail

__all__ = [
    # Auth
    'register',
    'verify_email',
    'resend_verification',
    'google_auth',
    'login',
    'logout',
    'profile',
    # Doctor
    'doctor_profile',
    'doctor_list',
    'doctor_detail',
    # Patient
    'patient_profile',
    # Specialty
    'specialty_list',
    'specialty_detail',
]