package esei.uvigo.es.tfg_donakyoin.repository
import esei.uvigo.es.tfg_donakyoin.database.MedDao
import esei.uvigo.es.tfg_donakyoin.models.*
import esei.uvigo.es.tfg_donakyoin.network.*
import esei.uvigo.es.tfg_donakyoin.utils.MedMapper
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class MedRepository(
    private val api: ApiService,
    private val dao: MedDao
) {

    private val io:CoroutineDispatcher = Dispatchers.IO

    /* -- Retrofit -- */
    suspend fun buscarMedicamentos(
        q: String,
        modo: String = "todo",
        paises: List<String>? = null,
        forma: String? = null,
        via: String? = null,
        laboratorio: String? = null,
        limit: Int = 50,
        offset: Int = 0
    ): Result<List<MedicamentoDto>> = runCatching {
        api.buscarMedicamentos(q, modo, paises, forma, via, laboratorio, limit, offset)
    }

    suspend fun getDetalleMedicamento(idMed: Int): Result<MedicamentoDetalleDto> = runCatching {
        api.getDetalleMedicamento(idMed)
    }

    suspend fun getEquivalencias(
        idMed: Int,
        paises: List<String>? = null
    ): Result<EquivalenciaDto> = runCatching {
        api.getEquivalencias(idMed, paises)
    }

    suspend fun getPaises(): Result<List<PaisDto>> = runCatching {
        api.getPaises()
    }

    suspend fun getFormasFarmaceuticas(): Result<List<FormaFarmaceuticaDto>> = runCatching {
        api.getFormasFarmaceuticas()
    }

    suspend fun getViasAdministracion(): Result<List<ViaAdministracionDto>> = runCatching {
        api.getViasAdministracion()
    }

    /* -- Room -- */
    suspend fun guardarMedicamento(med: MedicamentoDto, detalle: MedicamentoDetalleDto) = withContext(io) {
        val medEntity = MedMapper.toMedEntity(med)
        val detailEntity = MedMapper.toDetailEntity(detalle)
        dao.saveMedicamento(medEntity, detailEntity)
    }

    suspend fun eliminarMedicamento(idMed: Int) = withContext(io) {
        val med = dao.getAllMeds().find { it.id_med == idMed } ?: return@withContext
        dao.deleteMedicamento(med)
    }

    suspend fun getMedGuardado(): List<MedicamentoDto> = withContext(io) {
        dao.getAllMeds().map { MedMapper.toMedDto(it) }
    }

    suspend fun isMedSaved(idMed: Int): Boolean = withContext(io) {
        dao.isMedSaved(idMed)
    }

    suspend fun getDetalleGuardado(idMed: Int): MedicamentoDetalleDto? = withContext(io) {
        dao.getDetail(idMed)?.let { MedMapper.toDetailDto(it) }
    }
}
