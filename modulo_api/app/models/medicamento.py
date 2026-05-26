from pydantic import BaseModel
from .principio_activo import PrincipioActivoResponse
from .atc import AtcResponse

# Modelo de la Entidad: Medicamento -> Para Item Card en App
class MedicamentoResumen(BaseModel):
    id_med: int
    nom_comercial: str
    laboratorio: str | None
    iso_code: str
    nom_pais: str
    forma_farmaceutica: str | None
    via_administracion: str | None

# Modelo de Medicamento para Equivalencias -> Para Bottom Sheet de Equivalencias en App
class EquivalenciaResumen(MedicamentoResumen):
    dosaje: str | None

# Modelo de Medicamento con los Detalles -> Para Fragment Detail en App
class MedicamentoDetalle(BaseModel):
    id_med: int
    nom_comercial: str
    reg_pais: str | None
    laboratorio: str | None
    iso_code: str
    nom_pais: str
    forma_farmaceutica: str | None
    via_administracion: str | None
    dosaje: str | None
    principios_activos: list[PrincipioActivoResponse]
    codigos_atc: list[AtcResponse]