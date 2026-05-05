from fastapi import FastAPI
from app.routers import medicamentos

app = FastAPI(
    title="ProjectMed API",
    description="Consulta de Equivalencias Farmacéuticas Internacional",
    version="1.0.0"
)

# TODO: Endpoints para realizar las consultas

# Incluímos los Routers
app.include_router(medicamentos.router)

# Mensaje de Estado para ruta base
@app.get("/", tags=["Estado"])
def root():
    return {"status": "ok", "mensaje": "API de la Aplicación - Activa"}