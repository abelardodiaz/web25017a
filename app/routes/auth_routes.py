# app/routes/auth_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.forms import LoginForm
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            session.permanent = form.remember.data
            session['logged_in'] = True
            session['user_id'] = user.id
            session['user_role'] = user.role.value
            flash('¡Sesión iniciada correctamente!', 'success')
            return redirect(url_for('panel.dashboard'))
        
        flash('Credenciales inválidas', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('main.index'))