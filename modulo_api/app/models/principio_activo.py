from pydantic import BaseModel

# Modelo de la Entidad: Principio Activo
class PrincipioActivoResponse(BaseModel):
    id_pa: int
    nom_estandar: str