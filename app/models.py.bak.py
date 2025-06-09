# app/models.py
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from flask_login import UserMixin
from datetime import timezone



class UserRole(enum.Enum):
   ADMIN = "admin"
   STAFF = "staff"
   USER = "user"

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    telegram = db.Column(db.String(20))
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    master = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Flask-Login requiere estos métodos:
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True  # O lógica personalizada si necesitas
    
    @property
    def is_active(self):
        return True  # Para manejar cuentas desactivadas
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
class SyscomCredential(db.Model):
    __tablename__ = 'syscom_credentials'

    id            = db.Column(db.Integer, primary_key=True)
    client_id     = db.Column(db.String(120), nullable=False)
    client_secret = db.Column(db.String(256), nullable=False)
    token         = db.Column(db.String(1224))
    expires_at = db.Column(db.DateTime(timezone=True))
    created_at    = db.Column(db.DateTime, default=db.func.now())
    updated_at    = db.Column(db.DateTime, default=db.func.now(),
                            onupdate=db.func.now())

    def is_expired(self, grace_days=0):
        if not self.expires_at:
            return True

        now = datetime.now(timezone.utc)
        return now > (self.expires_at - timedelta(days=grace_days))
        
        time_left = self.expires_at - datetime.utcnow()
        
        # Si ya expiró (tiempo negativo)
        if time_left < timedelta(seconds=0):
            return True
        
        # Verifica si el tiempo restante es menor que el período de gracia
        return time_left <= timedelta(days=grace_days)

    def token_status(self, grace_days: int = 7) -> str:
        """Devuelve el estado del token: 'active', 'expiring', 'expired' o 'no-token'"""
        if not self.token:
            return 'no-token'
        
        if not self.expires_at:
            return 'expired'
        
        time_left = self.expires_at - datetime.utcnow()
        
        if time_left < timedelta(seconds=0):
            return 'expired'
        
        if time_left <= timedelta(days=grace_days):
            return 'expiring'
        
        return 'active'

    def time_remaining(self) -> timedelta | None:
        """Devuelve el tiempo restante para expirar"""
        if not self.expires_at:
            return None
        
        time_left = self.expires_at - datetime.utcnow()
        return time_left if time_left > timedelta(0) else timedelta(0)