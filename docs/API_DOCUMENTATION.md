# 📚 Documentación API - Médicos Argentina

## 📋 Índice
1. [Descripción General](#descripción-general)
2. [Tecnologías](#tecnologías)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Modelos de Datos](#modelos-de-datos)
5. [Endpoints de la API](#endpoints-de-la-api)
6. [Autenticación](#autenticación)
7. [Configuración y Ejecución](#configuración-y-ejecución)
8. [Tests](#tests)

---

## 🎯 Descripción General

Backend para la aplicación "Médicos Argentina", una plataforma que conecta pacientes con médicos para la gestión de turnos médicos.

### Funcionalidades implementadas:
- ✅ Registro con verificacion por email (codigo)
- ✅ Login con JWT
- ✅ Google OAuth
- ✅ Perfiles separados para médicos y pacientes
- ✅ Gestión de especialidades médicas
- ✅ Listado público de médicos con filtros
- ✅ Panel de administración

---

## 🛠 Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.12 | Lenguaje principal |
| Django | 5.0.1 | Framework web |
| Django REST Framework | 3.14 | API REST |
| PostgreSQL | 15+ | Base de datos |
| JWT (SimpleJWT) | 5.3 | Autenticación |
| Cloudinary | - | Almacenamiento de imágenes |
| Redis | - | Cache (futuro) |
| Celery | - | Tareas asíncronas (futuro) |

---

## 📁 Estructura del Proyecto

```
ma-backend/
├── config/                 # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   └── users/              # Módulo de usuarios
│       ├── models/         # Modelos de datos
│       │   ├── user.py     # Usuario base
│       │   ├── doctor.py   # Perfil de médico
│       │   ├── patient.py  # Perfil de paciente
│       │   ├── specialty.py # Especialidades
│       │   └── verification.py # Códigos de verificación
│       │
│       ├── serializers/    # Serializadores
│       │   ├── user.py
│       │   ├── auth.py     # Register, Login, Google, Verify
│       │   ├── doctor.py
│       │   ├── patient.py
│       │   └── specialty.py
│       │
│       ├── views/          # Vistas (endpoints)
│       │   ├── auth.py
│       │   ├── doctor.py
│       │   ├── patient.py
│       │   └── specialty.py
│       │
│       ├── urls/           # Rutas
│       │   ├── auth.py
│       │   ├── doctors.py
│       │   ├── patients.py
│       │   └── specialties.py
│       │
│       ├── tests/          # Tests unitarios
│       │   └── test_auth.py
│       │
│       ├── services.py     # Servicios (envío de emails)
│       ├── throttles.py    # Rate limiting y protección fuerza bruta
│       └── admin.py        # Panel de administración
│
├── docs/                   # Documentación
│   ├── API_DOCUMENTATION.md
│   └── AUTH_FLOW.md
├── requirements.txt        # Dependencias
└── manage.py
```

---

## 📊 Modelos de Datos

### User (Usuario base)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Identificador único |
| email | string | Email (único, usado para login) |
| username | string | Nombre de usuario |
| password | string | Contraseña (hasheada) |
| first_name | string | Nombre |
| last_name | string | Apellido |
| phone | string | Teléfono |
| is_active | boolean | Cuenta activa |
| deleted_at | datetime | Soft delete |
| created_at | datetime | Fecha de creación |

### Doctor (Perfil de médico)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Identificador único |
| user | FK → User | Usuario asociado |
| license_number | string | Número de matrícula (único) |
| university | string | Universidad |
| bio | text | Biografía profesional |
| address | string | Dirección del consultorio |
| latitude | decimal | Latitud (geolocalización) |
| longitude | decimal | Longitud (geolocalización) |
| image_url | string | URL de foto de perfil |
| is_active | boolean | Disponible para turnos |
| specialties | M2M → Specialty | Especialidades |

### Patient (Perfil de paciente)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Identificador único |
| user | FK → User | Usuario asociado |
| dni | string | DNI (único) |
| birth_date | date | Fecha de nacimiento |
| insurance_provider | string | Obra social/prepaga |
| insurance_plan | string | Plan |
| insurance_number | string | Número de afiliado |
| image_url | string | URL de foto de perfil |

### Specialty (Especialidad médica)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Identificador único |
| name | string | Nombre (único) |
| description | text | Descripción |
| doctors | M2M → Doctor | Médicos con esta especialidad |

### EmailVerification (Códigos de verificación)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | int | ID auto-incremental |
| user | FK → User | Usuario asociado |
| code | char(6) | Código de 6 dígitos |
| created_at | datetime | Fecha de creación |
| expires_at | datetime | Expiración (15 min default) |
| is_used | boolean | Si ya fue usado |
| ip_address | IP | IP del solicitante |

---

## 🌐 Endpoints de la API

### Autenticación (`/api/auth/`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/register/` | Crear cuenta (inactiva, envia codigo) | ❌ |
| POST | `/verify-email/` | Verificar codigo y activar cuenta | ❌ |
| POST | `/resend-verification/` | Reenviar codigo de verificacion | ❌ |
| POST | `/google/` | Login/registro con Google | ❌ |
| POST | `/login/` | Iniciar sesion | ❌ |
| POST | `/logout/` | Cerrar sesión | ✅ |
| GET | `/profile/` | Ver mi perfil | ✅ |
| PUT | `/profile/` | Editar mi perfil | ✅ |
| POST | `/token/refresh/` | Refrescar token | ❌ |

### Médicos (`/api/doctors/`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/` | Listar médicos | ❌ |
| GET | `/<uuid:id>/` | Ver detalle de médico | ❌ |
| GET | `/profile/` | Ver mi perfil de médico | ✅ |
| POST | `/profile/` | Crear perfil de médico | ✅ |
| PUT | `/profile/` | Editar perfil de médico | ✅ |

**Filtros disponibles en listado:**
- `?search=nombre` - Buscar por nombre
- `?specialty=cardiologia` - Filtrar por especialidad

### Pacientes (`/api/patients/`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/profile/` | Ver mi perfil de paciente | ✅ |
| POST | `/profile/` | Crear perfil de paciente | ✅ |
| PUT | `/profile/` | Editar perfil de paciente | ✅ |

### Especialidades (`/api/specialties/`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/` | Listar especialidades | ❌ |
| GET | `/<uuid:id>/` | Ver especialidad con médicos | ❌ |

---

## 🔐 Autenticación

Se utiliza **JWT (JSON Web Tokens)** con la librería `djangorestframework-simplejwt`.

### Tokens:
- **Access Token**: Expira en 15 minutos, se usa en cada peticion
- **Refresh Token**: Expira en 7 días, se usa para obtener nuevo access token

### Uso en peticiones:
```
Headers:
  Authorization: Bearer <access_token>
```

### Flujo de autenticación:
```
Registro email/password
1. POST /api/auth/register/ → crea usuario inactivo y envia codigo
2. POST /api/auth/verify-email/ → activa cuenta y retorna tokens

Login email/password
1. POST /api/auth/login/ → retorna tokens (solo si is_active=True)

Google OAuth
1. POST /api/auth/google/ → valida token Google y retorna tokens

Refresh
1. POST /api/auth/token/refresh/ → recibe { refresh } y retorna access
```

---

## 🛡️ Seguridad

### Rate Limiting (Throttling)

Protección contra ataques de fuerza bruta implementada en `apps/users/throttles.py`.

| Tipo | Límite | Descripción |
|------|--------|-------------|
| Usuarios anónimos | 20/minuto | Todas las peticiones sin auth |
| Usuarios autenticados | 60/minuto | Peticiones con JWT válido |
| Login | 5/minuto | Endpoint `/api/auth/login/` |
| Verificación | 3/minuto | Endpoint `/api/auth/verify-email/` |

### Bloqueo por Intentos Fallidos

| Evento | Acción |
|--------|--------|
| 5 intentos fallidos de verificación | Bloqueo 15 minutos por email |
| Código verificado correctamente | Se limpian los intentos |

### Mensajes de Error Seguros

- **Login**: Mensaje genérico "Credenciales inválidas" (no revela si el email existe)
- **Verificación**: Muestra intentos restantes antes de bloqueo

### Otras Medidas

- Passwords hasheados con PBKDF2
- JWT con blacklist al hacer logout
- Códigos de verificación expiran en 15 min
- Google OAuth valida `aud` (client ID)
- UUIDs como IDs (previene enumeración)

---

## ⚙️ Configuración y Ejecución

### Variables de entorno (.env)
```env
DEBUG=True
SECRET_KEY=tu-secret-key

DB_NAME=medicos_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx

SENDGRID_API_KEY=xxx
DEFAULT_FROM_EMAIL=noreply@appmedicos.com
GOOGLE_CLIENT_ID=xxx
```

### Comandos básicos
```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Verificar configuración
python manage.py check
```

### URLs importantes
- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/

---

## 📝 Reglas de Negocio

1. **Un usuario NO puede ser médico y paciente simultáneamente** con la misma cuenta
2. **El email es único** y se usa como identificador principal
3. **La matrícula médica es única** por doctor
4. **El DNI es único** por paciente
5. **Los médicos inactivos** no aparecen en listados públicos

---

## 🚧 Pendiente de Implementar

- [ ] Recuperación de contraseña
- [ ] Sistema de suscripción para médicos
- [ ] Validación de matrícula médica
- [ ] Módulo de turnos/citas
- [ ] Notificaciones
- [ ] Tests unitarios adicionales

---

## 🧪 Tests

### Ejecutar tests de autenticación
```bash
python manage.py test apps.users.tests.test_auth -v 2
```

### Cobertura de tests actual
| Módulo | Tests | Cobertura |
|--------|-------|-----------|
| Registro | 3 | Usuario inactivo, email duplicado, passwords |
| Verificación | 3 | Código válido/inválido, ya activo |
| Reenvío | 2 | Nuevo código, usuario activo |
| Login | 4 | Exitoso, inactivo, password, email |
| Google OAuth | 4 | Nuevo usuario, existente, token inválido, email no verificado |

**Total: 16 tests**

---

## 📖 Documentación Adicional

- [AUTH_FLOW.md](AUTH_FLOW.md) - Flujo detallado del sistema de autenticación

---

## 👥 Equipo

- **Backend**: Angel Gabriel García Plutín
- **Última actualización**: Febrero 2026
