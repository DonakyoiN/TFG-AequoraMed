package esei.uvigo.es.tfg_donakyoin.models
import com.squareup.moshi.JsonClass

// Modelo de Vía de Administración
@JsonClass(generateAdapter = true)
data class ViaAdministracionDto(
    val id_via: Int,
    val descripcion: String
)
