from pydantic import BaseModel

# Modelo de la Entidad: Pais
class PaisResponse(BaseModel):
    id_pais: int
    iso_code: str
    nom_pais: str