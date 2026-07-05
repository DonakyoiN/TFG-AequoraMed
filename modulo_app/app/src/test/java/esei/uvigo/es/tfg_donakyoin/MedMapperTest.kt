package esei.uvigo.es.tfg_donakyoin
import esei.uvigo.es.tfg_donakyoin.entities.MedEntity
import esei.uvigo.es.tfg_donakyoin.models.AtcDto
import esei.uvigo.es.tfg_donakyoin.models.MedicamentoDetalleDto
import esei.uvigo.es.tfg_donakyoin.models.MedicamentoDto
import esei.uvigo.es.tfg_donakyoin.models.PrincipioActivoDto
import esei.uvigo.es.tfg_donakyoin.utils.MedMapper
import org.junit.Assert.assertEquals
import org.junit.Test

class MedMapperTest {

    // DTO de ejemplo: Nurofen (ES)
    private val sampleDto = MedicamentoDto(
        id_med        = 1,
        nom_comercial = "Nurofen",
        laboratorio   = "Reckitt",
        iso_code      = "ES",
        nom_pais      = "España",
        forma_farmaceutica  = "Comprimido Recubierto",
        via_administracion  = "Vía Oral"
    )

    // Entity equivalente con savedAt fijo para comparaciones
    private val sampleEntity = MedEntity(
        id_med        = 1,
        nom_comercial = "Nurofen",
        laboratorio   = "Reckitt",
        iso_code      = "ES",
        nom_pais      = "España",
        forma_farmaceutica  = "Comprimido Recubierto",
        via_administracion  = "Vía Oral",
        savedAt       = 0L
    )

    // Mapea MedicamentoDto a MedEntity y verifica que todos los campos se conservan
    @Test
    fun test_toMedEntity() {
        val entity = MedMapper.toMedEntity(sampleDto)
        assertEquals(sampleDto.id_med,             entity.id_med)
        assertEquals(sampleDto.nom_comercial,       entity.nom_comercial)
        assertEquals(sampleDto.laboratorio,         entity.laboratorio)
        assertEquals(sampleDto.iso_code,            entity.iso_code)
        assertEquals(sampleDto.nom_pais,            entity.nom_pais)
        assertEquals(sampleDto.forma_farmaceutica,  entity.forma_farmaceutica)
        assertEquals(sampleDto.via_administracion,  entity.via_administracion)
    }

    // Mapea MedEntity a MedicamentoDto y verifica que todos los campos se conservan
    @Test
    fun test_toMedDto() {
        val dto = MedMapper.toMedDto(sampleEntity)
        assertEquals(sampleEntity.id_med,             dto.id_med)
        assertEquals(sampleEntity.nom_comercial,      dto.nom_comercial)
        assertEquals(sampleEntity.laboratorio,        dto.laboratorio)
        assertEquals(sampleEntity.iso_code,           dto.iso_code)
        assertEquals(sampleEntity.nom_pais,           dto.nom_pais)
        assertEquals(sampleEntity.forma_farmaceutica, dto.forma_farmaceutica)
        assertEquals(sampleEntity.via_administracion, dto.via_administracion)
    }

    // Convierte MedicamentoDto a MedEntity y de regreso a MedicamentoDto para verificar que se preservan todos los campos
    @Test
    fun test_mapping_MedDto() {
        val restored = MedMapper.toMedDto(MedMapper.toMedEntity(sampleDto))
        assertEquals(sampleDto.id_med,             restored.id_med)
        assertEquals(sampleDto.nom_comercial,      restored.nom_comercial)
        assertEquals(sampleDto.iso_code,           restored.iso_code)
        assertEquals(sampleDto.laboratorio,        restored.laboratorio)
        assertEquals(sampleDto.forma_farmaceutica, restored.forma_farmaceutica)
        assertEquals(sampleDto.via_administracion, restored.via_administracion)
    }

    // Convierte MedicamentoDetalleDto a MedDetailEntity y de regreso a MedicamentoDetalleDto para verificar la serialización Moshi de PAs y ATCs
    @Test
    fun test_mapping_MedDetailDto() {
        val detalleDto = MedicamentoDetalleDto(
            id_med        = 2,
            nom_comercial = "Augmentine",
            reg_pais      = "ES/123",
            laboratorio   = "GSK",
            iso_code      = "ES",
            nom_pais      = "España",
            forma_farmaceutica = "Comprimido recubierto",
            via_administracion = "Oral",
            dosaje        = "875/125 mg",
            principios_activos = listOf(
                PrincipioActivoDto(id_pa = 10, nom_estandar = "Amoxicilina"),
                PrincipioActivoDto(id_pa = 11, nom_estandar = "Ácido Clavulánico")
            ),
            codigos_atc = listOf(
                AtcDto(id_atc = 5, code_atc = "J01CR02", desc_es = "Amoxicilina y enzimas", desc_en = "Amoxicillin and enzyme inhibitor")
            )
        )

        val entity   = MedMapper.toDetailEntity(detalleDto)
        val restored = MedMapper.toDetailDto(entity)

        assertEquals(detalleDto.id_med,        restored.id_med)
        assertEquals(detalleDto.nom_comercial, restored.nom_comercial)
        assertEquals(detalleDto.dosaje,        restored.dosaje)
        assertEquals(detalleDto.reg_pais,      restored.reg_pais)

        // PAs conservados tras serializar/deserializar JSON
        assertEquals(2, restored.principios_activos.size)
        assertEquals("Amoxicilina",       restored.principios_activos[0].nom_estandar)
        assertEquals("Ácido Clavulánico", restored.principios_activos[1].nom_estandar)

        // ATCs conservados tras serializar/deserializar JSON
        assertEquals(1, restored.codigos_atc.size)
        assertEquals("J01CR02", restored.codigos_atc[0].code_atc)
    }
}
