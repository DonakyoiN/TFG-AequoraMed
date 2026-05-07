package esei.uvigo.es.tfg_donakyoin.network
import esei.uvigo.es.tfg_donakyoin.models.*
import retrofit2.http.GET
import retrofit2.http.Query

// Interfaz definiendo los endpoints de la API
interface ApiService {
    @GET("paises")
    suspend fun getPaises(): List<PaisDto>
    @GET("formas_farmaceuticas")
    suspend fun getFormasFarmaceuticas(): List<FormaFarmaceuticaDto>
    @GET("vias_administracion")
    suspend fun getViasAdministracion(): List<ViaAdministracionDto>
    @GET("medicamentos/buscar")
    suspend fun buscarMedicamentos(
        @Query("q") q: String,
        @Query("modo") modo: String = "todo",
        @Query("pais") pais: List<String>? = null,
        @Query("forma") forma: String? = null,
        @Query("via") via: String? = null,
        @Query("laboratorio") laboratorio: String? = null,
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0
    ): List<MedicamentoDto>

    @GET("medicamentos/id_med")
    suspend fun getDetalleMedicamento(
        @Query("id_med") idMed: Int
    ): MedicamentoDetalleDto

    @GET("equivalencias/id_med")
    suspend fun getEquivalencias(
        @Query("id_med") idMed: Int,
        @Query("pais") pais: List<String>? = null
    ): EquivalenciaDto
}