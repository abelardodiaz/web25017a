# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Optional, Length

class SetupForm(FlaskForm):
    username = StringField('Usuario', [
        validators.DataRequired(),
        validators.Length(min=4, max=25)
    ])
    password = PasswordField('Contraseña', [
        validators.DataRequired(),
        validators.Length(min=8, max=128),  # Longitud mínima 8
        validators.EqualTo('confirm', message='Las contraseñas deben coincidir')
    ])
    confirm = PasswordField('Repetir Contraseña')
    email = StringField('Email', [validators.Optional(), validators.Email()])
    first_name = StringField('Nombre', [validators.Optional()])
    last_name = StringField('Apellido', [validators.Optional()])
    whatsapp = StringField('WhatsApp', [validators.Optional()])
    telegram = StringField('Telegram', [validators.Optional()])

class LoginForm(FlaskForm):
    username = StringField('Usuario', [
        validators.DataRequired(),
        validators.Length(min=4, max=25)
    ])
    password = PasswordField('Contraseña', [
        validators.DataRequired()
    ])
    remember = BooleanField('Recordar sesión')

class UserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    role = SelectField('Rol', choices=[
        ('admin', 'Administrador'), 
        ('staff', 'Staff'), 
        ('user', 'Usuario')
    ], validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email()])

class EmptyForm(FlaskForm):
    pass

class SyscomCredentialForm(FlaskForm):
    client_id     = StringField('Client ID', validators=[DataRequired()])
    client_secret = StringField('Client Secret', validators=[DataRequired()])