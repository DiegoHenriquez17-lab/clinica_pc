# TODO: Add CRUD System for Diagnosticos

- [x] Add update view in diagnostico/views.py
- [x] Add delete view in diagnostico/views.py
- [x] Add URL routes for update and delete in diagnostico/urls.py
- [x] Create diagnostico/templates/diagnostico/edit.html template
- [x] Create diagnostico/templates/diagnostico/delete.html template
- [x] Update diagnostico/templates/diagnostico/listado.html to add edit/delete links and link to students list

# TODO: Make recepcion listado the same as diagnostico listado

- [x] Update recepcion/views.py listado view to fetch DiagnosticoModel objects
- [x] Update recepcion/templates/recepcion/listado.html to match diagnostico listado table structure

# TODO: Make recepcion listado_estudiantes the same as diagnostico student list

- [x] Update _get_estudiantes_list in diagnostico/views.py to return DB if any, else hardcoded
- [x] Update recepcion/views.py listado_estudiantes to use _get_estudiantes_list
- [x] Update recepcion/templates/recepcion/listado_estudiantes.html to display strings
