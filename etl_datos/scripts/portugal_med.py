import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Configuración DB
DB_CONFIG = {
    "dbname": "tfg_fuentes",
    "user": "donakyoin",    
    "password": "purple",
    "host": "localhost",
    "port": "5432"
}

# Directorio archivo .csv
ARCHIVO_CSV = '../data/lista_infomed.csv'

def cargar_datos_portugalmed():
    
    print("Leyendo el archivo CSV con pandas...")

    try:
        # Lectura del .csv
        df = pd.read_csv(ARCHIVO_CSV, sep=',', dtype=str)

        # Mapeo de datos del csv a la tabla portugal_med
        df_pt = pd.DataFrame()
        df_pt['active_substance'] = df.get('Active Substance/INN', 'N/A')     
        df_pt['product_name'] = df.get('Medicinal Product’s Name', 'N/A')  
        df_pt['dose_form'] = df.get('Pharmaceutical Dose Form', 'N/A')  
        df_pt['strength'] = df.get('Strength', 'N/A')  
        df_pt['ma_holder'] = df.get('MA Holder', 'N/A')  
        df_pt['ma_status'] = df.get('MA Status', 'N/A')  
        df_pt['marketing'] = df.get('Marketing', 'N/A') 

        # Limpieza de valores nulos
        df_pt = df_pt.fillna('N/A')

        # Principio Activo en Mayusculas por Estándar con los otros datos
        df_pt['active_substance'] = df_pt['active_substance'].astype(str).str.upper()

        # Convertir el DataFrame a una lista de tuplas
        registros_tuplas = [tuple(x) for x in df_pt.to_numpy()]

        print(f"CSV leído correctamente. Se encontraron {len(registros_tuplas)} medicamentos.")

        # Conexión a Postgres
        conexion = psycopg2.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # Limpiar la tabla antes de la carga para no duplicar datos (Portugal no tiene un dato de registro)
        cursor.execute("TRUNCATE TABLE portugal_med RESTART IDENTITY;")
        
        # Inserción de datos
        insert_portugalmed = """
            INSERT INTO portugal_med
            (active_substance, product_name, dose_form, strength, ma_holder, ma_status, marketing)
            VALUES %s
        """

        execute_values(cursor, insert_portugalmed, registros_tuplas)
        conexion.commit()

        print("\nCarga completada con éxito.")

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
    cargar_datos_portugalmed()
