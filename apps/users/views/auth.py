# apps/users/views/auth.py
"""
Views de autenticacion: registro con verificacion, login, Google OAuth y perfil.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import (
    RegisterVerifiedSerializer,
    VerifyEmailSerializer,
    ResendVerificationSerializer,
    GoogleAuthSerializer,
    LoginSerializer,
    UserSerializer,
)
from apps.users.throttles import LoginRateThrottle, VerificationRateThrottle


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Crea una nueva cuenta de usuario INACTIVA y envia codigo de verificacion.

    POST /api/auth/register/
    """
    serializer = RegisterVerifiedSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        result = serializer.save()
        return Response({
            'message': 'Revisa tu email para verificar tu cuenta',
            'user': UserSerializer(result['user']).data,
            'account_type': result['account_type'],
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([VerificationRateThrottle])
def verify_email(request):
    """
    Verifica el codigo de email y activa la cuenta.

    POST /api/auth/verify-email/
    """
    serializer = VerifyEmailSerializer(data=request.data)

    if serializer.is_valid():
        result = serializer.save()
        return Response({
            'message': 'Email verificado correctamente',
            'user': UserSerializer(result['user']).data,
            'tokens': result['tokens'],
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification(request):
    """
    Reenvia el codigo de verificacion.

    POST /api/auth/resend-verification/
    """
    serializer = ResendVerificationSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Codigo reenviado correctamente',
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """
    Login/registro con Google OAuth.

    POST /api/auth/google/
    """
    serializer = GoogleAuthSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        result = serializer.save()
        return Response({
            'message': 'Autenticacion con Google exitosa',
            'user': UserSerializer(result['user']).data,
            'tokens': result['tokens'],
            'is_new_user': result['is_new_user'],
            'account_type': result['account_type'],
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
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
