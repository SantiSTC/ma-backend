# apps/users/views/patient.py
"""
Views para pacientes.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.serializers import (
    PatientSerializer,
    PatientCreateSerializer,
    PatientUpdateSerializer,
)


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def patient_profile(request):
    """
    Gestionar MI perfil de paciente.
    
    GET /api/patients/profile/
    - Ver mi perfil de paciente
    
    POST /api/patients/profile/
    - Crear mi perfil de paciente
    Body: {
        "dni": "12345678",
        "birth_date": "1990-05-15",
        "insurance_provider": "OSDE",
        "insurance_plan": "310",
        "insurance_number": "123456789"
    }
    
    PUT /api/patients/profile/
    - Actualizar mi perfil de paciente
    """
    if request.method == 'GET':
        if not request.user.is_patient:
            return Response(
                {'error': 'No tienes un perfil de paciente'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PatientSerializer(request.user.patient_profile)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PatientCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            patient = serializer.save()
            return Response({
                'message': 'Perfil de paciente creado exitosamente',
                'patient': PatientSerializer(patient).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        if not request.user.is_patient:
            return Response(
                {'error': 'No tienes un perfil de paciente'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PatientUpdateSerializer(
            request.user.patient_profile,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            patient = serializer.save()
            return Response({
                'message': 'Perfil actualizado',
                'patient': PatientSerializer(patient).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
