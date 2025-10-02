"# Evaluacion1CLinica"
"# Evaluacion_clinica_pc"

## Restaurar datos locales (estudiantes/clientes)

Este proyecto incluye listas en memoria con clientes, equipos y estudiantes.
Después de clonar en un equipo nuevo, puedes poblar la base de datos SQLite local
con los estudiantes y clientes fijados ejecutando el siguiente comando:

```bash
python manage.py import_inmemory
```

El comando crea (get_or_create) los registros necesarios sin eliminar los ya existentes.
