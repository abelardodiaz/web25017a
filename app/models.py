# app/models.py
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Cambiar de 128 a 256
    email = db.Column(db.String(120))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    telegram = db.Column(db.String(20))
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    master = db.Column(db.Boolean, default=False)  # Nuevo campo añadido

    created_at = db.Column(db.DateTime, default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)