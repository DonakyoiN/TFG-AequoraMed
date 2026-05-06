from pydantic import BaseModel

# Modelo de la Entidad: Forma Farmacéutica
class FormaFarmaceuticaResponse(BaseModel):
    id_forma: int
    descripcion: str