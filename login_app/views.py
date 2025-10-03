# login_app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    """
    Vista de inicio de sesión usando el sistema de autenticación de Django.
    """
    # Si ya está autenticado, ir directo al dashboard
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        usuario = request.POST.get("usuario", "").strip()
        clave = request.POST.get("clave", "").strip()

        if usuario and clave:
            user = authenticate(request, username=usuario, password=clave)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido, {user.username}!")
                return redirect("dashboard")
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Por favor ingrese usuario y contraseña.")

    return render(request, "login_app/login.html")


def logout_view(request):
    """
    Vista de cierre de sesión.
    """
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("login_app:login")