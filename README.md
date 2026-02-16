# App Médicos Argentina - Backend

Backend Django para plataforma de reserva de turnos médicos.

## Stack Técnico

- **Django 5.0**
- **Django REST Framework**
- **PostgreSQL + PostGIS**
- **Redis**
- **Celery**

## Setup Inicial

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd ma-backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

Variables principales:

- `SECRET_KEY`
- `DEBUG`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `SENDGRID_API_KEY`, `DEFAULT_FROM_EMAIL`
- `GOOGLE_CLIENT_ID` (OAuth)
- `JWT_SECRET_KEY` (opcional, si no usa `SECRET_KEY`)

### 5. Levantar base de datos con Docker

```bash
docker-compose up -d
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

### 8. Correr servidor de desarrollo

```bash
python manage.py runserver
```

El servidor estará disponible en `http://localhost:8000`

## Estructura del Proyecto

```
backend/
├── config/              # Configuración Django
├── apps/
│   ├── users/          # Gestión de usuarios
├── requirements.txt
├── manage.py
└── docker-compose.yml
```

## Autenticacion (resumen)

- Registro con email/password requiere verificacion por codigo.
- Google OAuth autentica y activa al usuario automaticamente.

Endpoints:

- `POST /api/auth/register/`
- `POST /api/auth/verify-email/`
- `POST /api/auth/resend-verification/`
- `POST /api/auth/google/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET/PUT /api/auth/profile/`
- `POST /api/auth/token/refresh/`

## Seguridad

El backend implementa múltiples capas de seguridad:

- **Rate Limiting**: Protección contra fuerza bruta
  - Usuarios anónimos: 20 requests/minuto
  - Usuarios autenticados: 60 requests/minuto
  - Login: 5 intentos/minuto
  - Verificación de código: 3 intentos/minuto
- **Bloqueo temporal**: 5 intentos fallidos de verificación = bloqueo 15 min
- **Mensajes genéricos**: Login no revela si el email existe
- **JWT con blacklist**: Tokens invalidados al hacer logout
- **Passwords hasheados**: PBKDF2 (Django default)

## Documentación

Ver documentación completa en:
- [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- [docs/AUTH_FLOW.md](docs/AUTH_FLOW.md)




