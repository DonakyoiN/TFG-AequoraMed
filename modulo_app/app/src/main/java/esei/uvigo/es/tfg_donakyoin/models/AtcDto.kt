package esei.uvigo.es.tfg_donakyoin.models
import com.squareup.moshi.JsonClass

// Modelo de Código ATC
@JsonClass(generateAdapter = true)
data class AtcDto(
    val id_atc: Int,
    val code_atc: String,
    val desc_es: String? = null,
    val desc_en: String? = null
)
