# apps/users/views/doctor.py
"""
Views para doctores.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q

from apps.users.models import Doctor
from apps.users.serializers import (
    DoctorSerializer,
    DoctorCreateSerializer,
    DoctorUpdateSerializer,
)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def doctor_profile(request):
    """
    Gestionar MI perfil de doctor.
    
    GET /api/doctors/profile/
    - Ver mi perfil de doctor
    
    POST /api/doctors/profile/
    - Crear mi perfil de doctor
    Body: {
        "license_number": "MN12345",
        "university": "UBA",
        "bio": "Especialista en...",
        "address": "Av. Corrientes 1234",
        "latitude": -34.6037,
        "longitude": -58.3816,
        "specialty_ids": ["uuid1", "uuid2"]
    }
    
    PUT /api/doctors/profile/
    - Actualizar mi perfil de doctor
    """
    if request.method == 'GET':
        if not request.user.is_doctor:
            return Response(
                {'error': 'No tienes un perfil de doctor'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DoctorSerializer(request.user.doctor_profile)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = DoctorCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            doctor = serializer.save()
            return Response({
                'message': 'Perfil de doctor creado exitosamente',
                'doctor': DoctorSerializer(doctor).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        if not request.user.is_doctor:
            return Response(
                {'error': 'No tienes un perfil de doctor'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DoctorUpdateSerializer(
            request.user.doctor_profile,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            doctor = serializer.save()
            return Response({
                'message': 'Perfil actualizado',
                'doctor': DoctorSerializer(doctor).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def doctor_list(request):
    """
    Listar todos los doctores activos (público).
    
    GET /api/doctors/
    
    Query params:
    - specialty: filtrar por especialidad
    - search: buscar por nombre
    
    Response (200):
    {
        "count": 10,
        "results": [...]
    }
    """
    queryset = Doctor.objects.filter(
        is_active=True,
        deleted_at__isnull=True
    ).select_related('user')
    
    # Filtrar por especialidad
    specialty = request.query_params.get('specialty')
    if specialty:
        queryset = queryset.filter(specialties__name__icontains=specialty)
    
    # Buscar por nombre
    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    queryset = queryset.distinct()
    serializer = DoctorSerializer(queryset, many=True)
    
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def doctor_detail(request, doctor_id):
    """
    Ver detalle de un doctor específico (público).
    
    GET /api/doctors/<uuid:doctor_id>/
    """
    try:
        doctor = Doctor.objects.select_related('user').get(
            id=doctor_id,
            is_active=True,
            deleted_at__isnull=True
        )
    except Doctor.DoesNotExist:
        return Response(
            {'error': 'Doctor no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = DoctorSerializer(doctor)
    return Response(serializer.data)
