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




