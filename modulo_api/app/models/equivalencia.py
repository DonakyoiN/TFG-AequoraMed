from pydantic import BaseModel
from .medicamento import MedicamentoResumen, EquivalenciaResumen

# Modelo para mostrar Equivalencias Farmacéuticas
class EquivalenciaResponse(BaseModel):
    medicamento_origen: MedicamentoResumen
    por_atc: list[EquivalenciaResumen]
    por_principio_activo: list[EquivalenciaResumen]