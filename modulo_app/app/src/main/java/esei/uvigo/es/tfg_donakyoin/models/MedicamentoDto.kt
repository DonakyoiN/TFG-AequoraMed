package esei.uvigo.es.tfg_donakyoin.models
import com.squareup.moshi.JsonClass

// Modelo de Medicamento
@JsonClass(generateAdapter = true)
data class MedicamentoDto(
    val id_med: Int,
    val nom_comercial: String,
    val laboratorio: String? = null,
    val iso_code: String,
    val nom_pais: String,
    val forma_farmaceutica: String? = null,
    val via_administracion: String? = null
)

@JsonClass(generateAdapter = true)
data class MedicamentoDetalleDto(
    val id_med: Int,
    val nom_comercial: String,
    val laboratorio: String? = null,
    val iso_code: String,
    val nom_pais: String,
    val forma_farmaceutica: String? = null,
    val via_administracion: String? = null,
    val principios_activos: List<PrincipioActivoDto>,
    val codigos_atc: List<AtcDto>
)