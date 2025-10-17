# recepcion/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError
from .models import Cliente, Equipo, Estudiante
from diagnostico.models import Diagnostico as DiagnosticoModel
from datetime import timedelta
import json

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


@login_required
def index(request):
    """Vista principal de recepción con formulario de registro"""
    if request.method == 'POST':
        return registrar_equipo(request)
    
    # Estadísticas para mostrar en la sidebar
    hoy = timezone.now().date()
    ingresos_hoy = Equipo.objects.filter(created_at__date=hoy).count()
    ultimos_ingresos = Equipo.objects.select_related('cliente').order_by('-created_at')[:5]
    
    context = {
        'ingresos_hoy': ingresos_hoy,
        'ultimos_ingresos': ultimos_ingresos,
    }
    
    return render(request, 'recepcion/index.html', context)


def registrar_equipo(request):
    """Procesa el formulario de registro de equipos"""
    try:
        # Datos del cliente
        nombre_cliente = request.POST.get('nombre_cliente', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        
        # Datos del equipo
        tipo_equipo = request.POST.get('tipo_equipo', '').strip()
        marca = request.POST.get('marca', '').strip()
        modelo = request.POST.get('modelo', '').strip()
        serial = request.POST.get('serial', '').strip()
        problema = request.POST.get('problema', '').strip()
        observaciones_adicionales = request.POST.get('observaciones_adicionales', '').strip()
        
        # Accesorios (checkbox múltiple)
        accesorios = request.POST.getlist('accesorios')
        
        if not nombre_cliente or not telefono or not tipo_equipo or not problema:
            messages.error(request, 'Por favor complete todos los campos obligatorios.')
            return redirect('recepcion:index')
        
        # Crear o obtener cliente
        cliente, created = Cliente.objects.get_or_create(
            nombre=nombre_cliente,
            defaults={
                'telefono': telefono,
                'correo': correo or None,
            }
        )
        
        # Si el cliente ya existe pero tiene datos diferentes, actualizar
        if not created:
            if telefono and cliente.telefono != telefono:
                cliente.telefono = telefono
            if correo and cliente.correo != correo:
                cliente.correo = correo
            cliente.save()
        
        # Crear equipo
        equipo = Equipo.objects.create(
            cliente=cliente,
            tipo_equipo=tipo_equipo,
            marca=marca or None,
            modelo=modelo or None,
            serial=serial or None,
            problema=problema,
            accesorios=accesorios,
            observaciones_adicionales=observaciones_adicionales or None,
            estado='recepcion'
        )
        
        messages.success(request, f'Equipo registrado exitosamente. ID: #{equipo.id}')
        return redirect('recepcion:index')
        
    except Exception as e:
        messages.error(request, f'Error al registrar el equipo: {str(e)}')
        return redirect('recepcion:index')


def _get_estudiantes_list_local():
    """Obtener lista de estudiantes: preferir DB, sino fallback a la lista fija.

    Evitamos importar desde `diagnostico.views` para romper el ciclo de importación
    y garantizar que la vista `recepcion` pueda funcionar independientemente.
    """
    try:
        lista = list(Estudiante.objects.values_list('nombre', flat=True))
        if lista:
            return lista
    except Exception:
        pass
    return estudiantes


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
        diags = DiagnosticoModel.objects.select_related('cliente', 'estudiante', 'equipo').all()
        return render(request, "recepcion/listado.html", {"diagnosticos": diags})
    except Exception:
        return render(request, "recepcion/listado.html", {"diagnosticos": getattr(diag_views, 'diagnosticos', [])})


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


@login_required_simulado
def editar_equipo(request, pk):
    """Editar un equipo existente."""
    try:
        equipo = Equipo.objects.select_related('cliente').get(pk=pk)
    except Equipo.DoesNotExist:
        messages.error(request, "Equipo no encontrado.")
        return redirect("recepcion:listado")

    if request.method == "POST":
        tipo_equipo = request.POST.get("tipo_equipo")
        problema = request.POST.get("problema")
        serial = request.POST.get("serial")

        if not tipo_equipo or not problema:
            messages.error(request, "Completa todos los campos.")
            return redirect("recepcion:editar_equipo", pk=pk)

        equipo.tipo_equipo = tipo_equipo
        equipo.problema = problema
        equipo.serial = serial
        equipo.save()

        messages.success(request, "Equipo actualizado con éxito.")
        return redirect("recepcion:listado")

    return render(request, "recepcion/edit_equipo.html", {"equipo": equipo, "tipos_equipos": tipos_equipos})


@login_required_simulado
def eliminar_equipo(request, pk):
    """Eliminar un equipo."""
    try:
        equipo = Equipo.objects.get(pk=pk)
    except Equipo.DoesNotExist:
        messages.error(request, "Equipo no encontrado.")
        return redirect("recepcion:listado")

    if request.method == "POST":
        equipo.delete()
        messages.success(request, "Equipo eliminado con éxito.")
        return redirect("recepcion:listado")

    return render(request, "recepcion/delete_equipo.html", {"equipo": equipo})


# CRUD para Clientes

@login_required_simulado
def listado_clientes(request):
    """Listado de clientes."""
    try:
        clientes = Cliente.objects.all()
        return render(request, "recepcion/listado_clientes.html", {"clientes": clientes})
    except Exception:
        return render(request, "recepcion/listado_clientes.html", {"clientes": []})


@login_required_simulado
def crear_cliente(request):
    """Crear un nuevo cliente."""
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        rut = request.POST.get("rut")
        correo = request.POST.get("correo")
        telefono = request.POST.get("telefono")

        if not nombre:
            messages.error(request, "El nombre es obligatorio.")
            return redirect("recepcion:crear_cliente")

        try:
            Cliente.objects.create(nombre=nombre, rut=rut, correo=correo, telefono=telefono)
            messages.success(request, "Cliente creado con éxito.")
            return redirect("recepcion:listado_clientes")
        except IntegrityError:
            messages.error(request, "Error al crear el cliente.")
            return redirect("recepcion:crear_cliente")

    return render(request, "recepcion/crear_cliente.html")


@login_required_simulado
def editar_cliente(request, pk):
    """Editar un cliente existente."""
    try:
        cliente = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        messages.error(request, "Cliente no encontrado.")
        return redirect("recepcion:listado_clientes")

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        rut = request.POST.get("rut")
        correo = request.POST.get("correo")
        telefono = request.POST.get("telefono")

        if not nombre:
            messages.error(request, "El nombre es obligatorio.")
            return redirect("recepcion:editar_cliente", pk=pk)

        cliente.nombre = nombre
        cliente.rut = rut
        cliente.correo = correo
        cliente.telefono = telefono
        cliente.save()

        messages.success(request, "Cliente actualizado con éxito.")
        return redirect("recepcion:listado_clientes")

    return render(request, "recepcion/editar_cliente.html", {"cliente": cliente})


@login_required_simulado
def eliminar_cliente(request, pk):
    """Eliminar un cliente."""
    try:
        cliente = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        messages.error(request, "Cliente no encontrado.")
        return redirect("recepcion:listado_clientes")

    if request.method == "POST":
        cliente.delete()
        messages.success(request, "Cliente eliminado con éxito.")
        return redirect("recepcion:listado_clientes")

    return render(request, "recepcion/eliminar_cliente.html", {"cliente": cliente})


# CRUD para Estudiantes

@login_required_simulado
def listado_estudiantes(request):
    """Listado de estudiantes."""
    estudiantes_list = _get_estudiantes_list_local()
    return render(request, "recepcion/listado_estudiantes.html", {"estudiantes": estudiantes_list})


@login_required_simulado
def crear_estudiante(request):
    """Crear un nuevo estudiante."""
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")

        if not nombre:
            messages.error(request, "El nombre es obligatorio.")
            return redirect("recepcion:crear_estudiante")

        try:
            Estudiante.objects.create(nombre=nombre, email=email)
            messages.success(request, "Estudiante creado con éxito.")
            return redirect("recepcion:listado_estudiantes")
        except IntegrityError:
            messages.error(request, "Error al crear el estudiante.")
            return redirect("recepcion:crear_estudiante")

    return render(request, "recepcion/crear_estudiante.html")


@login_required_simulado
def editar_estudiante(request, pk):
    """Editar un estudiante existente."""
    try:
        estudiante = Estudiante.objects.get(pk=pk)
    except Estudiante.DoesNotExist:
        messages.error(request, "Estudiante no encontrado.")
        return redirect("recepcion:listado_estudiantes")

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")

        if not nombre:
            messages.error(request, "El nombre es obligatorio.")
            return redirect("recepcion:editar_estudiante", pk=pk)

        estudiante.nombre = nombre
        estudiante.email = email
        estudiante.save()

        messages.success(request, "Estudiante actualizado con éxito.")
        return redirect("recepcion:listado_estudiantes")

    return render(request, "recepcion/editar_estudiante.html", {"estudiante": estudiante})


@login_required_simulado
def eliminar_estudiante(request, pk):
    """Eliminar un estudiante."""
    try:
        estudiante = Estudiante.objects.get(pk=pk)
    except Estudiante.DoesNotExist:
        messages.error(request, "Estudiante no encontrado.")
        return redirect("recepcion:listado_estudiantes")

    if request.method == "POST":
        estudiante.delete()
        messages.success(request, "Estudiante eliminado con éxito.")
        return redirect("recepcion:listado_estudiantes")

    return render(request, "recepcion/eliminar_estudiante.html", {"estudiante": estudiante})
