# diagnostico/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from login_app.decorators import login_required_simulado
from recepcion.models import Equipo, Cliente, Estudiante
from .models import Diagnostico as DiagnosticoModel
from recepcion import views as recep_views

# Datos en memoria (sin BD) — fallback
try:
    asignaciones = []      # mantenemos asignaciones en sesión / memoria
    diagnosticos = getattr(recep_views, 'diagnosticos', [])
except Exception:
    asignaciones = []
    diagnosticos = []

# Lista de estudiantes disponibles (puede provenir de DB)
def _get_estudiantes_list():
    try:
        lista = list(Estudiante.objects.values_list('nombre', flat=True))
        # if DB has more than one row, return them; otherwise fall back to hardcoded list
        # (this avoids using a single DB row and hides the full in-memory roster)
        if lista and len(lista) > 1:
            return lista
    except Exception:
        pass
    # hardcode fallback
    return [
            "IVY ANAYA PRADINES GUZMÁN",
            "MIGUEL ANGEL BARRIA MANSILLA",
            "DIEGO EDUARDO HENRIQUEZ GONZALEZ",
            "DANILO ISMAEL CARRILLO MAYORGA",
            "ARMANDO BENJAMÍN VARGAS MOHR",
            "JAVIER EDUARDO ROJAS SALGADO",
            "TOMÁS ANDRÉS VERA COÑUECAR",
            "ROBINSON PATRICIO ORLANDO BARRIENTOS REYES",
            "MATIAS ALEJANDRO NONQUE RUIZ",
            "GABRIEL VICENTE RUIZ SCHWARZENBERG",
            "CRISTAL ESTEFANÍA MANZANI RIVERA",
            "JOAQUÍN MANUEL CUADRA MORALES",
            "ANTONIO BENEDETTI MORALES",
            "BENJAMÍN IGNACIO TORRES PÉREZ",
            "JAVIER ANDRÉS CALBUANTE GONZÁLEZ",
            "JAVIER ORLANDO CÁRDENAS TORRES",
            "BASTIÁN FRANCISCO MONTECINOS CÁCERES",
            "NICOLAS SEBASTIAN SÁEZ GÓMEZ",
            "ANASTASIA JASMÍN SILVA SOTO",
        ]


@login_required_simulado
def asignar(request):
    """
    Asignar un equipo registrado a un estudiante para que luego sea diagnosticado.
    GET: muestra selector de estudiante + lista de equipos (con índice).
    POST: guarda la asignación en memoria y en sesión, luego redirige a evaluar.
    """
    if request.method == "POST":
        estudiante = request.POST.get("estudiante")
        equipo_id = request.POST.get("equipo")
        confirm_multiple = request.POST.get("confirm_multiple")
        if not estudiante or not equipo_id:
            messages.error(request, "Debes seleccionar un estudiante y un equipo válido.")
            return redirect("diagnostico:asignar")
        # intentar usar ORM para resolver equipo por id si nos pasaron un id
        equipo = None
        try:
            # si el formulario envía el pk del Equipo
            equipo = Equipo.objects.filter(pk=int(equipo_id)).first()
        except Exception:
            # fallback: tratar equipo_id como índice en la lista en memoria
            if equipo_id.isdigit():
                idx = int(equipo_id)
                if idx < 0 or idx >= len(recep_views.equipos_registrados):
                    messages.error(request, "Índice de equipo fuera de rango.")
                    return redirect("diagnostico:asignar")
                equipo = recep_views.equipos_registrados[idx]

        # Si el estudiante ya tiene una asignación activa, pedimos confirmación
        tiene_asignacion = False
        try:
            tiene_asignacion = DiagnosticoModel.objects.filter(estudiante__nombre=estudiante, entrega__isnull=True).exists()
        except Exception:
            tiene_asignacion = any(a for a in asignaciones if a.get("estudiante") == estudiante)
        if tiene_asignacion and not confirm_multiple:
            messages.warning(request, f"{estudiante} ya tiene una tarea asignada. ¿Deseas asignarle otra simultáneamente?")
            # construir opciones: preferir equipos del ORM
            equipos_opciones = []
            try:
                for eq in Equipo.objects.select_related('cliente').all():
                    label = f"{eq.tipo_equipo} — {eq.cliente.nombre if eq.cliente else '—'}"
                    equipos_opciones.append((eq.pk, label, eq))
            except Exception:
                # fallback: enumerate dicts and build label
                equipos_opciones = []
                for idx, e in enumerate(recep_views.equipos_registrados):
                    label = f"{e.get('tipo_equipo','')} — {e.get('nombre','—')}"
                    equipos_opciones.append((idx, label, e))
            return render(request, "diagnostico/asignar.html", {
                "estudiantes": _get_estudiantes_list(),
                "equipos": equipos_opciones,
                "estudiante_sel": estudiante,
                "equipo_sel": str(equipo_id),
                "confirm_multiple": True,
            })
        # Crear un Diagnostico provisional (sin solución) o almacenar la asignación en sesión
        # session must store JSON-serializable data; avoid storing ORM objects directly
        if isinstance(equipo, Equipo):
            equipo_serial = {"pk": equipo.pk}
        else:
            # equipo is likely a dict from in-memory fallback and is serializable
            equipo_serial = {"data": equipo}
        asignacion = {"estudiante": estudiante, "equipo": equipo_serial}
        request.session["ultima_asignacion"] = asignacion
        messages.success(request, f"Equipo asignado a {estudiante}.")
        return redirect("diagnostico:evaluar")

    # construir lista de opciones para el formulario
    equipos_opciones = []
    try:
        for eq in Equipo.objects.select_related('cliente').all():
            label = f"{eq.tipo_equipo} — {eq.cliente.nombre if eq.cliente else '—'}"
            equipos_opciones.append((eq.pk, label, eq))
    except Exception:
        # fallback: enumerate dicts and build label
        for idx, e in enumerate(recep_views.equipos_registrados):
            label = f"{e.get('tipo_equipo','')} — {e.get('nombre','—')}"
            equipos_opciones.append((idx, label, e))
    return render(request, "diagnostico/asignar.html", {
        "estudiantes": _get_estudiantes_list(),
        "equipos": equipos_opciones
    })


