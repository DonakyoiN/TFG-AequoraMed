import os
from dotenv import load_dotenv
import requests
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import time

# Configuración DB
load_dotenv()
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),    
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def cargar_datos_fda():

    print("Iniciando extracción base de OpenFDA...")

    url_base_fda = "https://api.fda.gov/drug/drugsfda.json"
    medicamentos_usa = []
    limite_segmento = 1000 # Los datos están segmentados dentro del json, vamos ir de 1000 en 1000
    skip = 0 # Desplazamiento de medicamentos

    print("Descargando datos de la FDA...")
    
    while skip <= 25000: # Límite de 25000 para evitar bloqueos de la API
        print(f"Descargando segmento (skip={skip})...", end="\r")
        # Filtro extra: Verificar que tenga un id rxcui asociado
        url = f"{url_base_fda}?search=_exists_:openfda.rxcui&limit={limite_segmento}&skip={skip}"
        
        try:
            respuesta = requests.get(url)
            if respuesta.status_code != 200:
                break
                
            datos = respuesta.json().get('results', [])
            if not datos:
                break
                
            medicamentos_usa.extend(datos)
            skip += limite_segmento
            time.sleep(0.5) 
            
        except Exception as e:
            print(f"\nError en la descarga: {e}")
            break

    print(f"\nProcesando {len(medicamentos_usa)} medicamentos de la FDA...")

    lista_meds = []
    
    # Recorremos los medicamentos de cada segemento
    for med in medicamentos_usa:
        app_number = med.get('application_number', 'N/A')
        sponsor_name = med.get('sponsor_name', 'N/A')
        
        # Recorremos el producto específico para dicho medicamento
        for producto in med.get('products', []):

            brand_name = producto.get('brand_name', 'N/A')
            dosage_form = producto.get('dosage_form', 'N/A')
            route = producto.get('route', 'N/A')
            marketing_status = producto.get('marketing_status', 'N/A')
            
            active_ingredients = producto.get('active_ingredients', [])
            strengths = ", ".join([i.get('strength', '') for i in active_ingredients])
            
            openfda_data = med.get('openfda', {})
            rxcuis = openfda_data.get('rxcui', ['N/A']) 
            rxcui = rxcuis[0] if isinstance(rxcuis, list) and len(rxcuis) > 0 else 'N/A'
            
            lista_meds.append({
                'rxnorm_id': rxcui,
                'application_number': app_number,
                'id_atc': 'N/A', # ATC Vacío -> Será asignado con script de RxNorm
                'name_ingredient': 'N/A', # Principio Activo Vacío -> Será asignado con script RxNorm 
                'brand_name': brand_name,
                'sponsor_name': sponsor_name,
                'strength': strengths if strengths else 'N/A',
                'route_administration': route,
                'dosage_form': dosage_form,
                'marketing_status': marketing_status
            })
    
    df_usa = pd.DataFrame(lista_meds)
    
    df_usa = df_usa[df_usa['rxnorm_id'] != 'N/A'].copy() # Descarta los que no tengan rxcui
    df_usa = df_usa[df_usa['marketing_status'].isin(['Prescription', 'Over-the-counter'])].copy() # Almacena solo los que estén comercializados o bajo preescripción
    df_usa = df_usa.fillna('N/A')    # Filtro de valores nulos
    
    # Eliminación de duplicados
    df_usa = df_usa.drop_duplicates(subset=['rxnorm_id', 'application_number'])
    
    # Conversión a tuplas
    registros_tuplas = [tuple(x) for x in df_usa.to_numpy()]
    
    # Conexión a Postgres
    print("Conectando con Postgres...")

    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # Limpieza de datos
        cursor.execute("TRUNCATE TABLE fuentes.usa_med;")

        insert_usa = """
            INSERT INTO fuentes.usa_med (
                rxnorm_id, application_number, id_atc, name_ingredient, brand_name,
                sponsor_name, strength, route_administration, dosage_form, marketing_status
            ) VALUES %s
            ON CONFLICT (rxnorm_id, application_number) DO NOTHING;
        """
        
        execute_values(cursor, insert_usa, registros_tuplas)
        conexion.commit()

        print(f"Se han guardado {len(registros_tuplas)} medicamentos base de USA.")

    except Exception as e:
        print(f"Error de base de datos: {e}")
        if 'conexion' in locals(): conexion.rollback()
    finally:
        # Cerrar conexión
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): 
            conexion.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    cargar_datos_fda()