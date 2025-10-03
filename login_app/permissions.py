from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def role_required(*allowed_roles):
    """
    Decorador que requiere que el usuario tenga uno de los roles especificados.
    Los roles se determinan por los grupos de Django.
    
    Uso: @role_required('recepcion', 'admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Admin siempre tiene acceso a todo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar si el usuario pertenece a alguno de los grupos permitidos
            user_groups = set(request.user.groups.values_list('name', flat=True))
            
            if any(role in user_groups for role in allowed_roles):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('dashboard')
        
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Decorador que requiere permisos de administrador.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Solo los administradores pueden acceder a esta sección.')
            return redirect('dashboard')
    
    return _wrapped_view


def get_user_role(user):
    """
    Obtiene el rol principal del usuario basado en sus grupos.
    """
    if user.is_superuser:
        return 'admin'
    
    groups = user.groups.values_list('name', flat=True)
    
    # Orden de prioridad de roles
    role_priority = ['recepcion', 'diagnostico', 'hardware', 'software', 'despacho']
    
    for role in role_priority:
        if role in groups:
            return role
    
    return 'usuario'  # rol por defecto


def get_allowed_sections(user):
    """
    Obtiene las secciones a las que el usuario tiene acceso.
    """
    if user.is_superuser:
        return ['dashboard', 'recepcion', 'diagnostico', 'derivacion', 'hardware', 'software', 'despacho']
    
    groups = set(user.groups.values_list('name', flat=True))
    allowed = ['dashboard']  # dashboard siempre disponible
    
    if 'recepcion' in groups:
        allowed.append('recepcion')
    
    if 'diagnostico' in groups:
        allowed.extend(['diagnostico', 'derivacion'])
    
    if 'hardware' in groups:
        allowed.append('hardware')
    
    if 'software' in groups:
        allowed.append('software')
    
    if 'despacho' in groups:
        allowed.append('despacho')
    
    return allowed


# Decorador legacy para compatibilidad (reemplazado por role_required)
def login_required_simulado(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect("login_app:login")
        return view_func(request, *args, **kwargs)
    return wrapper