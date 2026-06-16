from fastapi import FastAPI, Depends
from psycopg2.extensions import connection
from app.routers import medicamentos, equivalencias
from app.models.pais import PaisResponse
from app.models.forma_farmaceutica import FormaFarmaceuticaResponse
from app.models.via_administracion import ViaAdministracionResponse
from app.database import get_db

# Definición de la API
app = FastAPI(
    title="AequoraMed API",
    description="API para la Aplicación de consultas de equivalencias farmacéuticas Internacional",
    version="1.0.0"
)

# Mensaje de Estado para ruta base
@app.get("/", tags=["Estado"])
def root():
    # Detalles del Endpoint dentro del DocStrings
    """
    Muestra el estado de la API.
    """
    return {"status": "ok", "mensaje": "API de la Aplicación - Activa"}

# Endoint de listado de países
@app.get("/paises", response_model=list[PaisResponse], tags=["Países"])
def listar_paises(db: connection = Depends(get_db)):
    # Detalles del Endpoint dentro del DocStrings
    """
    Listado de países de los que se tiene información de Medicamentos.
    """
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT id_pais, iso_code, nom_pais 
            FROM med.pais 
            ORDER BY id_pais
            """
        )
        rows = cur.fetchall()
    return [PaisResponse(**row) for row in rows]

# Endoint de listado de formas farmacéuticas
@app.get("/formas_farmaceuticas", response_model=list[FormaFarmaceuticaResponse], tags=["Formas Farmacéuticas"])
def listar_formas(db: connection = Depends(get_db)):
    # Detalles del Endpoint dentro del DocStrings
    """
    Listado de las formas farmacéuticas de los distintos Medicamentos de la Base de Datos.
    """
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT id_forma, descripcion
            FROM med.forma_farmaceutica
            ORDER BY descripcion
            """
        )
        rows = cur.fetchall()
    return [FormaFarmaceuticaResponse(**row) for row in rows]

# Endoint de listado de vías de administración
@app.get("/vias_administracion", response_model=list[ViaAdministracionResponse], tags=["Vías de Administración"])
def listar_vias(db: connection = Depends(get_db)):
    # Detalles del Endpoint dentro del DocStrings
    """
    Listado de las vías de administración de los distintos Medicamentos de la Base de Datos.
    """
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT id_via, descripcion
            FROM med.via_administracion
            ORDER BY descripcion
            """
        )
        rows = cur.fetchall()
    return [ViaAdministracionResponse(**row) for row in rows]

# Incluímos los Routers
app.include_router(medicamentos.router)
app.include_router(equivalencias.router)