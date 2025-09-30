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
    # Preferir lectura desde la base de datos (ORM). Fallback a listas en memoria si ocurre algún error.
    try:
        from recepcion.models import Equipo
        from diagnostico.models import Diagnostico as DiagnosticoModel
        from entrega.models import Entrega as EntregaModel

        total_recepcion = Equipo.objects.count()
        total_diagnosticos = DiagnosticoModel.objects.count()
        total_entregas = EntregaModel.objects.count()

        pct_recepcion = 100 if total_recepcion > 0 else 0
        pct_diag_vs_rec = int((total_diagnosticos / total_recepcion) * 100) if total_recepcion else 0
        pct_entrega_vs_diag = int((total_entregas / total_diagnosticos) * 100) if total_diagnosticos else 0

        # Pendientes de entrega: clientes con diagnóstico sin entrega
        diag_clientes = set(DiagnosticoModel.objects.values_list('cliente__nombre', flat=True))
        entregados = set(EntregaModel.objects.select_related('diagnostico__cliente').values_list('diagnostico__cliente__nombre', flat=True))
        pendientes_list = sorted(list(set([c for c in diag_clientes if c]) - set([e for e in entregados if e])))
        pendientes_entrega = len(pendientes_list)

        # Actividad reciente: combinar últimas recepciones, diagnósticos y entregas
        recientes = []
        # últimas recepciones (por fecha creada si existe)
        for eq in Equipo.objects.select_related('cliente').order_by('-created_at')[:3]:
            recientes.append({"txt": f"Recepción: {eq.tipo_equipo} de {eq.cliente.nombre}", "when": "Reciente"})
        for d in DiagnosticoModel.objects.select_related('estudiante').order_by('-created_at')[:3]:
            recientes.append({"txt": f"Diagnóstico: {d.estudiante.nombre if d.estudiante else '—'} · {d.tipo_solucion.capitalize()}", "when": "Reciente"})
        for ent in EntregaModel.objects.select_related('diagnostico__cliente').order_by('-fecha_entrega')[:3]:
            recientes.append({"txt": f"Entrega: {ent.diagnostico.cliente.nombre} · Entregado", "when": "Reciente"})
        recientes = recientes[:5]

    except Exception:
        # Fallback a listas en memoria para compatibilidad
        from recepcion.views import equipos_registrados
        from diagnostico.views import diagnosticos
        from entrega.views import entregas

        total_recepcion = len(equipos_registrados)
        total_diagnosticos = len(diagnosticos)
        total_entregas = len(entregas)

        pct_recepcion = 100 if total_recepcion > 0 else 0
        pct_diag_vs_rec = int((total_diagnosticos / total_recepcion) * 100) if total_recepcion else 0
        pct_entrega_vs_diag = int((total_entregas / total_diagnosticos) * 100) if total_diagnosticos else 0

        def _infer_cliente_from_equipo(equipo_str: str) -> str:
            if not equipo_str:
                return ""
            parts = equipo_str.split("—")
            if len(parts) >= 2:
                return parts[-1].strip()
            return equipo_str.strip()

        set_diag = set()
        for d in diagnosticos:
            if d.get("cliente"):
                candidato = d.get("cliente")
            else:
                candidato = _infer_cliente_from_equipo(d.get("equipo", "")) or d.get("estudiante", "")
            if candidato:
                set_diag.add(candidato)

        set_entregados = {e.get("nombre") for e in entregas}
        pendientes_list = sorted(list(set_diag - set_entregados))
        pendientes_entrega = len(pendientes_list)

        recientes = []
        for eq in equipos_registrados[-3:][::-1]:
            recientes.append({"txt": f"Recepción: {eq.get('tipo_equipo', 'Equipo')} de {eq.get('nombre', '—')}", "when": "Reciente"})
        for d in diagnosticos[-3:][::-1]:
            recientes.append({"txt": f"Diagnóstico: {d.get('estudiante', '—')} · {d.get('tipo_solucion', '').capitalize()}", "when": "Reciente"})
        for e in entregas[-3:][::-1]:
            recientes.append({"txt": f"Entrega: {e.get('nombre', '—')} · {e.get('estado', '').capitalize()}", "when": "Reciente"})
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
