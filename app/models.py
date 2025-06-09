# app/models.py
from app import db
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from flask_login import UserMixin
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

# ---------------------------------------------------
# Asociación Producto <-> Categoria (muchos a muchos)
# ---------------------------------------------------
product_category = Table(
    "product_category",
    db.metadata,
    Column("producto_id", Integer, ForeignKey("productos.id"), primary_key=True),
    Column("categoria_id", Integer, ForeignKey("categorias.id"), primary_key=True),
)

# -------------------------------
# Modelos básicos de Usuario/Rol
# -------------------------------
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
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

# -------------------------------
# Modelo Marca
# -------------------------------
class Marca(db.Model):
    __tablename__ = "marcas"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    logo_url = db.Column(db.String(500))
    productos = relationship("Producto", back_populates="marca")

# -------------------------------
# Modelo Categoria
# -------------------------------
class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, ForeignKey("categorias.id"), nullable=True)
    children = relationship("Categoria", backref=db.backref("parent", remote_side=[id]))
    productos = relationship(
        "Producto",
        secondary=product_category,
        back_populates="categorias",
    )

# -------------------------------
# Modelo Producto
# -------------------------------
class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)

    # Campos básicos de Syscom
    modelo = db.Column(db.String(100), nullable=True)
    titulo = db.Column(db.String(500), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    descripcion_corta = db.Column(db.String(700), nullable=True)
    total_existencia = db.Column(db.Integer, default=0)
    sat_key = db.Column(db.String(20), nullable=True)

    img_portada = db.Column(db.String(500), nullable=True)
    img_thumbnail = db.Column(db.String(500), nullable=True)

    precio_lista = db.Column(db.Numeric(10, 2), nullable=True)
    precio_especial = db.Column(db.Numeric(10, 2), nullable=True)
    margen = db.Column(db.Float, default=0.0)
    descuento = db.Column(db.Float, default=0.0)
    precio_publico = db.Column(db.Numeric(10, 2), nullable=True)
    precio_editado = db.Column(db.Boolean, default=False)
    visible = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    marca_id = db.Column(db.Integer, ForeignKey("marcas.id"), nullable=True)
    marca = relationship("Marca", back_populates="productos")

    categorias = relationship(
        "Categoria",
        secondary=product_category,
        back_populates="productos",
    )

    caracteristicas = db.Column(db.Text, nullable=True)
    recursos = db.Column(db.Text, nullable=True)

    # Relación con imágenes adicionales
    imagenes = relationship(
        "ProductoImagen",
        back_populates="producto",
        cascade="all, delete-orphan",
    )

    # Relación con el historial de cambios
    historial_cambios = relationship(
        "HistorialCambios",
        back_populates="producto",
        cascade="all, delete-orphan",
    )

# -------------------------------
# Modelo ProductoImagen
# -------------------------------
class ProductoImagen(db.Model):
    __tablename__ = "producto_imagenes"
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, ForeignKey("productos.id"), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    es_local = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    producto = relationship("Producto", back_populates="imagenes")

# -------------------------------
# Modelo HistorialCambios
# -------------------------------
class HistorialCambios(db.Model):
    __tablename__ = "historial_cambios"
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, ForeignKey("productos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)
    campo_modificado = db.Column(db.String(50), nullable=False)
    valor_anterior = db.Column(db.String(500), nullable=True)
    valor_nuevo = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    producto = relationship("Producto", back_populates="historial_cambios")
    usuario = relationship("User")

# -------------------------------
# Modelo SyscomCredential
# -------------------------------
class SyscomCredential(db.Model):
    __tablename__ = 'syscom_credentials'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(120), nullable=False)
    client_secret = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(1224))
    expires_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(),
                        onupdate=db.func.now())

    def is_expired(self, grace_days=0):
        """
        Retorna True si el token ya expiró o está a punto de expirar dentro de 'grace_days'.
        Usamos siempre naive UTC para evitar mezclar aware y naive.
        """
        if not self.expires_at:
            return True
        # Usamos UTC naive en ambos lados
        now = datetime.utcnow()
        # Si expires_at vino con tzinfo, lo convertimos a naive UTC
        exp = self.expires_at
        if getattr(exp, 'tzinfo', None):
            exp = exp.astimezone(timezone.utc).replace(tzinfo=None)
        # Comparamos: expiración adelantada por los 'grace_days'
        return now > (exp - timedelta(days=grace_days))
        
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