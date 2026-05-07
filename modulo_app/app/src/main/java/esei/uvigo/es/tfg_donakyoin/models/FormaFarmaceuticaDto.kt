package esei.uvigo.es.tfg_donakyoin.models
import com.squareup.moshi.JsonClass

// Modelo de Forma Farmacéutica
@JsonClass(generateAdapter = true)
data class FormaFarmaceuticaDto(
    val id_forma: Int,
    val descripcion: String
)
