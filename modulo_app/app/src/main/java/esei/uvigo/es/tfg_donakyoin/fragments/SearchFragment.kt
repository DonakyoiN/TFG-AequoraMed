package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.adapters.MedAdapter
import esei.uvigo.es.tfg_donakyoin.databinding.FragmentSearchBinding
import esei.uvigo.es.tfg_donakyoin.viewmodel.*
import esei.uvigo.es.tfg_donakyoin.*
import esei.uvigo.es.tfg_donakyoin.utils.RecentSearchManager
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.view.isVisible
import androidx.databinding.DataBindingUtil
import android.view.inputmethod.EditorInfo
import android.widget.ImageView
import android.widget.TextView
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.search.SearchView

class SearchFragment : Fragment() {

    // Binding
    private var _binding: FragmentSearchBinding? = null
    private val binding get() = _binding!!
    // ViewModel
    private val viewModel: MedViewModel by activityViewModels()
    // Adapter
    private lateinit var adapter: MedAdapter
    // Búsquedas Recientes
    private lateinit var recentSearches: RecentSearchManager

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

        // Inicialización de Búsquedas Recientes
        recentSearches = RecentSearchManager(requireContext())

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
        // Filtros
        setupFiltrado()
        // Búsquedas Recientes
        setupBusquedasRecientes()

        // Observer de los Medicamentos por ViewModel
        viewModel.medicamentos.observe(viewLifecycleOwner) { meds ->
            adapter.submitList(meds)
            if (meds.isEmpty()) mostrarEstado(getString(R.string.search_no_results))
            else mostrarLista()
        }

        // Observer de Errores
        viewModel.error.observe(viewLifecycleOwner) { error ->
            if (error != null) mostrarEstado("Error: $error")
        }

        if (viewModel.medicamentos.value == null) {
            mostrarEstado(getString(R.string.search_placeholder))
        }
    }

    // Layout de la búsqueda
    private fun setupBusqueda() {
        binding.searchView.setupWithSearchBar(binding.searchBar)
        binding.searchView.editText.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                binding.searchBar.setText(binding.searchView.text)
                binding.searchView.hide()
                buscar()
                true
            } else false
        }
    }

    // Layout del filtrado
    private fun setupFiltrado() {
        binding.searchBar.setOnMenuItemClickListener { item ->
            if (item.itemId == R.id.action_filter) {
                findNavController().navigate(R.id.action_searchFragment_to_filterBottomSheet)
                true
            } else false
        }
    }

    // Búsquedas Recientes
    private fun setupBusquedasRecientes() {
        binding.searchView.addTransitionListener { _, _, newState ->
            if (newState == SearchView.TransitionState.SHOWN) {
                refreshBusquedasRecientes()
            }
        }
    }

    // Reconstruye la lista de búsquedas recientes
    private fun refreshBusquedasRecientes() {
        val searches = recentSearches.getSearches()
        binding.llRecientes.isVisible = searches.isNotEmpty()
        binding.llRecientesItems.removeAllViews()
        searches.forEach { query ->
            val item = layoutInflater.inflate(R.layout.item_recent_search, binding.llRecientesItems, false)
            item.findViewById<TextView>(R.id.tv_query).text = query
            item.setOnClickListener {
                binding.searchBar.setText(query)
                binding.searchView.hide()
                recentSearches.addSearch(query)
                viewModel.buscarMedicamentos(q = query, modo = getModoSeleccionado())
            }
            item.findViewById<ImageView>(R.id.btn_eliminar).setOnClickListener {
                recentSearches.removeSearch(query)
                refreshBusquedasRecientes()
            }
            binding.llRecientesItems.addView(item)
        }
    }

    // Búsqueda de Medicamentos
    private fun buscar() {
        val q = binding.searchBar.text?.toString()?.trim() ?: return
        if (q.isEmpty()) return
        recentSearches.addSearch(q)
        viewModel.buscarMedicamentos(q = q, modo = getModoSeleccionado())
    }

    // Selección de Tipo de Búsqueda
    private fun getModoSeleccionado(): String = when (binding.chipGroupModo.checkedChipId) {
        R.id.chip_nombre -> "nombre"
        R.id.chip_atc -> "atc"
        R.id.chip_principio_activo -> "principio_activo"
        R.id.chip_registro -> "registro"
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
