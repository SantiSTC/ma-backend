# # test_sendgrid.py
# # Ejecutar con: python manage.py shell < test_sendgrid.py

# from django.core.mail import send_mail
from django.conf import settings

# print("🔍 Probando configuración de SendGrid...")
# print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
# print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
# print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# try:
#     send_mail(
#         subject='Prueba SendGrid - App Médicos',
#         message='Si recibes este email, SendGrid está configurado correctamente! 🎉',
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=['angel.02plu@gmail.com'],  # ← CAMBIA ESTO
#         fail_silently=False,
#     )
#     print("✅ Email enviado exitosamente!")
#     print("Revisa tu bandeja de entrada (y spam)")
# except Exception as e:
#     print(f"❌ Error al enviar email: {e}")
    


from django.core.mail import send_mail

send_mail(
    subject='Test SendGrid',
    message='Si recibes esto, SendGrid funciona correctamente!',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['garciaplutinangel02@gmail.com'],
    fail_silently=False,
)