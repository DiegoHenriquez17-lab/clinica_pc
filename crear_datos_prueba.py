from recepcion.models import Cliente, Equipo
from diagnostico.models import Diagnostico
from django.contrib.auth.models import User

# Crear algunos clientes de prueba
clientes_data = [
    {'nombre': 'Juan Pérez', 'telefono': '+56912345678', 'correo': 'juan@email.com'},
    {'nombre': 'María González', 'telefono': '+56987654321', 'correo': 'maria@email.com'},
    {'nombre': 'Carlos Rodríguez', 'telefono': '+56955555555', 'correo': None},
    {'nombre': 'Ana Torres', 'telefono': '+56944444444', 'correo': 'ana@email.com'},
]

for cliente_data in clientes_data:
    cliente, created = Cliente.objects.get_or_create(
        nombre=cliente_data['nombre'],
        defaults=cliente_data
    )
    if created:
        print(f"Cliente {cliente.nombre} creado.")

# Crear algunos equipos de prueba
equipos_data = [
    {
        'cliente_nombre': 'Juan Pérez',
        'tipo_equipo': 'Laptop',
        'marca': 'HP',
        'modelo': 'Pavilion 15',
        'serial': 'HP123456789',
        'problema': 'No enciende, posible problema con la fuente de poder',
        'accesorios': ['Cargador', 'Mouse'],
        'estado': 'recepcion'
    },
    {
        'cliente_nombre': 'María González',
        'tipo_equipo': 'PC Escritorio',
        'marca': 'Dell',
        'modelo': 'OptiPlex 3070',
        'serial': 'DELL987654321',
        'problema': 'Pantalla azul constante, Windows no inicia correctamente',
        'accesorios': ['Teclado', 'Mouse'],
        'estado': 'recepcion'
    },
    {
        'cliente_nombre': 'Carlos Rodríguez',
        'tipo_equipo': 'Laptop',
        'marca': 'Lenovo',
        'modelo': 'ThinkPad E14',
        'serial': 'LEN555777999',
        'problema': 'Muy lento, posible virus o malware',
        'accesorios': ['Cargador', 'Bolso'],
        'estado': 'recepcion'
    },
    {
        'cliente_nombre': 'Ana Torres',
        'tipo_equipo': 'All-in-One',
        'marca': 'ASUS',
        'modelo': 'V241',
        'serial': 'ASUS111222333',
        'problema': 'No reconoce dispositivos USB, puertos no funcionan',
        'accesorios': ['Teclado', 'Mouse'],
        'estado': 'diagnostico'
    }
]

for equipo_data in equipos_data:
    try:
        cliente = Cliente.objects.get(nombre=equipo_data['cliente_nombre'])
        equipo, created = Equipo.objects.get_or_create(
            cliente=cliente,
            serial=equipo_data['serial'],
            defaults={
                'tipo_equipo': equipo_data['tipo_equipo'],
                'marca': equipo_data['marca'],
                'modelo': equipo_data['modelo'],
                'problema': equipo_data['problema'],
                'accesorios': equipo_data['accesorios'],
                'estado': equipo_data['estado']
            }
        )
        if created:
            print(f"Equipo {equipo.tipo_equipo} de {cliente.nombre} creado.")
    except Cliente.DoesNotExist:
        print(f"Cliente {equipo_data['cliente_nombre']} no encontrado.")

print("\nDatos de prueba creados exitosamente!")
print("Puedes probar el sistema con estos equipos registrados.")