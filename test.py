import mysql.connector
from config import Config

try:
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT
    )
    print("✅ ¡Conexión exitosa a MySQL!")
    conn.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")