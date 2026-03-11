import os
from dotenv import load_dotenv
import requests 
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

def cargar_datos_canadamed():

    print("Iniciando extracción de API DPD Canadá...")

    # * Endpoints principales
    url_drugs = "https://health-products.canada.ca/api/drug/drugproduct/?lang=en&type=json" # Medicamentos
    url_ingredients = "https://health-products.canada.ca/api/drug/activeingredient/?lang=en&type=json" # Principios Activos
    url_atc = "https://health-products.canada.ca/api/drug/therapeuticclass/?lang=en&type=json" # Códigos ATC
    url_route = "https://health-products.canada.ca/api/drug/route/?lang=en&type=json" # Vía de administración
    url_form = "https://health-products.canada.ca/api/drug/form/?lang=en&type=json" # Forma farmacéutica
    url_status = "https://health-products.canada.ca/api/drug/status/?lang=en&type=json" # Estado del registro

    # Descarga de datos de la API pasado al pandas
    print("Descargando Datos...")
    df_drugs = pd.DataFrame(requests.get(url_drugs).json())
    df_ingredients = pd.DataFrame(requests.get(url_ingredients).json())
    df_atc = pd.DataFrame(requests.get(url_atc).json())
    df_route = pd.DataFrame(requests.get(url_route).json())
    df_form = pd.DataFrame(requests.get(url_form).json())
    df_status = pd.DataFrame(requests.get(url_status).json())

    # Agrupación de datos con más de un Principio Activo
    df_ing_name = df_ingredients.groupby('drug_code')['ingredient_name'].apply(lambda x: ' / '.join(x.dropna().astype(str).unique())).reset_index()
    df_ing_str = df_ingredients.groupby('drug_code')['strength'].apply(lambda x: ' / '.join(x.dropna().astype(str).unique())).reset_index()
    df_ing_unit = df_ingredients.groupby('drug_code')['strength_unit'].apply(lambda x: ' / '.join(x.dropna().astype(str).unique())).reset_index()

    df_ing_grouped = df_ing_name.merge(df_ing_str, on='drug_code').merge(df_ing_unit, on='drug_code')
    
    # Limpieza de duplicados
    df_atc_clean = df_atc.drop_duplicates(subset=['drug_code'])
    df_route_clean = df_route.drop_duplicates(subset=['drug_code'])
    df_form_clean = df_form.drop_duplicates(subset=['drug_code'])
    df_status_clean = df_status.drop_duplicates(subset=['drug_code'])

    print("Cruzando datos en Pandas...")
    df_merged = pd.merge(df_drugs, df_ing_grouped, on='drug_code', how='left')
    df_merged = pd.merge(df_merged, df_atc_clean, on='drug_code', how='left')
    df_merged = pd.merge(df_merged, df_route_clean, on='drug_code', how='left')
    df_merged = pd.merge(df_merged, df_form_clean, on='drug_code', how='left')
    df_merged = pd.merge(df_merged, df_status_clean, on='drug_code', how='left')

    # Filtro para medicamentos de consumo humano y comercializables
    if 'class_name' in df_merged.columns and 'status' in df_merged.columns:
        df_filtered = df_merged[
            (df_merged['class_name'] == 'Human') & 
            (df_merged['status'] == 'Marketed')
        ].copy()
    else:
        df_filtered = df_merged.copy()

    # Valores nulos
    df_filtered = df_filtered.fillna("N/A")

    # Mapeo de columnas al DDL canada_med
    df_final = pd.DataFrame({
        'drug_code': df_filtered.get('drug_code', 'N/A'),
        'din': df_filtered.get('drug_identification_number', 'N/A'),
        'atc_number': df_filtered.get('tc_atc_number', 'N/A'),
        'ingredient_name': df_filtered.get('ingredient_name', 'N/A'),
        'brand_name': df_filtered.get('brand_name', 'N/A'),
        'company_name': df_filtered.get('company_name', 'N/A'),
        'class_name': df_filtered.get('class_name', 'N/A'),
        'strength': df_filtered.get('strength', 'N/A'),
        'strength_unit': df_filtered.get('strength_unit', 'N/A'),
        'route_administration': df_filtered.get('route_of_administration_name', 'N/A'),
        'pharmaceutical_form': df_filtered.get('pharmaceutical_form_name', 'N/A'),
        'status': df_filtered.get('status', 'N/A')
    })

    # Eliminar duplicados de ID
    df_final = df_final.drop_duplicates(subset=['drug_code'])

    # Conversión a tuplas
    registro_tuplas = [tuple(x) for x in df_final.to_numpy()]

    # Conexión a Postgres
    print("Conectando con Postgres...")

    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # Insertar datos
        insert_canadamed = """
            INSERT INTO canada_med (
                drug_code, din, atc_number, ingredient_name, brand_name,
                company_name, class_name, strength, strength_unit, route_administration,
                pharmaceutical_form, status
            ) VALUES %s
            ON CONFLICT (drug_code) DO NOTHING;
        """

        execute_values(cursor, insert_canadamed, registro_tuplas)
        conexion.commit()

        print(f"Se han registrado {len(registro_tuplas)} medicamentos.")

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
    cargar_datos_canadamed()



