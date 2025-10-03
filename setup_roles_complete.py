#!/usr/bin/env python
"""
Script para configurar el sistema de roles y permisos de la clínica
"""
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

def create_roles():
    """Crear grupos y asignar permisos"""
    
    # Crear grupos si no existen
    groups_config = {
        'administradores': {
            'description': 'Acceso completo al sistema',
            'permissions': 'all'
        },
        'recepcion': {
            'description': 'Recepción y registro de equipos',
            'permissions': ['recepcion']
        },
        'diagnostico': {
            'description': 'Diagnóstico y derivación de equipos',
            'permissions': ['diagnostico']
        },
        'hardware': {
            'description': 'Reparaciones de hardware',
            'permissions': ['hardware']
        },
        'software': {
            'description': 'Reparaciones de software',
            'permissions': ['software']
        },
        'despacho': {
            'description': 'Entrega de equipos',
            'permissions': ['despacho']
        }
    }
    
    print("Creando grupos...")
    for group_name, config in groups_config.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"✓ Grupo '{group_name}' creado")
        else:
            print(f"- Grupo '{group_name}' ya existe")
    
    # Configurar usuarios
    users_config = [
        {
            'username': 'admin',
            'password': 'admin123',
            'is_superuser': True,
            'is_staff': True,
            'groups': ['administradores']
        },
        {
            'username': 'recepcion',
            'password': 'recepcion123',
            'is_staff': True,
            'groups': ['recepcion']
        },
        {
            'username': 'diagnostico',  
            'password': 'diagnostico123',
            'is_staff': True,
            'groups': ['diagnostico']
        },
        {
            'username': 'hardware',
            'password': 'hardware123', 
            'is_staff': True,
            'groups': ['hardware']
        },
        {
            'username': 'software',
            'password': 'software123',
            'is_staff': True, 
            'groups': ['software']
        },
        {
            'username': 'despacho',
            'password': 'despacho123',
            'is_staff': True,
            'groups': ['despacho']
        }
    ]
    
    print("\nConfigurando usuarios...")
    for user_config in users_config:
        username = user_config['username']
        
        # Crear o actualizar usuario
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'is_superuser': user_config.get('is_superuser', False),
                'is_staff': user_config.get('is_staff', False),
            }
        )
        
        if created:
            user.set_password(user_config['password'])
            user.save()
            print(f"✓ Usuario '{username}' creado")
        else:
            print(f"- Usuario '{username}' ya existe")
        
        # Asignar grupos
        user.groups.clear()  # Limpiar grupos existentes
        for group_name in user_config['groups']:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
                print(f"  → Asignado al grupo '{group_name}'")
            except Group.DoesNotExist:
                print(f"  ✗ Grupo '{group_name}' no existe")
    
    print("\n" + "="*50)
    print("SISTEMA DE ROLES CONFIGURADO")
    print("="*50)
    print("\nCredenciales de acceso:")
    print("-" * 30)
    for user_config in users_config:
        username = user_config['username']
        password = user_config['password']
        groups = ", ".join(user_config['groups'])
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")
        print(f"Acceso: {groups}")
        print("-" * 30)
    
    print("\nCada usuario solo verá las secciones de su rol:")
    print("• admin: Todas las secciones")
    print("• recepcion: Solo recepción de equipos")
    print("• diagnostico: Solo diagnóstico y derivación")
    print("• hardware: Solo reparaciones de hardware")
    print("• software: Solo reparaciones de software")
    print("• despacho: Solo entrega de equipos")

if __name__ == '__main__':
    create_roles()