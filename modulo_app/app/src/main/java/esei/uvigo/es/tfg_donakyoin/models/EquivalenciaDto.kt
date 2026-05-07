package esei.uvigo.es.tfg_donakyoin.models
import com.squareup.moshi.JsonClass

// Modelo de Equivalencia
@JsonClass(generateAdapter = true)
data class EquivalenciaDto(
    val medicamento_origen: MedicamentoDto,
    val por_atc: List<MedicamentoDto>,
    val por_principio_activo: List<MedicamentoDto>
)
