import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Configuración DB
load_dotenv()
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),    
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Directorio archivo .csv
ARCHIVO_CSV = '../data/Productos_RECETA_SIMPLE.csv'

def cargar_datos_chilemed():

    print("Leyendo el archivo CSV con pandas...")

    try:
        # Lectura del .csv
        df = pd.read_csv(ARCHIVO_CSV, sep=',', dtype=str)
        
        # Mapeo de datos del csv a la tabla chile_med
        df_chile = pd.DataFrame()
        df_chile['registro'] = df.get('Registro', 'N/A')                  
        df_chile['nombre_comercial'] = df.get('Nombre', 'N/A')
        df_chile['fecha_registro'] = df.get('Fecha Registro', 'N/A')
        df_chile['empresa'] = df.get('Empresa', 'N/A')                  
        df_chile['principio_activo'] = df.get('Principio Activo', 'N/A')
        df_chile['control_legal'] = df.get('Control Legal', 'N/A')

        # Limpieza de valores nulos
        df_chile = df_chile.fillna('N/A')

        # Convertir el DataFrame a una lista de tuplas
        registros_tuplas = [tuple(x) for x in df_chile.to_numpy()]

        print(f"CSV leído correctamente. Se encontraron {len(registros_tuplas)} medicamentos.")

        # Conexión a Postgres
        conexion = psycopg2.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # Inserción de datos
        insert_chilemed = """
            INSERT INTO chile_med
            (registro, nombre_comercial, fecha_registro, empresa, principio_activo, control_legal)
            VALUES %s
            ON CONFLICT (registro) DO NOTHING;
        """
        execute_values(cursor, insert_chilemed, registros_tuplas)
        conexion.commit()
        
        print(f"\nCarga completada con éxito.")

    except KeyError as e:
        print(f"Error: No se encontró la columna {e} en tu CSV.")
    except Exception as e:
        print(f"Error de conexión: {e}")

        if 'conexion' in locals():
            conexion.rollback()
    finally:
        # Cerrar conexión
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()
            print("Conexión a base de datos cerrada.")

if __name__ == "__main__":
    cargar_datos_chilemed()