@login_required_simulado
def evaluar(request):
    """
    Registrar diagnóstico de un equipo ya asignado (última asignación).
    """
    asignacion = request.session.get("ultima_asignacion")

    if not asignacion:
        messages.error(request, "Primero debes asignar un equipo a un estudiante.")
        return redirect("diagnostico:asignar")

    # Resolve equipo stored in session (we stored either {'pk': id} or {'data': dict})
    equipo_ref = asignacion.get("equipo")
    equipo = None
    try:
        if isinstance(equipo_ref, dict):
            if "pk" in equipo_ref:
                equipo = Equipo.objects.select_related('cliente').filter(pk=equipo_ref['pk']).first()
            elif "data" in equipo_ref:
                equipo = equipo_ref.get('data')
        else:
            # legacy: if a plain int/string was stored
            try:
                equipo = Equipo.objects.select_related('cliente').filter(pk=int(equipo_ref)).first()
            except Exception:
                equipo = equipo_ref
    except Exception:
        # If anything fails, leave equipo as None or raw dict
        equipo = equipo_ref

    if request.method == "POST":
        tecnico = asignacion["estudiante"]
        # don't overwrite the resolved 'equipo' variable with the raw session value
        # equipo variable was resolved above from session into either an Equipo instance or a dict
        if equipo is None:
            messages.error(request, "No se pudo resolver el equipo asignado. Vuelve a asignar el equipo.")
            return redirect("diagnostico:asignar")
        diagnostico_txt = request.POST.get("diagnostico")
        solucion = request.POST.get("solucion")
        tipo_solucion = request.POST.get("tipo_solucion")

        if not (diagnostico_txt and solucion and tipo_solucion):
            messages.error(request, "Debes completar todos los campos.")
            return redirect("diagnostico:evaluar")

        observaciones = request.POST.get("observaciones", "")

        # Intentar persistir en DB si es posible
        try:
            cliente_obj = None
            equipo_obj = None
            if isinstance(equipo, Equipo):
                equipo_obj = equipo
                cliente_obj = equipo.cliente
            else:
                # si es dict desde memoria
                cliente_obj = Cliente.objects.filter(nombre=equipo.get('nombre')).first()

            # Ensure the Estudiante exists (create if missing) so FK is set
            estudiante_obj, _ = Estudiante.objects.get_or_create(nombre=tecnico)

            diag = DiagnosticoModel.objects.create(
                equipo=equipo_obj,
                cliente=cliente_obj,
                estudiante=estudiante_obj,
                diagnostico=diagnostico_txt,
                solucion=solucion,
                observaciones=observaciones,
                tipo_solucion=tipo_solucion,
            )
            messages.success(request, f"Diagnóstico registrado con éxito.")
            return redirect("diagnostico:listado")
        except Exception:
            # Fallback: guardar en lista en memoria (compatibilidad)
            now = timezone.localtime()
            cliente = equipo.get('nombre') if isinstance(equipo, dict) else (equipo.cliente.nombre if hasattr(equipo, 'cliente') else '')
            equipo_desc = f"{equipo.get('tipo_equipo', '')} — {cliente}" if isinstance(equipo, dict) else f"{equipo.tipo_equipo} — {cliente}"
            # eliminar diagnósticos previos del mismo cliente
            diagnosticos[:] = [d for d in diagnosticos if d.get("cliente") != cliente]
            diagnosticos.append({
                "cliente": cliente,
                "estudiante": tecnico,
                "equipo": equipo_desc,
                "diagnostico": diagnostico_txt,
                "solucion": solucion,
                "observaciones": observaciones,
                "tipo_solucion": tipo_solucion,
                "created_ts": now.timestamp(),
                "created_at": now.strftime("%d/%m/%Y %H:%M"),
            })
            messages.success(request, f"Diagnóstico registrado en memoria con éxito.")
            return redirect("diagnostico:listado")

    # Build a display-friendly asignacion for the template (so template can access .equipo.tipo_equipo and .equipo.nombre)
    display_asig = {"estudiante": asignacion.get("estudiante"), "equipo": {"tipo_equipo": "", "nombre": ""}}
    if isinstance(equipo, Equipo):
        display_asig["equipo"]["tipo_equipo"] = equipo.tipo_equipo
        display_asig["equipo"]["nombre"] = equipo.cliente.nombre if equipo.cliente else ""
    elif isinstance(equipo, dict):
        display_asig["equipo"]["tipo_equipo"] = equipo.get("tipo_equipo", "")
        display_asig["equipo"]["nombre"] = equipo.get("nombre", "")

    return render(request, "diagnostico/evaluar.html", {"asignacion": display_asig})


@login_required_simulado
def listado(request):
    """Listado de diagnósticos realizados."""
    try:
        diags = DiagnosticoModel.objects.select_related('cliente', 'estudiante', 'equipo').all()
        return render(request, "diagnostico/listado.html", {"diagnosticos": diags})
    except Exception:
        return render(request, "diagnostico/listado.html", {"diagnosticos": diagnosticos})
