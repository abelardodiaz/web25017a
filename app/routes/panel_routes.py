# app/routes/panel_routes.py
from flask import Blueprint, render_template, redirect, flash, url_for, session, current_app, get_flashed_messages
from sqlalchemy.exc import IntegrityError
from app.decorators import login_required
from app.forms import UserForm, EmptyForm  # Importa EmptyForm
from app.models import User, UserRole, db

panel_bp = Blueprint('panel', __name__)

@panel_bp.route('/panel')
@login_required(role='admin')
def dashboard():
    form = UserForm()
    delete_form = EmptyForm()  # Formulario para eliminación
    reset_form = EmptyForm()   # Formulario para reset
    users = User.query.all()
    return render_template('panel/dashboard.html', users=users, form=form, delete_form=delete_form, reset_form=reset_form)

@panel_bp.route('/add-user', methods=['POST'])
@login_required(role='admin')
def add_user():
    form = UserForm()
    if form.validate_on_submit():  # Valida el formulario y el CSRF
        try:
            new_user = User(
                username=form.username.data,
                role=UserRole(form.role.data),
                email=form.email.data or None
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Usuario creado exitosamente', 'success')
        except IntegrityError:
            flash('El usuario ya existe', 'danger')
    return redirect(url_for('panel.dashboard'))

@panel_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required(role='admin')
def delete_user(user_id):
    form = EmptyForm()
    if form.validate_on_submit():  # Valida el token CSRF
        user = User.query.get_or_404(user_id)
        if user.master:
            flash('No se puede eliminar al usuario master', 'error')
        else:
            try:
                db.session.delete(user)
                db.session.commit()
                flash('Usuario eliminado exitosamente', 'success')
            except Exception as e:
                flash(f'Error al eliminar usuario: {str(e)}', 'danger')
    else:
        flash('Error de validación CSRF', 'danger')
    return redirect(url_for('panel.dashboard'))

@panel_bp.route('/reset-db', methods=['GET','POST'])  # Cambia a solo POST
# @login_required(role='admin')
def reset_db():
    form = EmptyForm()
    if form.validate_on_submit():  # Valida el token CSRF
        try:
            db.drop_all()
            db.create_all()
            session.clear()
            current_app.config['DB_RESETEADA'] = True
            flash({
                'message': 'ELIMINANDO TODO EL CONTENIDO DE LA BASE DE DATOS ...',
                'type': 'redirect',
                'url': url_for('setup.setup'),
                'delay': 6
            }, 'modal_data')
            return redirect(url_for('panel.redirect_handler'))
        except Exception as e:
            flash(f'Error al reiniciar la BD: {str(e)}', 'danger')
    else:
        flash('Error de validación CSRF', 'danger')
    return redirect(url_for('panel.dashboard'))

@panel_bp.route('/redirect-handler')
def redirect_handler():
    messages = get_flashed_messages(category_filter=["modal_data"])
    if not messages:
        return redirect(url_for('main.index'))
    return render_template('modals/redirect.html', modal_data=messages[0])