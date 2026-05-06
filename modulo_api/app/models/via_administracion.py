from pydantic import BaseModel

# Modelo de la Entidad: Vía Administración
class ViaAdministracionResponse(BaseModel):
    id_via: int
    descripcion: str