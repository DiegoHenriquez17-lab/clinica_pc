# entrega/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from login_app.decorators import login_required_simulado
from diagnostico.models import Diagnostico as DiagnosticoModel
from .models import Entrega as EntregaModel
from recepcion.models import Cliente, Equipo
import unicodedata

# Fallback: usar listas en memoria si la DB no está poblada
try:
    from diagnostico import views as diag_views
    diagnosticos = getattr(diag_views, 'diagnosticos', [])
except Exception:
    diagnosticos = []

# Simulamos almacenamiento de entregas en memoria (objeto compartido)
try:
    from . import views as _mod
    entregas = getattr(_mod, 'entregas', [])
except Exception:
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
    # Intentar buscar en la DB primero
    try:
        # buscar por cliente nombre exacto (case insensitive)
        diag = DiagnosticoModel.objects.filter(cliente__nombre__iexact=nombre).select_related('cliente', 'estudiante', 'equipo').first()
        if diag:
            return diag
        # búsqueda laxa: icontains
        diag = DiagnosticoModel.objects.filter(cliente__nombre__icontains=nombre).select_related('cliente', 'estudiante', 'equipo').first()
        if diag:
            return diag
    except Exception:
        pass

    # Si no hay DB o no encontramos, usar la lista en memoria
    for d in diagnosticos:
        candidato = d.get("cliente") if d.get("cliente") is not None else d.get("estudiante")
        if _norm(candidato) == n:
            return d

    for d in diagnosticos:
        candidato = d.get("cliente") if d.get("cliente") is not None else d.get("estudiante")
        cn = _norm(candidato)
        if n in cn or cn in n:
            return d
    return None

def _buscar_entrega_por_nombre(nombre: str):
    n = _norm(nombre)
    # Preferir DB
    try:
        diag = DiagnosticoModel.objects.filter(cliente__nombre__iexact=nombre).first()
        if diag and hasattr(diag, 'entrega'):
            return diag.entrega
        diag = DiagnosticoModel.objects.filter(cliente__nombre__icontains=nombre).first()
        if diag and hasattr(diag, 'entrega'):
            return diag.entrega
    except Exception:
        pass

    # fallback en memoria
    for e in entregas:
        if _norm(e.get("nombre")) == n:
            return e

    for e in entregas:
        en = _norm(e.get("nombre"))
        if n in en or en in n:
            return e
    return None


def _infer_cliente_from_equipo(equipo_str: str) -> str:
    """Intenta extraer el nombre del propietario a partir de la descripción de equipo.

    La descripción se genera en diagnostico como "Tipo — Nombre".
    """
    if not equipo_str:
        return ""
    parts = equipo_str.split("—")
    if len(parts) >= 2:
        # asumimos que la parte derecha es el nombre
        return parts[-1].strip()
    return equipo_str.strip()
# --------------------------------


@login_required_simulado
def listado_clientes(request):
    """
    /entrega/listado/ — Lista todos los clientes que tienen diagnóstico
    para iniciar el proceso de entrega.
    """
    # Preferir datos en DB si existen
    try:
        clientes_qs = Cliente.objects.all().order_by('nombre')
        clientes = [c.nombre for c in clientes_qs]
        # entregas en DB
        entregas_qs = EntregaModel.objects.select_related('diagnostico__cliente').all()
        entregas_map = { e.diagnostico.cliente.nombre.lower(): e for e in entregas_qs }
        delivered_map = { c: (c.lower() in entregas_map) for c in clientes }
        delivered_list = [c for c, v in delivered_map.items() if v]
        return render(request, "entrega/listado.html", {"clientes": clientes, "delivered_map": delivered_map, "delivered_list": delivered_list})
    except Exception:
        vistos = set()
        clientes = []
        for d in diagnosticos:
            if d.get("cliente"):
                est = d.get("cliente")
            else:
                est = _infer_cliente_from_equipo(d.get("equipo", "")) or d.get("estudiante", "")
            key = _norm(est)
            if key and key not in vistos:
                vistos.add(key)
                clientes.append(est)
        clientes.sort()
        entregas_map = { _norm(e.get("nombre")): e for e in entregas }
        delivered_map = {}
        for c in clientes:
            delivered_map[c] = (_norm(c) in entregas_map)
        delivered_list = [c for c, v in delivered_map.items() if v]
        return render(request, "entrega/listado.html", {"clientes": clientes, "delivered_map": delivered_map, "delivered_list": delivered_list})


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
            if d.get("cliente"):
                est = d.get("cliente")
            else:
                est = _infer_cliente_from_equipo(d.get("equipo", "")) or d.get("estudiante", "")
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
        # Intento de fallback: búsqueda laxa recorriendo diagnósticos (por cliente/estudiante/equipo)
        n = _norm(nombre)
        encontrado = None
        for d in diagnosticos:
            cand_cliente = _norm(d.get("cliente") or "")
            cand_est = _norm(d.get("estudiante") or "")
            cand_eq = _norm(d.get("equipo") or "")
            if n in cand_cliente or cand_cliente in n or n in cand_est or cand_est in n or n in cand_eq or cand_eq in n:
                encontrado = d
                break

        if encontrado:
            equipo = encontrado
        else:
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
        print("[DEBUG] diagnosticos (cliente, estudiante):", [(d.get("cliente"), d.get("estudiante")) for d in diagnosticos])
        messages.error(request, "No se encontró diagnóstico para ese cliente.")
        return redirect("entrega:listado")

    if request.method == "POST":
        estado = request.POST.get("estado")
        observaciones = request.POST.get("observaciones", "")

        if not estado:
            messages.error(request, "Debes seleccionar un estado de entrega.")
            return render(request, "entrega/reporte.html", {"nombre": nombre, "equipo": equipo})

        # intentar persistir en la DB
        try:
            # buscar diagnóstico
            diag = None
            if isinstance(equipo, DiagnosticoModel):
                diag = equipo
            else:
                # si es dict (memoria), buscar por cliente
                diag = DiagnosticoModel.objects.filter(cliente__nombre__iexact=nombre).first()

            if diag:
                # eliminar entrega previa si existiera
                EntregaModel.objects.filter(diagnostico=diag).delete()
                EntregaModel.objects.create(diagnostico=diag, recibido_por=nombre, observaciones=observaciones or "")
                messages.success(request, f"Entrega registrada para {nombre}.")
                return redirect("entrega:comprobante", nombre=nombre)

        except Exception:
            # fallback en memoria
            entregas[:] = [e for e in entregas if _norm(e.get("nombre")) != _norm(nombre)]
            now = timezone.localtime()
            entrega = {
                "nombre": nombre,
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
