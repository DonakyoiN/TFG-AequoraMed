import os
from dotenv import load_dotenv
import requests
import psycopg2
from psycopg2.extras import execute_values
import concurrent.futures
import time
from requests.adapters import HTTPAdapter

# Configuración DB
load_dotenv()
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),    
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# URLs de CIMA
url_busqueda = "https://cima.aemps.es/cima/rest/medicamentos" # Para lista de medicamentos
url_detalle = "https://cima.aemps.es/cima/rest/medicamento" # Para información de los medicamentos

# Evitar colapsos con la API y mayor rapidez
sesion_http = requests.Session()
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
sesion_http.mount("https://", adapter)

# Función para obtener los datos de un medicamento
def procesar_medicamento(med):
    nregistro = med.get("nregistro") # Número de registro del medicamento, Tipo Texto
    nombre = med.get("nombre") # Nombre del medicamento, Tipo Texto
    labtitular = med.get("labtitular") # Laboratorio titular del medicamento, Tipo Texto
    cpresc = med.get("cpresc", "SIN RECETA") # Condiciones de prescripción del medicamento, Tipo Texto
    dosis = med.get("dosis", "") # Dosis del o los principios activos, Tipos Texto
    estado_obj = med.get("estado", {}) # Estado de registro del medicamento, Tipo estado
    
    # El valor de tipo estado tiene los siguientes valores: rev, susp y aut las cuales son fechas de Renovación/Suspensión/Autorización
    if estado_obj.get("rev"):
        estado = "Revocado"
    elif estado_obj.get("susp"):
        estado = "Suspendido"
    elif estado_obj.get("aut"):
        estado = "Autorizado"
    else:
        estado = "Desconocido"
    
    # Nos interesa solo aquellos medicamentos autorizados
    if estado != "Autorizado":
        return None

    forma_farmaceutica = med.get("formaFarmaceutica", {}).get("nombre", "") # Forma farmacéutica, Tipo item
    # Lista de las vías de administración para las que está autorizado el medicamento, Tipo item[]
    vias_lista = [via.get("nombre") for via in med.get("viasAdministracion", []) if via.get("nombre")]
    vias_str = ", ".join(vias_lista)
    
    # Strings para almacenar luego el ATC y Principio Activio
    atc_str = ""
    pa_str = ""
    
    try:
        # Sesion para obtener los detalles de un medicamento
        request_detalles = sesion_http.get(url_detalle, params={"nregistro": nregistro}, timeout=10)

        if request_detalles.status_code == 200: # Si HTTP 200 (OK)
            detalle = request_detalles.json()

            # Lista de códigos ATC asociados al medicamento, Tipo atc[]
            atcs_lista = [
                atc.get("codigo")
                for atc in detalle.get("atcs", [])
                if atc.get("codigo") and len(atc.get("codigo")) == 7 # Si la longitud del código = 7 entonces es el ATC-Nivel 5
            ]
            atc_str = ", ".join(atcs_lista)
            
            # Lista de los principios activos del medicamento, Tipo principioActivo[]
            pa_lista = [pa.get("nombre") for pa in detalle.get("principiosActivos", []) if pa.get("nombre")]
            pa_str = " / ".join(pa_lista) # '/' en vez de ',' para que no se mezclen los que tienen más de uno 

    except Exception as e:
        print(f"No se pudo obtener detalle del medicamento {nregistro}: {e}")
    
    return (nregistro, atc_str, pa_str, nombre, labtitular, dosis, vias_str, forma_farmaceutica, estado, cpresc)

# Función para insertar datos a la database
def carga_datos_spainmed():
    pagina = 1 # Inicialización de número de página
    hay_mas_datos = True
    registros_insertados = 0

    print(f"Iniciando extracción de datos desde página {pagina}")

    try:
        # Conexión a Postgres
        conexion = psycopg2.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        # Limpieza de datos
        cursor.execute("TRUNCATE TABLE spain_med;")
    except Exception as e:
        print(f"Error al conectarse con PostgreSQL: {e}")
        return
    
    # Vamos a recorrer hasta que no hayan más datos que insertar
    while hay_mas_datos:
        # Parámetros de búsqueda oficial - ej. https://cima.aemps.es/cima/rest/medicamentos?comercializado=true&pagina=2&tamanioPagina=100
        params = {
            "comercializado": "true", # Necesitamos que sea un medicamento apto para la comercialización
            "pagina": pagina, # Número de página
            "tamanioPagina": 50  # Extraemos datos de 50 en 50 para no tener problemas con la API
        }

        exito_pagina = False

        for intento in range(3): # Si falla la conexión reintentará hasta un máximo de 3 intentos obtener los datos 
            try:
                # Sesion para la busqueda de la lista de medicamentos
                request_busqueda = sesion_http.get(url_busqueda, params=params, timeout=15)
                request_busqueda.raise_for_status()
                datos_json = request_busqueda.json() # Obtención del .json con los datos del medicamento
                exito_pagina = True
                break 
            except requests.exceptions.RequestException as e:
                print(f"Fallo en página {pagina} (Intento {intento+1}/3). Esperando 5 seg...")
                time.sleep(5) 

        if not exito_pagina:
            print(f"Imposible procesar la página {pagina}. Abortando.")
            break
        
        medicamentos_pagina = datos_json.get("resultados", [])
        
        if not medicamentos_pagina:
            print("\nExtracción finalizada con éxito.")
            break
        
        print(f"\nProcesando página {pagina}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=19) as executor:
            resultados = list(executor.map(procesar_medicamento, medicamentos_pagina))

        # Solo almacenamos los que estén Autorizados
        registros_tuplas = [res for res in resultados if res is not None]

        # Inserta los detalles del medicamento en la tabla spain_med
        insert_spainmed = """
        INSERT INTO spain_med 
        (nregistro, atc, principios_activos, nombre, labtitular, dosis, vias_administracion, forma_farmaceutica, estado, cpresc)
        VALUES %s
        ON CONFLICT (nregistro) DO UPDATE SET 
            atc = EXCLUDED.atc,
            principios_activos = EXCLUDED.principios_activos,
            nombre = EXCLUDED.nombre,
            dosis = EXCLUDED.dosis,
            estado = EXCLUDED.estado;
        """
        execute_values(cursor, insert_spainmed, registros_tuplas)
        conexion.commit()
        
        # Registro de datos obtenidos
        registros_insertados += len(registros_tuplas)
        print(f"{len(registros_tuplas)} procesados. (Total sesión: {registros_insertados})")

        pagina += 1 # Aumentamos número de página para seguir obteniendo datos
        time.sleep(1)
    
    # Al acabar cerramos conexión con Postgres
    cursor.close()
    conexion.close()
    print(f"\nProceso terminado.")

if __name__ == "__main__":
    carga_datos_spainmed()