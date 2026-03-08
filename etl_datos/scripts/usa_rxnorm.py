import requests
import psycopg2
from psycopg2.extras import execute_values
import concurrent.futures
import time
from requests.adapters import HTTPAdapter

# Configuración DB
DB_CONFIG = {
    "dbname": "tfg_fuentes",
    "user": "donakyoin",
    "password": "purple",
    "host": "localhost",
    "port": "5432"
}

# URL Base de RxNorm
url_base_rxnorm = "https://rxnav.nlm.nih.gov/REST/rxcui"

# Sesión para evitar colapsos con la API y mayor rapidez 
sesion_http = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
sesion_http.mount("https://", adapter)

# 3. Obtención de las ATC y Principios Activos de USA 
def obtener_atc_pa(rxcui):
    atc_codes = []
    principios_activos = []
    
    try:
        # Primero se extrae ATC directo del producto
        res = sesion_http.get(f"{url_base_rxnorm}/{rxcui}/property.json?propName=ATC", timeout=10)
        if res.status_code == 200:
            props = res.json().get('propConceptGroup', {}).get('propConcept', [])
            atc_codes.extend([p['propValue'] for p in props if p['propName'] == 'ATC'])

        # Almacenamiento de Principio Activo + Búsqueda de ATC si no es encontrado anteriormente
        res_rel = sesion_http.get(f"{url_base_rxnorm}/{rxcui}/related.json?tty=IN", timeout=10)
        if res_rel.status_code == 200:
            concepts = res_rel.json().get('relatedGroup', {}).get('conceptGroup', [])
            for group in concepts:
                for concept in group.get('conceptProperties', []):
                    principios_activos.append(concept['name'].upper()) # Almacena Principio Activo + Mayusculas por Estándar
                    
                    # Segunda búsqueda de ATC por Principio Activo
                    if not atc_codes:
                        ing_rxcui = concept['rxcui']
                        res_ing = sesion_http.get(f"{url_base_rxnorm}/{ing_rxcui}/property.json?propName=ATC", timeout=10)
                        if res_ing.status_code == 200:
                            ing_props = res_ing.json().get('propConceptGroup', {}).get('propConcept', [])
                            atc_codes.extend([p['propValue'] for p in ing_props if p['propName'] == 'ATC'])
                        time.sleep(0.05)
        
        atc_final = " / ".join(list(set(atc_codes))) if atc_codes else "N/A" # Agrupa ATCs por '/'
        ing_final = " / ".join(list(set(principios_activos))) if principios_activos else "N/A" # Agrupa múltiples Principios Activos por '/'
        
        # Devolvemos una tupla de 3 elementos ahora
        return (atc_final, ing_final, rxcui)
    
    except Exception:
        return ("N/A", "N/A", rxcui)

# Carga de los datos obtenidos a la tabla usa_med
def carga_atc_pa_usamed():

    print("Cargando datos USA...")
    
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        
        # Selección de los ids de rxcui
        cursor.execute("SELECT DISTINCT rxnorm_id FROM usa_med;")
        rxnorm_ids = [fila[0] for fila in cursor.fetchall()]
        
        total = len(rxnorm_ids) # rxcui ids totales 
        print(f"Se van a procesar {total} IDs.")

        # Para evitar bloqueos vamos a ir de 50 a 50
        size_lote = 50
        for i in range(0, total, size_lote):
            lote_ids = rxnorm_ids[i : i + size_lote]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                resultados = list(executor.map(obtener_atc_pa, lote_ids))
                        
            # Sobreescribimos los N/A anteriores por el ATC y el Principio Activo
            update_query = "UPDATE usa_med SET id_atc = %s, name_ingredient = %s WHERE rxnorm_id = %s;"
            
            # Actualzación de datos
            datos_a_actualizar = []
            for res in resultados:

                if res[0] != "N/A" or res[1] != "N/A":
                    datos_a_actualizar.append(res)
            
            if datos_a_actualizar:
                cursor.executemany(update_query, datos_a_actualizar)
            
            conexion.commit()
            print(f"Progreso: {i + len(lote_ids)}/{total} procesados.", end="\r")
            time.sleep(1)

        print("\nProceso terminado con éxito.")

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
    carga_atc_pa_usamed()