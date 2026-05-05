from pydantic import BaseModel

# Modelo de la Entidad: ATC
class AtcResponse(BaseModel):
    id_atc: int
    code_atc: str
    desc_es: str | None
    desc_en: str | None