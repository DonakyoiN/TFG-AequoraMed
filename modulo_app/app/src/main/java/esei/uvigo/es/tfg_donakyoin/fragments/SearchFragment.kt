package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.adapters.MedAdapter
import esei.uvigo.es.tfg_donakyoin.databinding.FragmentSearchBinding
import esei.uvigo.es.tfg_donakyoin.viewmodel.*
import esei.uvigo.es.tfg_donakyoin.*
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.databinding.DataBindingUtil
import android.view.inputmethod.EditorInfo
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager

class SearchFragment : Fragment() {

    // Binding
    private var _binding: FragmentSearchBinding? = null
    private val binding get() = _binding!!
    // ViewModel
    private val viewModel: MedViewModel by activityViewModels()
    // Adapter
    private lateinit var adapter: MedAdapter

    // onCreateView para SearchFragment
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = DataBindingUtil.inflate(inflater, R.layout.fragment_search, container, false)
        return binding.root
    }

    // onViewCreated para el binding del RecyclerView
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Inicialización de Adapter
        adapter = MedAdapter { med ->
            // Navegación a Detalles
            val action = SearchFragmentDirections.actionSearchFragmentToDetailFragment(med.id_med)
            findNavController().navigate(action)
        }

        // DataBinding
        binding.viewModel = viewModel
        binding.lifecycleOwner = viewLifecycleOwner

        // RecyclerView
        binding.rvMedicamentos.layoutManager = LinearLayoutManager(requireContext())
        binding.rvMedicamentos.adapter = adapter

        // Búsqueda
        setupBusqueda()

        // Observer de los Medicamentos por ViewModel
        viewModel.medicamentos.observe(viewLifecycleOwner) { meds ->
            adapter.submitList(meds)
            if (meds.isEmpty()) mostrarEstado("Sin resultados")
            else mostrarLista()
        }

        // Observer de Errores
        viewModel.error.observe(viewLifecycleOwner) { error ->
            if (error != null) mostrarEstado("Error: $error")
        }

        if (viewModel.medicamentos.value == null) {
            mostrarEstado("Busca un medicamento para ver resultados")
        }
    }

    // Layout de la búsqueda
    private fun setupBusqueda() {
        binding.etBusqueda.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                buscar()
                true
            } else false
        }
    }

    // Búsqueda de Medicamentos
    private fun buscar() {
        val q = binding.etBusqueda.text?.toString()?.trim() ?: return
        if (q.isEmpty()) return
        viewModel.buscarMedicamentos(q = q, modo = getModoSeleccionado())
    }

    // Selección de Tipo de Búsqueda
    private fun getModoSeleccionado(): String = when (binding.chipGroupModo.checkedChipId) {
        R.id.chip_nombre -> "nombre"
        R.id.chip_atc -> "atc"
        R.id.chip_principio_activo -> "principio_activo"
        else -> "todo"
    }

    // Mostrar Lista según el Estado
    private fun mostrarLista() {
        binding.rvMedicamentos.visibility = View.VISIBLE
        binding.tvEstado.visibility = View.GONE
    }

    // Manejo de Visibilidad según el Estado
    private fun mostrarEstado(mensaje: String) {
        binding.tvEstado.text = mensaje
        binding.tvEstado.visibility = View.VISIBLE
        binding.rvMedicamentos.visibility = View.GONE
    }

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
