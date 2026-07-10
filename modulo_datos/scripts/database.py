import os
import psycopg2
from dotenv import load_dotenv

# Configuración DB para los scripts de extracción y carga de datos 

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "sslmode": os.getenv("DB_SSLMODE", "prefer")
}

def get_connection():
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        return conexion
    except Exception as e:
        print(f"Error al conectarse con PostgreSQL: {e}")
        return None
