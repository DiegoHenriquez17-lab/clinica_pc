@echo off
REM Pobla grupos, permisos y usuarios (usa el venv del proyecto)
cd /d %~dp0\..
call python manage.py seed_users
