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
    print(f"Leyendo el archivo CSV con pandas...")

    try:
        # Lectura del .csv
        df = pd.read_csv(ARCHIVO_CSV, sep=',', dtype=str)

        # Limpieza de valores nulos
        df = df.where(pd.notnull(df), None)

        # Mapeo de datos del csv a la tabla portugal_med
        df_pt = pd.DataFrame()
        df_pt['active_substance'] = df["Active Substance/INN"]
        df_pt['product_name'] = df["Medicinal Product’s Name"]
        df_pt['dose_form'] = df["Pharmaceutical Dose Form"]
        df_pt['strength'] = df["Strength"]
        df_pt['ma_holder'] = df["MA Holder"]
        df_pt['ma_status'] = df["MA Status"]
        df_pt['marketing'] = df["Marketing"]

        # Convertir el DataFrame a una lista de tuplas
        registros_tuplas = [tuple(x) for x in df_pt.to_numpy()]

        print(f"CSV leído correctamente. Se encontraron {len(registros_tuplas)} medicamentos.")

        # Conexión a Postgres
        conexion = psycopg2.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # Inserción de datos
        insert_portugalmed = """
            INSERT INTO portugal_med
            (active_substance, product_name, dose_form, strength, ma_holder, ma_status, marketing)
            VALUES %s
        """

        execute_values(cursor, insert_portugalmed, registros_tuplas)
        conexion.commit()

        print(f"\nCarga completada con éxito.")

    except KeyError as e:
        print(f"Error: No se encontró la columna {e} en tu CSV.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        # Cerrar conexión
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    cargar_datos_portugalmed()
