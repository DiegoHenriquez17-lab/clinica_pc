# recepcion/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from login_app.decorators import session_required   # 👈 usamos sesión manual

# Lista global de equipos registrados
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

@session_required
def registrar_equipo(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        tipo_equipo = request.POST.get("tipo_equipo")
        problema = request.POST.get("problema")

        equipos_registrados.append({
            "nombre": nombre,
            "tipo_equipo": tipo_equipo,
            "problema": problema
        })

        messages.success(request, f"Equipo de {nombre} registrado con éxito.")
        return redirect("recepcion:listado")

    return render(request, "recepcion/registrar.html", {
        "estudiantes": estudiantes,
        "tipos_equipos": tipos_equipos   # 👈 ahora enviamos la lista
    })


@session_required
def listado_equipos(request):
    return render(request, "recepcion/listado.html", {"equipos": equipos_registrados})


@session_required
def detalle_equipo(request, nombre):
    equipo = next((eq for eq in equipos_registrados if eq["nombre"] == nombre), None)
    return render(request, "recepcion/detalle.html", {"equipo": equipo})
