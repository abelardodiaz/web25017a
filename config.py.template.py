# config.py.example.py example about how to configure the database connection 
#rename this file to config.py and fill the fields with the correct values
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-segura'
    DEFAULT_THEME = 'dark'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@server:3306/master001' #keep database name as master001
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 299}
    DB_RESETEADA = True  # flag to know if the database was reseted
    
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 299,
    'pool_pre_ping': True  
}

