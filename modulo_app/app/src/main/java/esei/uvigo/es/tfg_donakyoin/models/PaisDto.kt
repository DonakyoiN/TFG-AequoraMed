package esei.uvigo.es.tfg_donakyoin.models
import com.squareup.moshi.JsonClass

// Modelo de País
@JsonClass(generateAdapter = true)
data class PaisDto (
    val id_pais: Int,
    val iso_code: String,
    val nom_pais: String
)