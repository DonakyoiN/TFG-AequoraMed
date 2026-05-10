package esei.uvigo.es.tfg_donakyoin.viewmodel
import esei.uvigo.es.tfg_donakyoin.models.*
import esei.uvigo.es.tfg_donakyoin.network.RetrofitClient
import esei.uvigo.es.tfg_donakyoin.repository.MedRepository
import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

class MedViewModel(app: Application) : AndroidViewModel(app) {

    // MedRepository
    private val repository : MedRepository

    // Inicializador de Repositorio y Filtros
    init {
        val api = RetrofitClient.apiService
        repository = MedRepository(api)
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

    // Estado de Carga
    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    // Error
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    // Mostrar Detalles del Medicamento
    fun cargarDetalle(idMed: Int) {
        viewModelScope.launch {
            _detalle.value = null
            _isLoading.value = true
            _error.value = null
            repository.getDetalleMedicamento(idMed)
                .onSuccess { _detalle.value = it }
                .onFailure { _error.value = it.message }
            _isLoading.value = false
        }
    }

    // Búsqueda de Medicamentos
    fun buscarMedicamentos(
        q: String,
        modo: String = "todo",
        paises: List<String>? = null,
        forma: String? = null,
        via: String? = null,
        laboratorio: String? = null
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            repository.buscarMedicamentos(q, modo, paises, forma, via, laboratorio)
                .onSuccess { _medicamentos.value = it }
                .onFailure { _error.value = it.message }
            _isLoading.value = false
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

}