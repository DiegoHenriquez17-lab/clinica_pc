@echo off
REM Arranca el servidor Django usando directamente el python del venv (sin depender del PATH)
cd /d %~dp0\..
set VENV_PYTHON=%~dp0..\venv\Scripts\python.exe
if not exist "%VENV_PYTHON%" (
	echo No se encontró el interprete del venv en: %VENV_PYTHON%
	echo Crea/activa el entorno virtual primero: python -m venv venv
	exit /b 1
)
"%VENV_PYTHON%" manage.py runserver 0.0.0.0:8000
