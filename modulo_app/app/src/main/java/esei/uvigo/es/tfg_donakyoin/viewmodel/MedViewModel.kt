package esei.uvigo.es.tfg_donakyoin.viewmodel
import esei.uvigo.es.tfg_donakyoin.R
import esei.uvigo.es.tfg_donakyoin.database.MedDb
import esei.uvigo.es.tfg_donakyoin.models.*
import esei.uvigo.es.tfg_donakyoin.network.RetrofitClient
import esei.uvigo.es.tfg_donakyoin.repository.MedRepository
import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

class MedViewModel(app: Application) : AndroidViewModel(app) {

    // MedRepository
    private val repository : MedRepository

    // Inicializador de Repositorio y Filtros
    init {
        val api = RetrofitClient.apiService
        val dao = MedDb.getInstance(app).medDao()
        repository = MedRepository(api, dao)
        cargarFiltros()
    }

    /* -- LiveData de Atributos -- */
    // Medicamentos
    private val _medicamentos = MutableLiveData<List<MedicamentoDto>>()
    val medicamentos: LiveData<List<MedicamentoDto>> = _medicamentos

    // Paises
    private val _paises = MutableLiveData<List<PaisDto>>()
    val paises: LiveData<List<PaisDto>> = _paises

    // Formas Farmacéuticas
    private val _formas = MutableLiveData<List<FormaFarmaceuticaDto>>()
    val formas: LiveData<List<FormaFarmaceuticaDto>> = _formas

    // Vías de Administración
    private val _vias = MutableLiveData<List<ViaAdministracionDto>>()
    val vias: LiveData<List<ViaAdministracionDto>> = _vias

    // Detalle de Medicamento
    private val _detalle = MutableLiveData<MedicamentoDetalleDto?>()
    val detalle: LiveData<MedicamentoDetalleDto?> = _detalle

    // Indicador de filtros activos
    private val _filtrosActivos = MutableLiveData(false)
    val filtrosActivos: LiveData<Boolean> = _filtrosActivos

    // Equivalencias de Medicamento
    private val _equivalencias = MutableLiveData<EquivalenciaDto?>()
    val equivalencias: LiveData<EquivalenciaDto?> = _equivalencias

    // Estado de Carga
    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    // Estado de Carga en Equivalencias
    private val _isLoadingEquiv = MutableLiveData(false)
    val isLoadingEquiv: LiveData<Boolean> = _isLoadingEquiv

    // Error
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    // Error - Equivalencias
    private val _errorEquiv = MutableLiveData<String?>()
    val errorEquiv: LiveData<String?> = _errorEquiv

    // Medicamentos Guardados
    private val _medicamentosGuardados = MutableLiveData<List<MedicamentoDto>>()
    val medicamentosGuardados: LiveData<List<MedicamentoDto>> = _medicamentosGuardados

    // Estado de Guardado
    private val _isSaved = MutableLiveData(false)
    val isSaved: LiveData<Boolean> = _isSaved

    // Mostrar Detalles del Medicamento
    fun cargarDetalle(idMed: Int) {
        viewModelScope.launch {
            _detalle.value = null
            _isLoading.value = true
            _error.value = null
            repository.getDetalleMedicamento(idMed)
                .onSuccess { _detalle.value = it }
                .onFailure {
                    val local = repository.getDetalleGuardado(idMed)
                    if (local != null) _detalle.value = local
                    else _error.value = mapError(it)
                }
            _isLoading.value = false
        }
    }

    // Cargar Detalle desde Local
    fun cargarDetalleLocal(idMed: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            val local = repository.getDetalleGuardado(idMed)
            if (local != null) _detalle.value = local
            _isLoading.value = false
        }
    }

    // Comprobar si el Medicamento está Guardado
    fun checkSaved(idMed: Int) {
        viewModelScope.launch {
            _isSaved.value = repository.isMedSaved(idMed)
        }
    }

    // Guardar Medicamento en Local
    fun guardarMed() {
        val detalle = _detalle.value ?: return
        viewModelScope.launch {
            val med = MedicamentoDto(
                id_med = detalle.id_med,
                nom_comercial = detalle.nom_comercial,
                laboratorio = detalle.laboratorio,
                iso_code = detalle.iso_code,
                nom_pais = detalle.nom_pais,
                forma_farmaceutica = detalle.forma_farmaceutica,
                via_administracion = detalle.via_administracion
            )
            repository.guardarMedicamento(med, detalle)
            _isSaved.value = true
            cargarGuardados()
        }
    }

    // Eliminar Medicamento de Local
    fun eliminarMed(idMed: Int) {
        viewModelScope.launch {
            repository.eliminarMedicamento(idMed)
            _isSaved.value = false
            cargarGuardados()
        }
    }

    // Cargar Medicamentos Guardados
    fun cargarGuardados() {
        viewModelScope.launch {
            _medicamentosGuardados.value = repository.getMedGuardado()
        }
    }

    // Filtros de Búsqueda
    var ultimaQuery: String = ""
    var ultimoModo: String = "todo"
    var paisesActivo: List<String> = emptyList()
    var formaActiva: String? = null
    var viaActiva: String? = null
    var laboratorioActivo: String? = null

    // Búsqueda de Medicamentos
    fun buscarMedicamentos(
        q: String,
        modo: String = "todo"
    ) {
        ultimaQuery = q
        ultimoModo = modo
        busquedaFiltro()
    }

    // Búsqueda con Filtrado Avanzado
    fun busquedaFiltro() {
        _filtrosActivos.value = paisesActivo.isNotEmpty() || formaActiva != null || viaActiva != null || laboratorioActivo != null
        if (ultimaQuery.isEmpty()) return
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            repository.buscarMedicamentos(
                ultimaQuery,
                ultimoModo,
                paisesActivo.takeIf { it.isNotEmpty() },
                formaActiva,
                viaActiva,
                laboratorioActivo
            )
                .onSuccess { _medicamentos.value = it }
                .onFailure { _error.value = mapError(it) }
            _isLoading.value = false
        }
    }

    // Limpia los resultados de búsqueda
    fun limpiarBusqueda() {
        _medicamentos.value = emptyList()
        ultimaQuery = ""
        _error.value = null
    }

    // Carga de Equivalencias de un Medicamento
    fun cargarEquivalencias(idMed: Int) {
        viewModelScope.launch {
            _equivalencias.value = null
            _errorEquiv.value = null
            _isLoadingEquiv.value = true
            repository.getEquivalencias(idMed)
                .onSuccess { _equivalencias.value = it }
                .onFailure { _errorEquiv.value = mapError(it) }
            _isLoadingEquiv.value = false
        }
    }

    // Carga de filtros de búsqueda
    private fun cargarFiltros() {
        viewModelScope.launch {
            repository.getPaises().onSuccess { _paises.value = it }
            repository.getFormasFarmaceuticas().onSuccess { _formas.value = it }
            repository.getViasAdministracion().onSuccess { _vias.value = it }
        }
    }

    // Mapeo de Errores
    private fun mapError(e: Throwable): String = when (e) {
        is UnknownHostException  -> getApplication<Application>().getString(R.string.error_sin_conexion)
        is SocketTimeoutException -> getApplication<Application>().getString(R.string.error_timeout)
        is HttpException          -> getApplication<Application>().getString(R.string.error_servidor)
        else                      -> getApplication<Application>().getString(R.string.error_generico)
    }

}