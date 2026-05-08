package esei.uvigo.es.tfg_donakyoin.models
import com.squareup.moshi.JsonClass

// Modelo de Principio Activo
@JsonClass(generateAdapter = true)
data class PrincipioActivoDto(
    val id_pa: Int,
    val nom_estandar: String
)
