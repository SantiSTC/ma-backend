# 🔐 Sistema de Autenticación - Médicos Argentina

## 📋 Índice
1. [Resumen](#resumen)
2. [Métodos de Autenticación](#métodos-de-autenticación)
3. [Flujos Detallados](#flujos-detallados)
4. [Endpoints](#endpoints)
5. [Modelos de Datos](#modelos-de-datos)
6. [Casos de Uso](#casos-de-uso)
7. [Manejo de Errores](#manejo-de-errores)
8. [Seguridad](#seguridad)
9. [Configuración](#configuración)

---

## 📝 Resumen

El sistema de autenticación soporta **2 métodos**:

| Método | Verificación | Velocidad | Privacidad |
|--------|--------------|-----------|------------|
| Email + Password | Código 6 dígitos | Media (2 pasos) | Alta |
| Google OAuth | Automática (Google) | Rápida (1 click) | Media |

**Principio clave**: Un usuario debe verificar su identidad antes de usar la app.

---

## 🔑 Métodos de Autenticación

### 1. Email + Password (con verificación)

```
┌─────────────────────────────────────────────────────────────┐
│                    REGISTRO                                 │
│                                                             │
│  Usuario                          Backend                   │
│     │                                │                      │
│     │──── POST /register/ ──────────>│                      │
│     │     {email, password, ...}     │                      │
│     │                                │                      │
│     │                          Crea usuario                 │
│     │                          is_active=False              │
│     │                                │                      │
│     │<─── 201 "Revisa tu email" ────│                      │
│     │                                │                      │
│     │                          Envía código                 │
│     │                          (6 dígitos)                  │
│     │                                │                      │
│  [Revisa email]                      │                      │
│     │                                │                      │
│     │──── POST /verify-email/ ──────>│                      │
│     │     {email, code}              │                      │
│     │                                │                      │
│     │                          Valida código                │
│     │                          is_active=True               │
│     │                                │                      │
│     │<─── 200 {tokens} ─────────────│                      │
│     │                                │                      │
│  ✅ LOGUEADO                         │                      │
└─────────────────────────────────────────────────────────────┘
```

### 2. Google OAuth

```
┌─────────────────────────────────────────────────────────────┐
│                    GOOGLE AUTH                              │
│                                                             │
│  Usuario          Frontend              Backend             │
│     │                │                     │                │
│     │── Click ──────>│                     │                │
│     │  "Google"      │                     │                │
│     │                │                     │                │
│     │<── Google ────>│                     │                │
│     │   OAuth UI     │                     │                │
│     │                │                     │                │
│     │── Selecciona ─>│                     │                │
│     │   cuenta       │                     │                │
│     │                │                     │                │
│     │           id_token                   │                │
│     │                │                     │                │
│     │                │── POST /google/ ───>│                │
│     │                │   {id_token}        │                │
│     │                │                     │                │
│     │                │              Valida con Google       │
│     │                │              Crea/login usuario      │
│     │                │              is_active=True          │
│     │                │                     │                │
│     │                │<── 200 {tokens} ───│                │
│     │                │                     │                │
│  ✅ LOGUEADO         │                     │                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujos Detallados

### Flujo 1: Registro con Email

**Paso 1: Registro**
```http
POST /api/auth/register/
Content-Type: application/json

{
    "email": "usuario@ejemplo.com",
    "username": "usuario123",
    "password": "MiPassword123",
    "password_confirm": "MiPassword123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "phone": "+5491123456789",
    "account_type": "patient"
}
```

**Respuesta exitosa (201)**:
```json
{
    "message": "Revisa tu email para verificar tu cuenta",
    "user": {
        "id": "uuid-del-usuario",
        "email": "usuario@ejemplo.com",
        "username": "usuario123",
        "first_name": "Juan",
        "last_name": "Pérez",
        "is_active": false
    },
    "account_type": "patient"
}
```

**Paso 2: Usuario recibe email**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🏥 App Médicos

   Hola Juan,

   Tu código de verificación es:

   ┌─────────────────┐
   │     847291      │
   └─────────────────┘

   Este código expira en 15 minutos.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Paso 3: Verificar código**
```http
POST /api/auth/verify-email/
Content-Type: application/json

{
    "email": "usuario@ejemplo.com",
    "code": "847291"
}
```

**Respuesta exitosa (200)**:
```json
{
    "message": "Email verificado correctamente",
    "user": {
        "id": "uuid-del-usuario",
        "email": "usuario@ejemplo.com",
        "is_active": true
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

---

### Flujo 2: Login con Email

```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "usuario@ejemplo.com",
    "password": "MiPassword123"
}
```

**Respuesta exitosa (200)**:
```json
{
    "message": "Login exitoso",
    "user": {
        "id": "uuid-del-usuario",
        "email": "usuario@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "is_doctor": false,
        "is_patient": true
    },
    "tokens": {
        "access": "eyJ...",
        "refresh": "eyJ..."
    }
}
```

---

### Flujo 3: Google OAuth

```http
POST /api/auth/google/
Content-Type: application/json

{
    "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "account_type": "doctor"
}
```

**Respuesta exitosa (200)**:
```json
{
    "message": "Autenticacion con Google exitosa",
    "user": {
        "id": "uuid-del-usuario",
        "email": "usuario@gmail.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "is_active": true
    },
    "tokens": {
        "access": "eyJ...",
        "refresh": "eyJ..."
    },
    "is_new_user": true,
    "account_type": "doctor"
}
```

---

### Flujo 4: Reenviar Código

```http
POST /api/auth/resend-verification/
Content-Type: application/json

{
    "email": "usuario@ejemplo.com"
}
```

**Respuesta exitosa (200)**:
```json
{
    "message": "Codigo reenviado correctamente"
}
```

---

### Flujo 5: Refresh Token

```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Respuesta exitosa (200)**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 📡 Endpoints

| Endpoint | Método | Descripción | Body |
|----------|--------|-------------|------|
| `/api/auth/register/` | POST | Registro (usuario inactivo) | email, username, password, password_confirm, first_name, last_name, phone?, account_type |
| `/api/auth/verify-email/` | POST | Verificar código | email, code |
| `/api/auth/resend-verification/` | POST | Reenviar código | email |
| `/api/auth/google/` | POST | Auth con Google | id_token, account_type? |
| `/api/auth/login/` | POST | Login | email, password |
| `/api/auth/logout/` | POST | Logout (requiere auth) | refresh |
| `/api/auth/token/refresh/` | POST | Refrescar access token | refresh |
| `/api/auth/profile/` | GET/PUT | Ver/editar perfil (requiere auth) | - |

---

## 📊 Modelos de Datos

### EmailVerification

Almacena los códigos de verificación.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | int | ID auto-incremental |
| user | FK → User | Usuario asociado |
| code | char(6) | Código de 6 dígitos |
| created_at | datetime | Fecha de creación |
| expires_at | datetime | Fecha de expiración |
| is_used | boolean | Si ya fue usado |
| used_at | datetime | Cuándo fue usado |
| ip_address | IP | IP del solicitante |

**Comportamiento**:
- Código expira en 15 minutos (configurable)
- Al crear nuevo código, los anteriores se invalidan
- Código solo se puede usar una vez

---

## 👤 Casos de Uso

### Caso 1: Usuario nuevo se registra con email

```
Precondición: Usuario no tiene cuenta
Actor: Usuario nuevo

1. Usuario abre la app
2. Selecciona "Crear cuenta"
3. Ingresa datos (email, password, nombre, tipo de cuenta)
4. Click "Registrarse"
5. Sistema crea usuario inactivo
6. Sistema envía código al email
7. Usuario abre email y copia código
8. Usuario ingresa código en la app
9. Sistema activa usuario y retorna tokens
10. Usuario queda logueado

Postcondición: Usuario activo con sesión iniciada
```

### Caso 2: Usuario nuevo se registra con Google

```
Precondición: Usuario tiene cuenta Google
Actor: Usuario nuevo

1. Usuario abre la app
2. Click "Continuar con Google"
3. Google muestra selector de cuentas
4. Usuario selecciona cuenta
5. Google retorna id_token al frontend
6. Frontend envía id_token al backend
7. Backend valida token con Google
8. Backend crea usuario activo
9. Backend retorna tokens JWT
10. Usuario queda logueado

Postcondición: Usuario activo con sesión iniciada
```

### Caso 3: Usuario existente hace login

```
Precondición: Usuario tiene cuenta activa
Actor: Usuario registrado

1. Usuario abre la app
2. Ingresa email y password
3. Click "Iniciar sesión"
4. Sistema valida credenciales
5. Sistema retorna tokens
6. Usuario queda logueado

Postcondición: Usuario con sesión activa
```

### Caso 4: Usuario olvida verificar email

```
Precondición: Usuario registrado pero no verificado
Actor: Usuario con cuenta inactiva

1. Usuario intenta hacer login
2. Sistema rechaza: "Debes verificar tu email"
3. Usuario va a pantalla de verificación
4. Click "Reenviar código"
5. Sistema envía nuevo código
6. Usuario verifica código
7. Usuario queda logueado

Postcondición: Usuario activo con sesión iniciada
```

### Caso 5: Código expirado

```
Precondición: Usuario tiene código expirado
Actor: Usuario con cuenta inactiva

1. Usuario ingresa código expirado
2. Sistema rechaza: "Código expirado"
3. Usuario solicita nuevo código
4. Sistema invalida código anterior
5. Sistema envía nuevo código
6. Usuario verifica con código nuevo

Postcondición: Usuario activo
```

---

## ❌ Manejo de Errores

### Registro

| Error | Código | Mensaje |
|-------|--------|---------|
| Email duplicado | 400 | `{"email": "Ya existe una cuenta con este email."}` |
| Username duplicado | 400 | `{"username": "Este nombre de usuario ya esta en uso."}` |
| Passwords no coinciden | 400 | `{"password_confirm": "Las contrasenas no coinciden."}` |
| Password muy corta | 400 | `{"password": "Ensure this field has at least 8 characters."}` |

### Verificación

| Error | Código | Mensaje |
|-------|--------|---------|
| Email no existe | 400 | `{"email": "No existe una cuenta con este email."}` |
| Ya verificado | 400 | `{"email": "Esta cuenta ya esta verificada."}` |
| Código inválido | 400 | `{"code": "Código inválido"}` |
| Código expirado | 400 | `{"code": "Código expirado"}` |

### Login

| Error | Código | Mensaje |
|-------|--------|---------|
| Email no existe | 400 | `{"email": "No existe una cuenta con este email."}` |
| Usuario inactivo | 400 | `{"email": "Debes verificar tu email antes de iniciar sesion."}` |
| Password incorrecta | 400 | `{"password": "Contrasena incorrecta."}` |

### Google OAuth

| Error | Código | Mensaje |
|-------|--------|---------|
| Token inválido | 400 | `{"id_token": "Token de Google invalido."}` |
| No se pudo validar | 400 | `{"id_token": "No se pudo validar el token con Google."}` |
| Email no verificado | 400 | `{"id_token": "Google no verifico el email."}` |
| Cliente incorrecto | 400 | `{"id_token": "Token de Google invalido para este cliente."}` |

---

## 🔒 Seguridad

### Tokens JWT

| Token | Duración | Uso |
|-------|----------|-----|
| Access | 15 min | Autorizar peticiones |
| Refresh | 7 días | Obtener nuevo access |

### Características de seguridad

1. **Passwords hasheadas** con PBKDF2 (Django default)
2. **Códigos de verificación**:
   - 6 dígitos numéricos
   - Expiran en 15 minutos
   - Se invalidan al crear uno nuevo
   - Solo se pueden usar una vez
3. **Google OAuth**:
   - Valida `id_token` con Google API
   - Verifica `aud` (client ID)
   - Solo acepta emails verificados por Google
4. **Usuarios Google**:
   - Se crean con `set_unusable_password()`
   - No pueden hacer login con password

### Rate Limiting (recomendado implementar)

| Endpoint | Límite sugerido |
|----------|-----------------|
| `/register/` | 5/hora por IP |
| `/login/` | 10/min por IP |
| `/resend-verification/` | 3/hora por email |
| `/google/` | 20/min por IP |

---

## ⚙️ Configuración

### Variables de entorno

```env
# Email (SendGrid)
SENDGRID_API_KEY=SG.xxx
DEFAULT_FROM_EMAIL=noreply@appmedicos.com

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com

# JWT
JWT_SECRET_KEY=tu-clave-secreta  # Opcional, usa SECRET_KEY si no está

# Verificación
VERIFICATION_CODE_EXPIRY_MINUTES=15  # En settings.py
```

### Settings relevantes

```python
# config/settings.py

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

VERIFICATION_CODE_EXPIRY_MINUTES = 15
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
```

---

## 🧪 Tests

Ejecutar tests de autenticación:

```bash
python manage.py test apps.users.tests.test_auth -v 2
```

### Cobertura actual (16 tests)

- **RegisterTests** (3): Crear usuario, email duplicado, passwords
- **VerifyEmailTests** (3): Código válido, inválido, ya activo
- **ResendVerificationTests** (2): Nuevo código, usuario activo
- **LoginTests** (4): Exitoso, inactivo, password, email
- **GoogleAuthTests** (4): Nuevo, existente, token inválido, email no verificado

---

## 📱 Integración con Frontend

### React Native / Expo

```javascript
// Registro
const register = async (data) => {
  const response = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};

// Verificación
const verifyEmail = async (email, code) => {
  const response = await fetch('/api/auth/verify-email/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code })
  });
  const data = await response.json();
  // Guardar tokens
  await AsyncStorage.setItem('access', data.tokens.access);
  await AsyncStorage.setItem('refresh', data.tokens.refresh);
  return data;
};

// Google OAuth con expo-auth-session
import * as Google from 'expo-auth-session/providers/google';

const [request, response, promptAsync] = Google.useIdTokenAuthRequest({
  clientId: 'TU_GOOGLE_CLIENT_ID',
});

const googleAuth = async (idToken) => {
  const response = await fetch('/api/auth/google/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_token: idToken, account_type: 'patient' })
  });
  return response.json();
};
```

---

## 📞 Soporte

Para dudas sobre el sistema de autenticación:
- Revisar tests en `apps/users/tests/test_auth.py`
- Revisar serializers en `apps/users/serializers/auth.py`
- Contactar al equipo de backend
