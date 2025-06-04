# /app/__init__.py
from flask import Flask, session, current_app, request, redirect, url_for, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()  # Inicializa CSRFProtect

def create_app():
    #app = Flask(__name__)
    app = Flask(__name__, static_url_path='/111/static')
    app.config.from_object('config.Config')  # Asegúrate de que config.Config tenga SECRET_KEY
    
    # Inicializar extensiones
    db.init_app(app)
    csrf.init_app(app)  # Activa la protección CSRF
    
    with app.app_context():
        from app.models import User
        try:
            inspector = db.inspect(db.engine)
            if inspector.has_table('users'):
                user_count = User.query.count()
                app.config['DB_RESETEADA'] = user_count == 0
            else:
                db.create_all()
                app.config['DB_RESETEADA'] = True
            db.engine.connect()
        except Exception as e:
            app.logger.error(f"🔥 Error crítico de base de datos: {str(e)}")
            db.create_all()
            app.config['DB_RESETEADA'] = True

    # Inyectar variables de tema y usuario (sin cambios aquí)
    @app.context_processor
    def inject_theme():
        return dict(current_theme=app.config.get('DEFAULT_THEME', 'dark'))
    
    @app.context_processor
    def inject_user():
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return dict(current_user=user)
    
    # Registrar Blueprints (sin cambios aquí)
    from app.routes import main_routes, setup_routes, auth_routes, panel_routes
    app.register_blueprint(main_routes.main_bp)
    app.register_blueprint(setup_routes.setup_bp)
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(panel_routes.panel_bp)
    
    # Middleware de verificación de DB (sin cambios aquí)
    @app.before_request
    def check_db_status():
        if current_app.config.get('DB_RESETEADA', True):
            if request.endpoint not in ['setup.setup', 'static', 'panel.redirect_handler']:
                return redirect(url_for('setup.setup'))
    
    return app
