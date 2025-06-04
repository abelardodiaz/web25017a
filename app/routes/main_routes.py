# app/routes/main.routes.py
from flask import Blueprint, render_template
from app.decorators import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ruta principal de la aplicación"""
    return render_template('index.html')

