from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, Doctor, Patient, Specialty


class DoctorInline(admin.StackedInline):
    model = Doctor
    can_delete = False
    fk_name = 'user'
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    verbose_name = 'Perfil de Doctor'
    verbose_name_plural = 'Perfil de Doctor'


class PatientInline(admin.StackedInline):
    model = Patient
    can_delete = False
    fk_name = 'user'
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    verbose_name = 'Perfil de Paciente'
    verbose_name_plural = 'Perfil de Paciente'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'get_role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'deleted_at')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'created_at', 'updated_at', 'deleted_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    inlines = (DoctorInline, PatientInline)
    
    @admin.display(description='Nombre Completo')
    def full_name(self, obj):
        return obj.full_name
    
    @admin.display(description='Rol')
    def get_role(self, obj):
        if obj.is_doctor:
            return format_html('<span style="color: #1976d2;">Doctor</span>')
        elif obj.is_patient:
            return format_html('<span style="color: #388e3c;">Paciente</span>')
        return format_html('<span style="color: #757575;">Sin perfil</span>')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'license_number', 'get_user_email', 'get_specialties', 'is_active', 'created_at')
    list_filter = ('is_active', 'specialties', 'deleted_at')
    search_fields = ('license_number', 'user__email', 'user__first_name', 'user__last_name', 'university')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('user',)
    
    fieldsets = (
        ('Usuario', {'fields': ('user',)}),
        ('Información Profesional', {'fields': ('license_number', 'university', 'bio')}),
        ('Ubicación', {'fields': ('address',)}),
        ('Imagen', {'fields': ('image_url',)}),
        ('Estado', {'fields': ('is_active', 'deleted_at')}),
        ('Metadatos', {'fields': ('id', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    @admin.display(description='Nombre')
    def get_full_name(self, obj):
        return f"Dr. {obj.user.full_name}"
    
    @admin.display(description='Email')
    def get_user_email(self, obj):
        return obj.user.email
    
    @admin.display(description='Especialidades')
    def get_specialties(self, obj):
        specialties = obj.specialties.all()[:3]
        if specialties:
            return ', '.join([s.name for s in specialties])
        return '-'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'dni', 'get_user_email', 'get_age', 'insurance_provider', 'created_at')
    list_filter = ('insurance_provider', 'deleted_at')
    search_fields = ('dni', 'user__email', 'user__first_name', 'user__last_name', 'insurance_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('user',)
    
    fieldsets = (
        ('Usuario', {'fields': ('user',)}),
        ('Información Personal', {'fields': ('dni', 'birth_date')}),
        ('Cobertura Médica', {'fields': ('insurance_provider', 'insurance_plan', 'insurance_number')}),
        ('Imagen', {'fields': ('image_url',)}),
        ('Estado', {'fields': ('deleted_at',)}),
        ('Metadatos', {'fields': ('id', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    @admin.display(description='Nombre')
    def get_full_name(self, obj):
        return obj.user.full_name
    
    @admin.display(description='Email')
    def get_user_email(self, obj):
        return obj.user.email
    
    @admin.display(description='Edad')
    def get_age(self, obj):
        age = obj.age
        return f"{age} años" if age else '-'


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_doctors_count', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at')
    filter_horizontal = ('doctors',)
    
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Doctores', {'fields': ('doctors',)}),
        ('Metadatos', {'fields': ('id', 'created_at'), 'classes': ('collapse',)}),
    )
    
    @admin.display(description='Nº Doctores')
    def get_doctors_count(self, obj):
        return obj.doctors.count()
