import os
import psycopg2
from dotenv import load_dotenv

# Config de la DB auxiliar para los script de carga de datos

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path)

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),    
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def get_connection():
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        return conexion
    except Exception as e:
        print(f"Error al conectarse con PostgreSQL: {e}")
        return None
