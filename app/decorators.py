# decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not session.get('logged_in'):
                flash('Debe iniciar sesión para acceder', 'warning')
                return redirect(url_for('auth.login'))
            
            if role and session.get('user_role') != role:
                flash('No tiene permisos suficientes', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return wrapper
    return decorator