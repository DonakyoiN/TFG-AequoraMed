package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.databinding.FragmentLocalDetailBinding
import esei.uvigo.es.tfg_donakyoin.models.MedicamentoDetalleDto
import esei.uvigo.es.tfg_donakyoin.viewmodel.MedViewModel
import esei.uvigo.es.tfg_donakyoin.*
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.view.isVisible
import androidx.databinding.DataBindingUtil
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.navArgs
import com.google.android.material.chip.Chip
import esei.uvigo.es.tfg_donakyoin.utils.*

class LocalDetailFragment : Fragment() {

    // Binding
    private var _binding: FragmentLocalDetailBinding? = null
    private val binding get() = _binding!!
    // ViewModel
    private val viewModel: MedViewModel by activityViewModels()
    // SafeArgs
    private val args: LocalDetailFragmentArgs by navArgs()

    // onCreateView para LocalDetailFragment
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = DataBindingUtil.inflate(inflater, R.layout.fragment_local_detail, container, false)
        return binding.root
    }

    // onViewCreated para el binding con la información del Detalle Local
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.cargarDetalleLocal(args.idMed)

        viewModel.isLoading.observe(viewLifecycleOwner) { loading ->
            binding.progressDetail.visibility = if (loading) View.VISIBLE else View.GONE
        }

        viewModel.detalle.observe(viewLifecycleOwner) { detalle ->
            if (detalle != null) {
                mostrarDetalles(detalle)
                binding.scrollContent.visibility = View.VISIBLE
            }
        }
    }

    // Mostrar la información del Medicamento guardado
    private fun mostrarDetalles(detalle: MedicamentoDetalleDto) {
        binding.detalle = detalle
        binding.executePendingBindings()

        // Registro: Ocultar si es Portugal
        binding.rowRegPais.isVisible = detalle.iso_code != "PT"
        binding.textLabelRegPais.text = registroLabelFor(detalle.iso_code)
        binding.textRegPais.text = detalle.reg_pais

        // Dosaje: Ocultar si es null
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

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
