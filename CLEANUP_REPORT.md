# Repo cleanup (safe, non-breaking)

Date: 2025-10-16

What I did:
- Archived old, unused files:
  - templates/base_old.html -> archive/templates/base_old.html
  - diagnostico/views_old.py -> archive/old_code/diagnostico/views_old.py
  - entrega/views_old.py -> archive/old_code/entrega/views_old.py
  - recepcion/views_old.py -> archive/old_code/recepcion/views_old.py
  - login_app/views_old.py -> archive/old_code/login_app/views_old.py
- Moved temporary helper scripts:
  - tmp_*.py -> scripts/tmp/
- Removed Python caches:
  - __pycache__/ at project root and in apps (diagnostico, entrega, recepcion, login_app)

Checks performed:
- Verified no references to base_old.html in templates.
- Verified no imports of tmp_* scripts in project.

How to restore any file:
- Move back from archive/ or scripts/ to original location keeping same name.

Next optional cleanups (not done yet):
- Group operational/one-off scripts (setup_*.py, preparar_*.py, verificar_*.py) under scripts/operations/ if you want a tidier root, they are not used by Django runtime.
- Consider excluding scripts/ from production deploys if not needed.

If anything seems off, ping me and I’ll revert quickly.