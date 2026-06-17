package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.adapters.EquivalenciaAdapter
import esei.uvigo.es.tfg_donakyoin.databinding.BottomSheetEquivalenciasBinding
import esei.uvigo.es.tfg_donakyoin.models.EquivalenciaResumenDto
import esei.uvigo.es.tfg_donakyoin.viewmodel.*
import esei.uvigo.es.tfg_donakyoin.*
import esei.uvigo.es.tfg_donakyoin.utils.paisResIdFor
import android.os.Bundle
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.databinding.DataBindingUtil
import androidx.core.view.isVisible
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.navArgs
import androidx.navigation.fragment.findNavController
import com.google.android.material.chip.Chip

class EquivalenciasBottomSheet : BottomSheetDialogFragment() {

    // SafeArgs de EquivalenciasBottomSheet
    private val args: EquivalenciasBottomSheetArgs by navArgs()
    // Binding
    private var _binding: BottomSheetEquivalenciasBinding? = null
    private val binding get() = _binding!!
    // ViewModel
    private val viewModel: MedViewModel by activityViewModels()
    // Adapter
    private lateinit var adapter: EquivalenciaAdapter

    // onCreateView para EquivalenciasBottomSheet
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = DataBindingUtil.inflate(inflater, R.layout.bottom_sheet_equivalencias, container, false)
        return binding.root
    }

    // onViewCreated para el binding con las Equivalencias
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Inicialización de Adapter
        adapter = EquivalenciaAdapter { med ->
            findNavController().navigate(
                EquivalenciasBottomSheetDirections.actionEquivalenciasBottomSheetToDetailFragment(med.id_med)
            )
        }

        // RecyclerView
        binding.rvEquivalencias.adapter = adapter

        // Carga de Equivalencias
        viewModel.cargarEquivalencias(args.idMed)

        // Observer de Carga
        viewModel.isLoadingEquiv.observe(viewLifecycleOwner) { loading ->
            binding.progressEquivalencias.isVisible = loading
        }

        // Observer de Equivalencias
        viewModel.equivalencias.observe(viewLifecycleOwner) { equiv ->
            if (equiv == null) return@observe
            val todos = equiv.por_atc.map { it.copy(tipo_equivalencia = getString(R.string.equiv_tipo_atc)) } +
                        equiv.por_principio_activo.map { it.copy(tipo_equivalencia = getString(R.string.equiv_tipo_principio)) }
            if (todos.isEmpty()) {
                binding.tvEmpty.text = getString(R.string.equiv_vacio)
                binding.tvEmpty.isVisible = true
                binding.rvEquivalencias.isVisible = false
            } else {
                configurarChips(todos)
                mostrarSeleccionPais()
            }
        }
    }

    // Configuración de Chips de Países
    private fun configurarChips(lista: List<EquivalenciaResumenDto>) {
        val paises = lista.map { it.iso_code to (paisResIdFor(it.iso_code)?.let { id -> getString(id) } ?: it.nom_pais) }.distinctBy { it.first }
        binding.chipGroupPaises.removeAllViews()

        paises.forEach { (iso, nombre) ->
            val chip = Chip(requireContext()).apply {
                text = nombre
                isCheckable = true
                tag = iso
            }
            chip.setOnCheckedChangeListener { _, _ -> filtrarPorPais() }
            binding.chipGroupPaises.addView(chip)
        }
    }

    // Filtrado de Equivalencias por País
    private fun filtrarPorPais() {
        val seleccionados = (0 until binding.chipGroupPaises.childCount)
            .map { binding.chipGroupPaises.getChildAt(it) as Chip }
            .filter { it.isChecked }
            .map { it.tag as String }

        if (seleccionados.isEmpty()) {
            mostrarSeleccionPais()
            return
        }

        val todos = viewModel.equivalencias.value?.let {
            it.por_atc.map { med -> med.copy(tipo_equivalencia = getString(R.string.equiv_tipo_atc)) } +
            it.por_principio_activo.map { med -> med.copy(tipo_equivalencia = getString(R.string.equiv_tipo_principio)) }
        } ?: return

        val filtrados = todos.filter { it.iso_code in seleccionados }
        binding.tvEmpty.text = getString(R.string.equiv_vacio)
        binding.tvEmpty.isVisible = filtrados.isEmpty()
        binding.rvEquivalencias.isVisible = filtrados.isNotEmpty()
        adapter.submitList(filtrados)
    }

    // Estado inicial: Ningún país seleccionado
    private fun mostrarSeleccionPais() {
        binding.tvEmpty.text = getString(R.string.equiv_selecciona_pais)
        binding.tvEmpty.isVisible = true
        binding.rvEquivalencias.isVisible = false
        adapter.submitList(emptyList())
    }

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
