from pydantic import BaseModel
from .medicamento import MedicamentoResumen

# Modelo para mostrar Equivalencias Farmacéuticas
class EquivalenciaResponse(BaseModel):
    medicamento_origen: MedicamentoResumen
    por_atc: list[MedicamentoResumen]
    por_principio_activo: list[MedicamentoResumen]