# apps/users/views/specialty.py
"""
Views para especialidades médicas.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.users.models import Specialty
from apps.users.serializers import SpecialtySerializer, DoctorSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def specialty_list(request):
    """
    Listar todas las especialidades médicas (público).
    
    GET /api/specialties/
    
    Query params:
    - search: buscar por nombre
    
    Response (200):
    {
        "count": 15,
        "results": [
            {
                "id": "uuid",
                "name": "Cardiología",
                "description": "...",
                "doctors_count": 5
            },
            ...
        ]
    }
    """
    queryset = Specialty.objects.all().order_by('name')
    
    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(name__icontains=search)
    
    serializer = SpecialtySerializer(queryset, many=True)
    
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def specialty_detail(request, specialty_id):
    """
    Ver detalle de una especialidad con sus doctores.
    
    GET /api/specialties/<uuid:specialty_id>/
    
    Response (200):
    {
        "id": "uuid",
        "name": "Cardiología",
        "description": "...",
        "doctors_count": 5,
        "doctors": [...]
    }
    """
    try:
        specialty = Specialty.objects.get(id=specialty_id)
    except Specialty.DoesNotExist:
        return Response(
            {'error': 'Especialidad no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    data = SpecialtySerializer(specialty).data
    
    # Agregar lista de doctores
    doctors = specialty.doctors.filter(is_active=True, deleted_at__isnull=True)
    data['doctors'] = DoctorSerializer(doctors, many=True).data
    
    return Response(data)
