# diagnostico/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from login_app.decorators import login_required_simulado
from recepcion.views import equipos_registrados  # usamos los equipos registrados en Recepción

# Datos en memoria (sin BD)
asignaciones = []      # equipos asignados a estudiantes para diagnóstico
diagnosticos = []      # diagnósticos realizados (se usa en Entrega y Dashboard)

# Lista de estudiantes disponibles (puedes unificarla si ya la mantienes en otra app)
estudiantes = [
    "IVY ANAYA PRADINES GUZMÁN",
    "MIGUEL ANGEL BARRIA MANSILLA",
    "DIEGO EDUARDO HENRIQUEZ GONZÁLEZ",
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
    POST: guarda la asignación y redirige a evaluar.
    """
    if request.method == "POST":
        estudiante = request.POST.get("estudiante")
        equipo_id = request.POST.get("equipo")

        # Validaciones básicas
        if not estudiante:
            messages.error(request, "Debes seleccionar un estudiante.")
            return redirect("diagnostico:asignar")

        if not equipo_id or not equipo_id.isdigit():
            messages.error(request, "Debes seleccionar un equipo válido.")
            return redirect("diagnostico:asignar")

        equipo_idx = int(equipo_id)

        if equipo_idx < 0 or equipo_idx >= len(equipos_registrados):
            messages.error(request, "Índice de equipo fuera de rango.")
            return redirect("diagnostico:asignar")

        equipo = equipos_registrados[equipo_idx]
        asignaciones.append({"estudiante": estudiante, "equipo": equipo})

        messages.success(
            request,
            f"Equipo '{equipo.get('tipo_equipo', 'Equipo')}' de {equipo.get('nombre')} "
            f"asignado a {estudiante}."
        )
        return redirect("diagnostico:evaluar")

    # GET: pasamos los equipos disponibles con su índice para el <select>
    equipos_opciones = list(enumerate(equipos_registrados))
    return render(request, "diagnostico/asignar.html", {
        "estudiantes": estudiantes,
        "equipos": equipos_opciones
    })


@login_required_simulado
def evaluar(request):
    """
    Registrar diagnóstico de un equipo ya asignado.
    GET: muestra formulario.
    POST: guarda diagnóstico (mutando la lista en sitio para no romper importaciones).
    """
    if request.method == "POST":
        estudiante = request.POST.get("estudiante")
        equipo_desc = request.POST.get("equipo")
        diagnostico_txt = request.POST.get("diagnostico")
        solucion = request.POST.get("solucion")
        tipo_solucion = request.POST.get("tipo_solucion")

        # Validaciones
        if not (estudiante and equipo_desc and diagnostico_txt and solucion and tipo_solucion):
            messages.error(request, "Debes completar todos los campos.")
            return redirect("diagnostico:evaluar")

        now = timezone.localtime()

        # ✅ Mutamos EN SITIO para mantener el mismo objeto 'diagnosticos'
        diagnosticos[:] = [d for d in diagnosticos if d.get("estudiante") != estudiante]

        diagnosticos.append({
            "estudiante": estudiante,
            "equipo": equipo_desc,                  # texto legible (ej: "Notebook de Juan")
            "diagnostico": diagnostico_txt,
            "solucion": solucion,
            "tipo_solucion": tipo_solucion,        # ej: "Software", "Hardware", etc.
            "created_ts": now.timestamp(),         # para ordenar por fecha
            "created_at": now.strftime("%d/%m/%Y %H:%M"),  # para mostrar en UI
        })

        messages.success(request, f"Diagnóstico de {equipo_desc} registrado con éxito.")
        return redirect("diagnostico:listado")

    # GET: pasamos asignaciones para facilitar selección en el formulario (opcional)
    return render(request, "diagnostico/evaluar.html", {
        "asignaciones": asignaciones
    })


@login_required_simulado
def listado(request):
    """
    Listado de diagnósticos realizados.
    """
    return render(request, "diagnostico/listado.html", {
        "diagnosticos": diagnosticos
    })
