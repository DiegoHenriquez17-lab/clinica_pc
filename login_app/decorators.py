# login_app/decorators.py
from django.shortcuts import redirect
from functools import wraps

def login_required_simulado(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print("[DEBUG] login_required_simulado:", request.path,
              "| autenticado =", bool(request.session.get("autenticado")))
        if not request.session.get("autenticado"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper
