package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.viewmodel.*
import esei.uvigo.es.tfg_donakyoin.*
import android.os.Bundle
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.databinding.DataBindingUtil
import esei.uvigo.es.tfg_donakyoin.databinding.BottomSheetFilterBinding
import androidx.fragment.app.activityViewModels
import androidx.core.view.children
import com.google.android.material.chip.Chip

class FilterBottomSheet : BottomSheetDialogFragment() {

    // Binding
    private var _binding: BottomSheetFilterBinding? = null
    private val binding get() = _binding!!

    // ViewModel
    private val viewModel: MedViewModel by activityViewModels()

    // onCreateView para FilterBottomSheet
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = DataBindingUtil.inflate(inflater, R.layout.bottom_sheet_filter, container, false)
        return binding.root
    }

    // onViewCreated para el binding de los Filtros
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Chips de Países desde el ViewModel
        (viewModel.paises.value ?: emptyList()).forEach { pais ->
            val chip = Chip(requireContext()).apply {
                text = pais.nom_pais
                isCheckable = true
                isChecked = pais.iso_code in viewModel.paisesActivo
                tag = pais.iso_code
            }
            binding.chipGroupPaisesFiltro.addView(chip)
        }

        // Pre-rellenar campos de texto desde el ViewModel
        binding.etForma.setText(viewModel.formaActiva)
        binding.etVia.setText(viewModel.viaActiva)
        binding.etLaboratorio.setText(viewModel.laboratorioActivo)

        // Limpiar todos los filtros
        binding.btnLimpiar.setOnClickListener {
            binding.chipGroupPaisesFiltro.children
                .filterIsInstance<Chip>()
                .forEach { it.isChecked = false }
            binding.etForma.text?.clear()
            binding.etVia.text?.clear()
            binding.etLaboratorio.text?.clear()
        }

        // Aplicar filtros: Guarda en el ViewModel y re-busca
        binding.btnAplicar.setOnClickListener {
            viewModel.paisesActivo = binding.chipGroupPaisesFiltro.children
                .filterIsInstance<Chip>()
                .filter { it.isChecked }
                .map { it.tag as String }
                .toList()
            viewModel.formaActiva = binding.etForma.text?.toString()?.trim()?.takeIf { it.isNotEmpty() }
            viewModel.viaActiva = binding.etVia.text?.toString()?.trim()?.takeIf { it.isNotEmpty() }
            viewModel.laboratorioActivo = binding.etLaboratorio.text?.toString()?.trim()?.takeIf { it.isNotEmpty() }
            viewModel.busquedaFiltro()
            dismiss()
        }
    }

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

}