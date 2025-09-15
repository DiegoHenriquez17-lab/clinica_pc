from django.shortcuts import render, redirect
from django.contrib import messages
from login_app.decorators import session_required
from diagnostico.views import diagnosticos   # 👈 clientes ya diagnosticados

# Simulamos almacenamiento de entregas
entregas = []


@session_required
def listado_clientes(request):
    """
    Muestra todos los clientes que tienen diagnóstico para iniciar el proceso de entrega.
    """
    clientes = [d["estudiante"] for d in diagnosticos]

    return render(request, "entrega/listado.html", {
        "clientes": clientes
    })


@session_required
def verificar(request, nombre):
    """
    Ver estado actual del equipo diagnosticado del cliente.
    """
    equipo = next((d for d in diagnosticos if d["estudiante"] == nombre), None)
    entrega = next((e for e in entregas if e["nombre"] == nombre), None)

    if not equipo:
        messages.error(request, "No se encontró diagnóstico para ese cliente.")
        return redirect("entrega:listado")

    return render(request, "entrega/verificar.html", {
        "equipo": equipo,
        "entrega": entrega,
    })


@session_required
def reporte(request, nombre):
    """
    Registrar estado final del equipo (entregado/pendiente + observaciones).
    """
    if request.method == "POST":
        estado = request.POST["estado"]
        observaciones = request.POST["observaciones"]

        entrega = {
            "nombre": nombre,
            "estado": estado,
            "observaciones": observaciones,
        }
        entregas.append(entrega)

        messages.success(request, f"Entrega registrada para {nombre}.")
        return redirect("entrega:comprobante", nombre=nombre)

    return render(request, "entrega/reporte.html", {
        "nombre": nombre
    })


@session_required
def comprobante(request, nombre):
    """
    Mostrar comprobante con diagnóstico y estado de entrega.
    """
    equipo = next((d for d in diagnosticos if d["estudiante"] == nombre), None)
    entrega = next((e for e in entregas if e["nombre"] == nombre), None)

    return render(request, "entrega/comprobante.html", {
        "equipo": equipo,
        "entrega": entrega,
    })
