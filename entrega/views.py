# entrega/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from login_app.decorators import login_required_simulado
from diagnostico.views import diagnosticos  # lista en memoria con los diagnósticos
import unicodedata

# Simulamos almacenamiento de entregas en memoria (objeto compartido)
entregas = []


# ---------- utilidades ----------
def _strip_accents(s: str) -> str:
    """Elimina tildes/diacríticos para comparar acento-insensible."""
    if s is None:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def _norm(s: str) -> str:
    """Normaliza cadenas: sin tildes, sin espacios dobles, casefold."""
    s = _strip_accents(s)
    s = " ".join(s.split())  # colapsa múltiples espacios
    return s.casefold()

def _buscar_diagnostico_por_nombre(nombre: str):
    n = _norm(nombre)
    for d in diagnosticos:
        if _norm(d.get("estudiante")) == n:
            return d
    return None

def _buscar_entrega_por_nombre(nombre: str):
    n = _norm(nombre)
    for e in entregas:
        if _norm(e.get("nombre")) == n:
            return e
    return None
# --------------------------------


@login_required_simulado
def listado_clientes(request):
    """
    /entrega/listado/ — Lista todos los clientes que tienen diagnóstico
    para iniciar el proceso de entrega.
    """
    vistos = set()
    clientes = []
    for d in diagnosticos:
        est = d.get("estudiante", "")
        key = _norm(est)
        if key and key not in vistos:
            vistos.add(key)
            clientes.append(est)
    clientes.sort()
    return render(request, "entrega/listado.html", {"clientes": clientes})


@login_required_simulado
def verificar_buscar(request):
    """
    /entrega/verificar/ — GET con formulario para buscar clientes y ver estado.
    """
    q = request.GET.get("q", "")
    qn = _norm(q)
    resultados = []

    if qn:
        vistos = set()
        for d in diagnosticos:
            est = d.get("estudiante", "")
            if qn in _norm(est):
                key = _norm(est)
                if key not in vistos:
                    vistos.add(key)
                    resultados.append(est)
        resultados.sort()
        if not resultados:
            messages.info(request, "No se encontraron clientes para esa búsqueda.")

    return render(request, "entrega/verificar.html", {
        "query": q,
        "resultados": resultados
    })


@login_required_simulado
def verificar(request, nombre):
    """
    /entrega/verificar/<nombre>/ — Ver estado actual del equipo diagnosticado del cliente.
    """
    equipo = _buscar_diagnostico_por_nombre(nombre)
    entrega = _buscar_entrega_por_nombre(nombre)

    if not equipo:
        messages.error(request, "No se encontró diagnóstico para ese cliente.")
        return redirect("entrega:listado")

    return render(request, "entrega/verificar.html", {
        "equipo": equipo,
        "entrega": entrega,
        "query": "",
        "resultados": [],
    })


@login_required_simulado
def reporte(request, nombre):
    """
    /entrega/reporte/<nombre>/ — GET muestra resumen del diagnóstico + formulario.
    POST registra estado final (entregado/pendiente + observaciones).
    """
    # Trae diagnóstico del cliente (para mostrar resumen en GET y validar en POST)
    equipo = _buscar_diagnostico_por_nombre(nombre)
    if not equipo:
        # Log para depurar si vuelve a fallar
        print("[DEBUG] reporte: diagnóstico NO encontrado para nombre URL =", repr(nombre))
        print("[DEBUG] candidatos:", [d.get("estudiante") for d in diagnosticos])
        messages.error(request, "No se encontró diagnóstico para ese cliente.")
        return redirect("entrega:listado")

    if request.method == "POST":
        estado = request.POST.get("estado")
        observaciones = request.POST.get("observaciones", "")

        if not estado:
            messages.error(request, "Debes seleccionar un estado de entrega.")
            return render(request, "entrega/reporte.html", {"nombre": nombre, "equipo": equipo})

        # ✅ Mutamos EN SITIO para mantener el mismo objeto 'entregas' compartido
        entregas[:] = [e for e in entregas if _norm(e.get("nombre")) != _norm(nombre)]

        now = timezone.localtime()
        entrega = {
            "nombre": nombre,  # guardamos el texto tal cual viene en la URL
            "estado": estado,
            "observaciones": observaciones,
            "created_ts": now.timestamp(),
            "created_at": now.strftime("%d/%m/%Y %H:%M"),
        }
        entregas.append(entrega)

        messages.success(request, f"Entrega registrada para {nombre}.")
        return redirect("entrega:comprobante", nombre=nombre)

    # GET → muestra formulario + resumen del diagnóstico
    return render(request, "entrega/reporte.html", {"nombre": nombre, "equipo": equipo})


@login_required_simulado
def comprobante(request, nombre):
    """
    /entrega/comprobante/<nombre>/ — Comprobante visual con diagnóstico + estado de entrega.
    """
    equipo = _buscar_diagnostico_por_nombre(nombre)
    entrega = _buscar_entrega_por_nombre(nombre)

    if not equipo or not entrega:
        # Debug útil si llegara a ocurrir nuevamente
        print("[DEBUG] comprobante faltante:",
              "equipo:", bool(equipo), "| entrega:", bool(entrega),
              "| nombre(url)=", repr(nombre))
        messages.error(request, "Falta información para generar el comprobante.")
        return redirect("entrega:listado")

    return render(request, "entrega/comprobante.html", {
        "equipo": equipo,
        "entrega": entrega,
    })
