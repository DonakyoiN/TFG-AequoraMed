package esei.uvigo.es.tfg_donakyoin.utils
import com.squareup.moshi.Moshi
import com.squareup.moshi.Types
import esei.uvigo.es.tfg_donakyoin.entities.*
import esei.uvigo.es.tfg_donakyoin.models.*

object MedMapper {
    private val moshi = Moshi.Builder().build()

    // Adaptador para Entity de los Principios Activos
    private val principiosAdapter = moshi.adapter<List<PrincipioActivoDto>>(
        Types.newParameterizedType(List::class.java, PrincipioActivoDto::class.java)
    )

    // Adaptador para Entity de los códigos ATC
    private val atcAdapter = moshi.adapter<List<AtcDto>>(
        Types.newParameterizedType(List::class.java, AtcDto::class.java)
    )

    // MedEntity → MedicamentoDto
    fun toMedDto(entity: MedEntity): MedicamentoDto {
        return MedicamentoDto(
            id_med = entity.id_med,
            nom_comercial = entity.nom_comercial,
            laboratorio = entity.laboratorio,
            iso_code = entity.iso_code,
            nom_pais = entity.nom_pais,
            forma_farmaceutica = entity.forma_farmaceutica,
            via_administracion = entity.via_administracion
        )
    }

    // MedicamentoDto → MedEntity
    fun toMedEntity(dto: MedicamentoDto): MedEntity {
        return MedEntity(
            id_med = dto.id_med,
            nom_comercial = dto.nom_comercial,
            laboratorio = dto.laboratorio,
            iso_code = dto.iso_code,
            nom_pais = dto.nom_pais,
            forma_farmaceutica = dto.forma_farmaceutica,
            via_administracion = dto.via_administracion
        )
    }

    // MedDetailEntity → MedicamentoDetalleDto
    fun toDetailDto(entity: MedDetailEntity): MedicamentoDetalleDto {
        return MedicamentoDetalleDto(
            id_med = entity.id_med,
            nom_comercial = entity.nom_comercial,
            reg_pais = entity.reg_pais,
            laboratorio = entity.laboratorio,
            iso_code = entity.iso_code,
            nom_pais = entity.nom_pais,
            forma_farmaceutica = entity.forma_farmaceutica,
            via_administracion = entity.via_administracion,
            dosaje = entity.dosaje,
            principios_activos = principiosAdapter.fromJson(entity.principios_activos) ?: emptyList(),
            codigos_atc = atcAdapter.fromJson(entity.codigos_atc) ?: emptyList()
        )

    }

    // MedicamentoDetalleDto → MedDetailEntity
    fun toDetailEntity(dto: MedicamentoDetalleDto): MedDetailEntity {
        return MedDetailEntity(
            id_med = dto.id_med,
            nom_comercial = dto.nom_comercial,
            reg_pais = dto.reg_pais,
            laboratorio = dto.laboratorio,
            iso_code = dto.iso_code,
            nom_pais = dto.nom_pais,
            forma_farmaceutica = dto.forma_farmaceutica,
            via_administracion = dto.via_administracion,
            dosaje = dto.dosaje,
            principios_activos = principiosAdapter.toJson(dto.principios_activos),
            codigos_atc = atcAdapter.toJson(dto.codigos_atc)
        )
    }
}
