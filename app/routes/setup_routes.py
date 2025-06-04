# app/routes/setup_routes.py
from flask import Blueprint, render_template, redirect, url_for, current_app, get_flashed_messages
from sqlalchemy.exc import IntegrityError, DataError
from app import db
from app.models import User, UserRole
from app.forms import SetupForm

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    # Limpiar mensajes de reset previos
    get_flashed_messages(category_filter=["modal_data"])

    if not current_app.config.get('DB_RESETEADA', True):
        return redirect(url_for('main.index'))
    
    form = SetupForm()
    
    if form.validate_on_submit():
        try:
            # Verificar y crear tablas con confirmación
            current_app.logger.info("🔨 Verificando estructura de la base de datos...")
            db.create_all()
            current_app.logger.info("✅ Estructura de BD verificada")
            
            # Validación adicional de nombre de usuario
            if User.query.filter_by(username=form.username.data).first():
                raise IntegrityError("Usuario duplicado", params=None, orig=None)
            
            # Crear usuario con hash seguro
            admin_user = User(
                username=form.username.data,
                email=form.email.data if form.email.data else None,
                first_name=form.first_name.data if form.first_name.data else None,
                last_name=form.last_name.data if form.last_name.data else None,
                whatsapp=form.whatsapp.data if form.whatsapp.data else None,
                telegram=form.telegram.data if form.telegram.data else None,
                master=True,
                role=UserRole.ADMIN
            )
            admin_user.set_password(form.password.data)  # This might raise an exception if password is too long
            
            db.session.add(admin_user)
            db.session.commit()  # Commit must succeed before changing DB_RESETEADA
            
            # Only set DB_RESETEADA to False if commit succeeds
            current_app.config['DB_RESETEADA'] = False
            current_app.logger.info("🎉 Usuario administrador creado exitosamente")
            return redirect(url_for('main.index'))
            
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"🚨 Error de integridad: {str(e)}")
            form.username.errors.append('El nombre de usuario ya existe')
        except DataError as e:
            db.session.rollback()
            current_app.logger.error(f"🚨 Error de datos (probable longitud excesiva): {str(e)}")
            form.password.errors.append('La contraseña excede el límite de caracteres permitido.')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"🔥 Error inesperado: {str(e)}")
            form.form_errors.append(f'Error del sistema: {str(e)}')
    
    return render_template('setup.html', form=form)