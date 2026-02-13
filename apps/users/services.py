# apps/users/services.py

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from apps.users.models import EmailVerification


def send_verification_code(user, ip_address=None):
    """
    Genera y envía código de verificación de 6 dígitos
    
    Args:
        user: Usuario a verificar
        ip_address: IP del usuario (opcional, para seguridad)
    
    Returns:
        EmailVerification: Instancia del código creado
    """
    # Crear código
    verification = EmailVerification.create_for_user(user, ip_address)
    
    # Preparar email
    subject = 'Verifica tu cuenta - App Médicos'
    
    # Texto plano (fallback)
    text_content = f"""
Hola {user.first_name or 'Usuario'},

Tu código de verificación es: {verification.code}

Este código expira en {settings.VERIFICATION_CODE_EXPIRY_MINUTES} minutos.

Si no solicitaste este código, ignora este email.

Saludos,
Equipo App Médicos
    """
    
    # HTML (mejor presentación)
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .logo {{
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2563eb;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .code-container {{
            background: #f3f4f6;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 30px 0;
        }}
        .code {{
            font-size: 36px;
            font-weight: bold;
            color: #2563eb;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }}
        .expiry {{
            color: #6b7280;
            font-size: 14px;
            margin-top: 10px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 12px;
            text-align: center;
        }}
        .warning {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px;
            margin-top: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>🏥 App Médicos</h1>
        </div>
        
        <p>Hola <strong>{user.first_name or 'Usuario'}</strong>,</p>
        
        <p>Gracias por registrarte en App Médicos. Para completar tu registro, ingresa el siguiente código de verificación:</p>
        
        <div class="code-container">
            <div class="code">{verification.code}</div>
            <div class="expiry">Este código expira en {settings.VERIFICATION_CODE_EXPIRY_MINUTES} minutos</div>
        </div>
        
        <p>Ingresa este código en la aplicación para activar tu cuenta.</p>
        
        <div class="warning">
            ⚠️ Si no solicitaste este código, puedes ignorar este email de forma segura.
        </div>
        
        <div class="footer">
            <p>Este es un email automático, por favor no respondas a este mensaje.</p>
            <p>&copy; 2024 App Médicos - Argentina</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Crear email
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    
    # Enviar
    try:
        msg.send(fail_silently=False)
        return verification
    except Exception as e:
        # Log del error (puedes usar logging aquí)
        print(f"Error enviando email: {e}")
        raise


def send_password_reset_code(user, ip_address=None):
    """
    Envía código para resetear contraseña
    Similar a send_verification_code pero con mensaje diferente
    """
    # Crear código
    verification = EmailVerification.create_for_user(user, ip_address)
    
    subject = 'Recupera tu contraseña - App Médicos'
    
    text_content = f"""
Hola {user.first_name or 'Usuario'},

Recibimos una solicitud para restablecer tu contraseña.

Tu código de recuperación es: {verification.code}

Este código expira en {settings.VERIFICATION_CODE_EXPIRY_MINUTES} minutos.

Si no solicitaste restablecer tu contraseña, ignora este email.

Saludos,
Equipo App Médicos
    """
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2563eb; }}
        .code {{
            font-size: 36px;
            font-weight: bold;
            color: #2563eb;
            letter-spacing: 8px;
            text-align: center;
            background: #f3f4f6;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .warning {{
            background: #fee2e2;
            border-left: 4px solid #ef4444;
            padding: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Recuperación de Contraseña</h1>
        
        <p>Hola <strong>{user.first_name or 'Usuario'}</strong>,</p>
        
        <p>Recibimos una solicitud para restablecer tu contraseña. Usa el siguiente código:</p>
        
        <div class="code">{verification.code}</div>
        
        <p>Este código expira en {settings.VERIFICATION_CODE_EXPIRY_MINUTES} minutos.</p>
        
        <div class="warning">
            🔒 Si no solicitaste restablecer tu contraseña, <strong>ignora este email</strong>. Tu cuenta permanece segura.
        </div>
    </div>
</body>
</html>
    """
    
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send(fail_silently=False)
        return verification
    except Exception as e:
        print(f"Error enviando email: {e}")
        raise


def send_welcome_email(user):
    """
    Email de bienvenida después de verificar cuenta
    """
    subject = '¡Bienvenido a App Médicos! 🎉'
    
    text_content = f"""
Hola {user.first_name},

¡Tu cuenta ha sido verificada exitosamente!

Ya puedes empezar a buscar médicos y reservar turnos.

Saludos,
Equipo App Médicos
    """
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: #ffffff;
            border-radius: 8px;
            padding: 30px;
        }}
        h1 {{ color: #10b981; }}
        .button {{
            display: inline-block;
            background: #2563eb;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>¡Bienvenido a App Médicos! 🎉</h1>
        
        <p>Hola <strong>{user.first_name}</strong>,</p>
        
        <p>¡Tu cuenta ha sido verificada exitosamente!</p>
        
        <p>Ya puedes:</p>
        <ul>
            <li>Buscar médicos por especialidad y ubicación</li>
            <li>Ver perfiles de profesionales</li>
            <li>Reservar turnos fácilmente</li>
            <li>Recibir recordatorios automáticos</li>
        </ul>
        
        <p>¡Gracias por confiar en nosotros!</p>
    </div>
</body>
</html>
    """
    
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send(fail_silently=False)
    except Exception as e:
        # No es crítico si falla el email de bienvenida
        print(f"Error enviando email de bienvenida: {e}")