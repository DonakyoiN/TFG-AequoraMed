from pydantic import BaseModel
from .principio_activo import PrincipioActivoResponse
from .atc import AtcResponse

# Modelo de la Entidad: Medicamento
class MedicamentoResumen(BaseModel):
    id_med: int
    nom_comercial: str
    laboratorio: str | None
    iso_code: str
    nom_pais: str
    forma_farmaceutica: str | None
    via_administracion: str | None

class MedicamentoDetalle(MedicamentoResumen):
    principios_activos: list[PrincipioActivoResponse]
    codigos_atc: list[AtcResponse]