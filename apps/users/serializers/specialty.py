"""
Serializer para el modelo Specialty.
"""

from rest_framework import serializers
from apps.users.models import Specialty


class SpecialtySerializer(serializers.ModelSerializer):
    """
    Serializer para especialidades médicas.
    
    Se usa para:
    - Listar especialidades disponibles
    - Mostrar detalles de una especialidad
    """
    
    # Cantidad de doctores con esta especialidad
    doctors_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Specialty
        fields = [
            'id',
            'name',
            'description',
            'doctors_count',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_doctors_count(self, obj):
        """Cuenta los doctores activos con esta especialidad"""
        return obj.doctors.filter(is_active=True).count()
