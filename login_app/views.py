# login_app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from login_app.decorators import login_required_simulado

# Credenciales fijas (login simulado)
VALID_USER = "inacap"
VALID_PASS = "clinica2025"


def login_view(request):
    """
    Pantalla de inicio de sesión con credenciales fijas.
    Guarda 'autenticado' en sesión cuando el login es correcto.
    """
    # Si ya está autenticado, ir directo al dashboard
    if request.session.get("autenticado"):
        return redirect("dashboard")

    if request.method == "POST":
        usuario = request.POST.get("usuario", "").strip()
        clave = request.POST.get("clave", "").strip()

        if usuario == VALID_USER and clave == VALID_PASS:
            request.session["autenticado"] = True
            messages.success(request, "Sesión iniciada correctamente.")
            return redirect("dashboard")
        else:
            messages.error(request, "Usuario o clave incorrectos.")

    # Importante: sin placeholders ni autocompletado en el template (ya ajustado)
    return render(request, "login_app/login.html")


@login_required_simulado
def dashboard(request):
    """
    Dashboard con KPIs y atajos. Importa las listas en memoria desde otras apps.
    Hacemos 'imports' DENTRO de la función para evitar importaciones circulares.
    """
    # Importaciones perezosas para evitar ciclos
    from recepcion.views import equipos_registrados
    from diagnostico.views import diagnosticos
    from entrega.views import entregas

    # Totales
    total_recepcion = len(equipos_registrados)
    total_diagnosticos = len(diagnosticos)
    total_entregas = len(entregas)

    # Porcentajes (con protección de división por cero)
    pct_recepcion = 100 if total_recepcion > 0 else 0
    pct_diag_vs_rec = int((total_diagnosticos / total_recepcion) * 100) if total_recepcion else 0
    pct_entrega_vs_diag = int((total_entregas / total_diagnosticos) * 100) if total_diagnosticos else 0

    # Pendientes de entrega (diagnosticados que no aparecen en entregas)
    set_diag = {d.get("estudiante") for d in diagnosticos}
    set_entregados = {e.get("nombre") for e in entregas}
    pendientes_list = sorted(list(set_diag - set_entregados))
    pendientes_entrega = len(pendientes_list)

    # Actividad reciente (últimos eventos simples; sin timestamps aún)
    recientes = []
    for eq in equipos_registrados[-3:][::-1]:
        recientes.append({
            "txt": f"Recepción: {eq.get('tipo_equipo', 'Equipo')} de {eq.get('nombre', '—')}",
            "when": "Reciente",
        })
    for d in diagnosticos[-3:][::-1]:
        recientes.append({
            "txt": f"Diagnóstico: {d.get('estudiante', '—')} · {d.get('tipo_solucion', '').capitalize()}",
            "when": "Reciente",
        })
    for e in entregas[-3:][::-1]:
        recientes.append({
            "txt": f"Entrega: {e.get('nombre', '—')} · {e.get('estado', '').capitalize()}",
            "when": "Reciente",
        })
    recientes = recientes[:5]

    context = {
        "total_recepcion": total_recepcion,
        "total_diagnosticos": total_diagnosticos,
        "total_entregas": total_entregas,
        "pct_recepcion": pct_recepcion,
        "pct_diag_vs_rec": pct_diag_vs_rec,
        "pct_entrega_vs_diag": pct_entrega_vs_diag,
        "pendientes_entrega": pendientes_entrega,
        "pendientes_list": pendientes_list,
        "recientes": recientes,
    }
    return render(request, "login_app/dashboard.html", context)


def logout_view(request):
    """
    Cierra la sesión y vuelve al login.
    """
    request.session.flush()
    messages.info(request, "Sesión finalizada.")
    return redirect("login")
