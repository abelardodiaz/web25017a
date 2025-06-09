# app/routes/panel_routes.py
from flask import Blueprint, render_template, redirect, flash, url_for, session, current_app, get_flashed_messages, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from functools import wraps
from app.forms import UserForm, SyscomCredentialForm, EmptyForm
from app.models import User, UserRole, SyscomCredential, db
from app.utils.token_obtener_api import request_token
from flask_login import login_required, current_user
from flask import flash, redirect


panel_bp = Blueprint('panel', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acceso denegado: administrador requerido', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@panel_bp.route('/panel')
@admin_required
def dashboard():
    form = UserForm()
    delete_form = EmptyForm()
    reset_form = EmptyForm()
    users = User.query.all()
    return render_template('panel/dashboard.html', 
                         users=users, 
                         form=form, 
                         delete_form=delete_form, 
                         reset_form=reset_form)

@panel_bp.route('/add-user', methods=['POST'])
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
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
            db.session.rollback()
            flash('El usuario ya existe', 'danger')
    return redirect(url_for('panel.dashboard'))

@panel_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_required
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

@panel_bp.route('/reset-db', methods=['POST'])  # Cambia a solo POST
@admin_required
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

@panel_bp.route('/get-token', methods=['POST'])
@admin_required
def get_token():
    cred = SyscomCredential.query.order_by(SyscomCredential.created_at.desc()).first()
    
    if not cred or not cred.client_id or not cred.client_secret:
        flash('Primero debe configurar las credenciales de Syscom', 'warning')
        return redirect(url_for('panel.list_credentials'))
    
    current_app.logger.debug(f">>> GET-TOKEN: Cred id={cred.id}, client_id={cred.client_id[:6]}…, client_secret(len)={len(cred.client_secret)}")
    success = request_token(cred)
    
    if success:
        flash('Token obtenido exitosamente', 'success')
    else:
        flash('Error al obtener token. Ver logs para detalles.', 'danger')
    
    return redirect(url_for('panel.list_credentials'))


# --- Listado ---
@panel_bp.route('/credentials')
@admin_required
def list_credentials():
    creds = SyscomCredential.query.all()
    form = EmptyForm()  # Crea una instancia del formulario
    return render_template('panel_credenciales_lista.html', creds=creds, form=form)

# --- Alta ---
@panel_bp.route('/credentials/new', methods=['GET', 'POST'])
@admin_required
def new_credential():
    form = SyscomCredentialForm()
    if form.validate_on_submit():
        cred = SyscomCredential(
            client_id=form.client_id.data.strip(),
            client_secret=form.client_secret.data.strip(),
        )
        db.session.add(cred)
        db.session.commit()
        flash('Credencial guardada. Pulsa “Renovar” para obtener token.', 'success')
        return redirect(url_for('panel.list_credentials'))
    return render_template('panel_credenciales_form.html', form=form)

# --- Renovación manual ---
@panel_bp.route('/credentials/<int:cred_id>/renew', methods=['POST'])
@admin_required
def renew_credential(cred_id):
    cred = SyscomCredential.query.get_or_404(cred_id)
    current_app.logger.info(f"Renovando token para credencial ID: {cred_id}")
    
    try:
        if request_token(cred):
            flash('Token renovado correctamente', 'success')
            current_app.logger.info(f"Token renovado para credencial ID: {cred_id}")
        else:
            flash('Error al renovar token. Ver logs para detalles.', 'danger')
            current_app.logger.exception("Error crítico renovando token")

    except Exception as e:

        current_app.logger.error(f"Error crítico renovando token: {str(e)}", exc_info=True)
        flash(f'Error al renovar: {e}', 'danger')
    
    return redirect(url_for('panel.list_credentials'))

# --- Borrado ---
@panel_bp.route('/credentials/<int:cred_id>/delete', methods=['POST'])
@admin_required
def delete_credential(cred_id):
    cred = SyscomCredential.query.get_or_404(cred_id)
    db.session.delete(cred)
    db.session.commit()
    flash('Credencial eliminada', 'success')
    return redirect(url_for('panel.list_credentials'))