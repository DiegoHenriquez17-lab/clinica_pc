# recepcion/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from login_app.decorators import login_required_simulado

# Lista global en memoria (sin BD)
equipos_registrados = []

# Lista fija de estudiantes
estudiantes = [
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

# Lista fija de tipos de equipos
tipos_equipos = [
    "Notebook",
    "PC de Escritorio",
    "Tablet",
    "Impresora",
    "Celular",
    "Servidor",
]

@login_required_simulado
def registrar(request):
    """
    Vista única para GET (mostrar formulario) y POST (registrar equipo).
    """
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        tipo_equipo = request.POST.get("tipo_equipo")
        problema = request.POST.get("problema")

        # Validaciones simples (opcional)
        if not nombre or not tipo_equipo or not problema:
            messages.error(request, "Completa todos los campos.")
            return render(request, "recepcion/registrar.html", {
                "estudiantes": estudiantes,
                "tipos_equipos": tipos_equipos,
                "nombre": nombre,
                "tipo_equipo": tipo_equipo,
                "problema": problema,
            })

        equipos_registrados.append({
            "nombre": nombre,
            "tipo_equipo": tipo_equipo,
            "problema": problema
        })

        messages.success(request, f"Equipo de {nombre} registrado con éxito.")
        return redirect("recepcion:listado")

    # GET
    return render(request, "recepcion/registrar.html", {
        "estudiantes": estudiantes,
        "tipos_equipos": tipos_equipos
    })


@login_required_simulado
def listado(request):
    return render(request, "recepcion/listado.html", {"equipos": equipos_registrados})


@login_required_simulado
def detalle(request, nombre):
    equipo = next((eq for eq in equipos_registrados if eq["nombre"] == nombre), None)
    if not equipo:
        messages.error(request, "No se encontró el equipo solicitado.")
        return redirect("recepcion:listado")
    return render(request, "recepcion/detalle.html", {"equipo": equipo})
