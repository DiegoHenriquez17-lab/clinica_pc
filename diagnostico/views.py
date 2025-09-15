from django.shortcuts import render, redirect
from django.contrib import messages
from login_app.decorators import session_required
from recepcion.views import equipos_registrados   # 👈 usamos equipos ya registrados

# Datos simulados
asignaciones = []      # lista de equipos asignados a estudiantes
diagnosticos = []      # lista de diagnósticos realizados

# Lista de estudiantes disponibles
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

@session_required
def asignar(request):
    if request.method == "POST":
        estudiante = request.POST.get("estudiante")
        equipo_id = request.POST.get("equipo")

        if not equipo_id:
            messages.error(request, "Debes seleccionar un equipo válido.")
            return redirect("diagnostico:asignar")

        equipo_id = int(equipo_id)
        equipo = equipos_registrados[equipo_id]

        asignaciones.append({"estudiante": estudiante, "equipo": equipo})
        messages.success(
            request,
            f"Equipo '{equipo['tipo_equipo']}' de {equipo['nombre']} asignado a {estudiante}."
        )
        return redirect("diagnostico:evaluar")

    # Pasamos los equipos disponibles (con índice)
    equipos_opciones = list(enumerate(equipos_registrados))
    return render(request, "diagnostico/asignar.html", {
        "estudiantes": estudiantes,
        "equipos": equipos_opciones
    })


@session_required
def evaluar(request):
    if request.method == "POST":
        estudiante = request.POST.get("estudiante")
        equipo_desc = request.POST.get("equipo")
        diagnostico = request.POST.get("diagnostico")
        solucion = request.POST.get("solucion")
        tipo_solucion = request.POST.get("tipo_solucion")

        diagnosticos.append({
            "estudiante": estudiante,
            "equipo": equipo_desc,
            "diagnostico": diagnostico,
            "solucion": solucion,
            "tipo_solucion": tipo_solucion
        })
        messages.success(request, f"Diagnóstico de {equipo_desc} registrado con éxito.")
        return redirect("diagnostico:listado")

    return render(request, "diagnostico/evaluar.html", {
        "asignaciones": asignaciones
    })


@session_required
def listado(request):
    return render(request, "diagnostico/listado.html", {
        "diagnosticos": diagnosticos
    })
