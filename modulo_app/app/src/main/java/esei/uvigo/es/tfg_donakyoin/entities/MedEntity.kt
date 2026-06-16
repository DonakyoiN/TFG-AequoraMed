package esei.uvigo.es.tfg_donakyoin.entities
import androidx.room.Entity
import androidx.room.PrimaryKey

// Medicamento Guardado
@Entity(tableName = "saved_med")
data class MedEntity(
    @PrimaryKey val id_med: Int,
    val nom_comercial: String,
    val laboratorio: String?,
    val iso_code: String,
    val nom_pais: String,
    val forma_farmaceutica: String?,
    val via_administracion: String?,
    val savedAt: Long = System.currentTimeMillis()
)

// Detalles de Medicamento Guardado
@Entity(tableName = "saved_detail")
data class MedDetailEntity(
    @PrimaryKey val id_med: Int,
    val nom_comercial: String,
    val reg_pais: String?,
    val laboratorio: String?,
    val iso_code: String,
    val nom_pais: String,
    val forma_farmaceutica: String?,
    val via_administracion: String?,
    val dosaje: String?,
    val principios_activos: String,
    val codigos_atc: String,
    val savedAt: Long = System.currentTimeMillis()
)