from fastapi import FastAPI, Depends
from psycopg2.extensions import connection
from app.routers import medicamentos, equivalencias
from app.models.pais import PaisResponse
from app.database import get_db

# Definición de la API
app = FastAPI(
    title="ProjectMed API",
    description="API para la Aplicación de consultas de equivalencias farmacéuticas Internacional",
    version="1.0.0"
)

# Mensaje de Estado para ruta base
@app.get("/", tags=["Estado"])
def root():
    return {"status": "ok", "mensaje": "API de la Aplicación - Activa"}

# Endoint de listado de países
@app.get("/paises", response_model=list[PaisResponse], tags=["Países"])
def listar_paises(db: connection = Depends(get_db)):
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

# Incluímos los Routers
app.include_router(medicamentos.router)
app.include_router(equivalencias.router)