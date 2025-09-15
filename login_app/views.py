# login_app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages

# Credenciales fijas
VALID_USER = "inacap"
VALID_PASS = "clinica2025"


def login_view(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        clave = request.POST.get("clave")

        # Validación con credenciales fijas
        if usuario == VALID_USER and clave == VALID_PASS:
            request.session["autenticado"] = True  # Guardamos sesión
            return redirect("dashboard")
        else:
            messages.error(request, "Usuario o clave incorrectos")

    return render(request, "login_app/login.html")


def dashboard(request):
    # Protegemos el acceso manualmente con sesión
    if not request.session.get("autenticado"):
        return redirect("login")
    return render(request, "login_app/dashboard.html")


def logout_view(request):
    request.session.flush()  # Cierra la sesión
    return redirect("login")
