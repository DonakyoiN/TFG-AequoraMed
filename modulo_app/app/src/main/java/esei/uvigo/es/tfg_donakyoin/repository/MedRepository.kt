package esei.uvigo.es.tfg_donakyoin.repository
import esei.uvigo.es.tfg_donakyoin.network.*
import esei.uvigo.es.tfg_donakyoin.models.*

class MedRepository(private val api: ApiService) {

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
}
