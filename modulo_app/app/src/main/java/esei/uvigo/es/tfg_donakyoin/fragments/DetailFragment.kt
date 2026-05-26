package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.databinding.FragmentDetailBinding
import esei.uvigo.es.tfg_donakyoin.models.MedicamentoDetalleDto
import esei.uvigo.es.tfg_donakyoin.viewmodel.MedViewModel
import esei.uvigo.es.tfg_donakyoin.*
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.databinding.DataBindingUtil
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import androidx.core.view.isVisible
import com.google.android.material.chip.Chip

class DetailFragment : Fragment() {

    // Binding
    private var _binding: FragmentDetailBinding? = null
    private val binding get() = _binding!!
    // ViewModel
    private val viewModel: MedViewModel by activityViewModels()
    // SafeArgs
    private val args: DetailFragmentArgs by navArgs()

    // onCreateView para DetailFragment
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = DataBindingUtil.inflate(inflater, R.layout.fragment_detail, container, false)
        return binding.root
    }

    // onViewCreated para el binding con la información de los Detalles
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.cargarDetalle(args.idMed)

        viewModel.isLoading.observe(viewLifecycleOwner) { loading ->
            binding.progressDetail.visibility = if (loading) View.VISIBLE else View.GONE
        }

        viewModel.detalle.observe(viewLifecycleOwner) { detalle ->
            if (detalle != null) {
                mostrarDetalles(detalle)
                binding.scrollContent.visibility = View.VISIBLE
            }
        }

        // Botón de Equivalencias Farmacéuticas
        binding.btnEquivalencias.setOnClickListener {
            findNavController().navigate(
                DetailFragmentDirections.actionDetailFragmentToEquivalenciasBottomSheet(args.idMed)
            )
        }
    }

    // Mostrar la información del Medicamento seleccionado
    private fun mostrarDetalles(detalle: MedicamentoDetalleDto) {
        binding.detalle = detalle
        binding.executePendingBindings()

        // Registro: Ocultar si es Portugal (id_pt != registro)
        binding.rowRegPais.isVisible = detalle.iso_code != "PT"
        binding.textLabelRegPais.text = registroLabelFor(detalle.iso_code)
        binding.textRegPais.text = detalle.reg_pais

        // Dosaje: Ocultar si es null (CL + algunos med sin dosis)
        binding.rowDosaje.isVisible = detalle.dosaje != null
        binding.textDosaje.text = detalle.dosaje

        // Bandera
        val flagRes = flagResFor(detalle.iso_code)
        if (flagRes != null) binding.ivBanderaDetalle.setImageResource(flagRes)

        // Código ATC
        binding.llAtcContainer.removeAllViews()
        if (detalle.codigos_atc.isNotEmpty()) {

            binding.dividerAtc.visibility = View.VISIBLE
            binding.sectionAtc.visibility = View.VISIBLE

            val bottomMargin = (6 * resources.displayMetrics.density).toInt()

            detalle.codigos_atc.forEach { atc ->
                val tv = TextView(requireContext())
                val desc = atc.desc_es ?: atc.desc_en
                tv.text = if (desc != null) "${atc.code_atc}  ·  $desc" else atc.code_atc
                val lp = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
                lp.bottomMargin = bottomMargin
                tv.layoutParams = lp
                binding.llAtcContainer.addView(tv)
            }
        }

        // Principios Activos
        binding.chipGroupPrincipios.removeAllViews()
        if (detalle.principios_activos.isNotEmpty()) {

            binding.dividerPrincipios.visibility = View.VISIBLE
            binding.sectionPrincipios.visibility = View.VISIBLE

            detalle.principios_activos.forEach { pa ->
                val chip = Chip(requireContext())
                chip.text = pa.nom_estandar
                chip.isClickable = false
                chip.isFocusable = false
                binding.chipGroupPrincipios.addView(chip)
            }
        }
    }

    // Determinar nombre para Registro de Medicamento según País
    private fun registroLabelFor(isoCode: String): String = when (isoCode.uppercase()) {
        "CA" -> "Drug Identification Number (DIN)"
        "US" -> "Application Number"
        else -> "Nº de Registro"
    }

    // Asignación de Banderas según ISO
    private fun flagResFor(isoCode: String): Int? = when (isoCode.uppercase()) {
        "ES" -> R.drawable.ic_spain
        "CL" -> R.drawable.ic_chile
        "PT" -> R.drawable.ic_portugal
        "US" -> R.drawable.ic_usa
        "CA" -> R.drawable.ic_canada
        else -> null
    }

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
