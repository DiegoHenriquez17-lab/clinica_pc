# recepcion/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from login_app.decorators import login_required_simulado
from .models import Cliente, Equipo, Estudiante
from django.db import IntegrityError

# Lista global en memoria (sin BD) - se mantiene solo como fallback
try:
    from . import views as _views_module
    equipos_registrados = getattr(_views_module, 'equipos_registrados', [])
except Exception:
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


def _prefix_for_tipo(tipo: str) -> str:
    """Mapea el tipo de equipo a un prefijo corto para el serial."""
    if not tipo:
        return "EQ"
    t = tipo.lower()
    if "notebook" in t:
        return "NB"
    if "pc" in t or "escritorio" in t:
        return "PC"
    if "tablet" in t:
        return "TB"
    if "impresora" in t:
        return "PR"
    if "celular" in t or "móvil" in t or "movil" in t:
        return "CL"
    if "servidor" in t:
        return "SV"
    return "EQ"


def _generate_next_serial(tipo_equipo: str) -> str:
    """Genera un serial secuencial por tipo, p. ej. PC-0001.

    Garantiza unicidad contra `equipos_registrados` incrementando el contador si el serial ya existe.
    """
    prefix = _prefix_for_tipo(tipo_equipo)
    # contar existentes del mismo tipo para iniciar el número
    # contar existentes en BD preferentemente
    try:
        existing_count = Equipo.objects.filter(tipo_equipo=tipo_equipo).count()
    except Exception:
        existing = [e for e in equipos_registrados if e.get("tipo_equipo") == tipo_equipo]
        existing_count = len(existing)
    seq = existing_count + 1
    # generar y asegurar unicidad
    while True:
        candidate = f"{prefix}-{seq:04d}"
        if not any(e for e in equipos_registrados if (e.get("serial") or "") == candidate):
            return candidate
        seq += 1

@login_required_simulado
def registrar(request):
    """
    Vista única para GET (mostrar formulario) y POST (registrar equipo).
    """
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        tipo_equipo = request.POST.get("tipo_equipo")
        problema = request.POST.get("problema")
        confirm = request.POST.get("confirm_duplicate")
        rut = request.POST.get("rut")
        correo = request.POST.get("correo")
        telefono = request.POST.get("telefono")
        serial = request.POST.get("serial")
        # Si no se proporciona serial, generamos uno automático por tipo
        if not serial:
            serial = _generate_next_serial(tipo_equipo)

        # Validaciones simples (opcional)
        if not nombre or not tipo_equipo or not problema:
            messages.error(request, "Completa todos los campos.")
            return render(request, "recepcion/registrar.html", {
                "estudiantes": estudiantes,
                "tipos_equipos": tipos_equipos,
                "nombre": nombre,
                "tipo_equipo": tipo_equipo,
                "problema": problema,
                "rut": rut,
                "correo": correo,
                "telefono": telefono,
                "serial": serial,
            })
        # ¿Ya existe un cliente con ese nombre?
        existe = False
        try:
            existe = Cliente.objects.filter(nombre=nombre).exists()
        except Exception:
            existe = any(eq for eq in equipos_registrados if eq.get("nombre") == nombre)
        if existe and not confirm:
            # Pedimos confirmación al usuario antes de agregar duplicado
            messages.warning(request, f"Ya existe un registro para {nombre}. ¿Deseas agregar otro registro para revisión distinta?")
            return render(request, "recepcion/registrar.html", {
                "estudiantes": estudiantes,
                "tipos_equipos": tipos_equipos,
                "nombre": nombre,
                "tipo_equipo": tipo_equipo,
                "problema": problema,
                "rut": rut,
                "correo": correo,
                "telefono": telefono,
                "serial": serial,
                "confirm_duplicate": True,
            })

        # Guardar en DB si está disponible
        try:
            cliente, created = Cliente.objects.get_or_create(nombre=nombre, defaults={"rut": rut, "correo": correo, "telefono": telefono})
            equipo = Equipo.objects.create(cliente=cliente, tipo_equipo=tipo_equipo, problema=problema, serial=serial)
            messages.success(request, f"Equipo de {nombre} registrado con éxito.")
            return redirect("recepcion:listado")
        except IntegrityError:
            messages.error(request, "Error al guardar en la base de datos (integrity).")
            return redirect("recepcion:registrar")
        except Exception:
            # Fallback: guardar en lista en memoria
            equipos_registrados.append({
                "nombre": nombre,
                "tipo_equipo": tipo_equipo,
                "problema": problema,
                "rut": rut,
                "correo": correo,
                "telefono": telefono,
                "serial": serial,
            })
            messages.success(request, f"Equipo de {nombre} registrado con éxito (almacenado en memoria).")
            return redirect("recepcion:listado")

    # GET
    return render(request, "recepcion/registrar.html", {
        "estudiantes": estudiantes,
        "tipos_equipos": tipos_equipos
    })


@login_required_simulado
def listado(request):
    # Preferir datos en DB
    try:
        equipos = Equipo.objects.select_related('cliente').all()
        return render(request, "recepcion/listado.html", {"equipos": equipos})
    except Exception:
        return render(request, "recepcion/listado.html", {"equipos": equipos_registrados})


@login_required_simulado
def detalle(request, nombre):
    try:
        cliente = Cliente.objects.filter(nombre=nombre).first()
        if not cliente:
            raise Exception("no cliente")
        equipo = cliente.equipos.first()
        if not equipo:
            messages.error(request, "No se encontró el equipo solicitado.")
            return redirect("recepcion:listado")
        return render(request, "recepcion/detalle.html", {"equipo": equipo})
    except Exception:
        equipo = next((eq for eq in equipos_registrados if eq["nombre"] == nombre), None)
        if not equipo:
            messages.error(request, "No se encontró el equipo solicitado.")
            return redirect("recepcion:listado")
        return render(request, "recepcion/detalle.html", {"equipo": equipo})
