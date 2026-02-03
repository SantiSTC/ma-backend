# apps/users/views/auth.py
"""
Views de autenticación: Register, Login, Logout, Profile.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Crea una nueva cuenta de usuario.
    
    POST /api/auth/register/
    
    Body:
    {
        "email": "usuario@mail.com",
        "username": "usuario123",
        "password": "contraseña123",
        "password_confirm": "contraseña123",
        "first_name": "Juan",
        "last_name": "Pérez",
        "phone": "+5491123456789",  (opcional)
        "account_type": "doctor" o "patient"
    }
    
    Response (201):
    {
        "message": "Cuenta creada exitosamente",
        "user": { ... },
        "account_type": "doctor",
        "tokens": { "access": "...", "refresh": "..." }
    }
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        result = serializer.save()
        
        return Response({
            'message': 'Cuenta creada exitosamente',
            'user': UserSerializer(result['user']).data,
            'account_type': result['account_type'],
            'tokens': result['tokens'],
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Inicia sesión y devuelve tokens JWT.
    
    POST /api/auth/login/
    
    Body:
    {
        "email": "usuario@mail.com",
        "password": "contraseña123"
    }
    
    Response (200):
    {
        "message": "Login exitoso",
        "user": { ... },
        "tokens": { "access": "...", "refresh": "..." }
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        result = serializer.validated_data
        
        return Response({
            'message': 'Login exitoso',
            'user': UserSerializer(result['user']).data,
            'tokens': result['tokens'],
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Cierra sesión invalidando el refresh token.
    
    POST /api/auth/logout/
    
    Body:
    {
        "refresh": "eyJ..."
    }
    
    Response (200):
    {
        "message": "Sesión cerrada exitosamente"
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Se requiere el refresh token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response(
            {'message': 'Sesión cerrada exitosamente'},
            status=status.HTTP_200_OK
        )
    except Exception:
        return Response(
            {'error': 'Token inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Ver o actualizar el perfil del usuario autenticado.
    
    GET /api/auth/profile/
    Response (200): { datos del usuario }
    
    PUT /api/auth/profile/
    Body: { "first_name": "Juan Carlos", "phone": "..." }
    Response (200): { "message": "...", "user": {...} }
    """
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Perfil actualizado',
                'user': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
