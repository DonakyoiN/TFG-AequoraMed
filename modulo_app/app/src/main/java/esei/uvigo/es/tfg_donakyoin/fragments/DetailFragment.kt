package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.databinding.FragmentDetailBinding
import esei.uvigo.es.tfg_donakyoin.models.MedicamentoDetalleDto
import esei.uvigo.es.tfg_donakyoin.viewmodel.MedViewModel
import esei.uvigo.es.tfg_donakyoin.*
import android.os.Bundle
import android.view.LayoutInflater
import android.view.Menu
import android.view.MenuInflater
import android.view.MenuItem
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.view.MenuProvider
import androidx.databinding.DataBindingUtil
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.Lifecycle
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import androidx.core.view.isVisible
import com.google.android.material.chip.Chip
import com.google.android.material.snackbar.Snackbar
import esei.uvigo.es.tfg_donakyoin.utils.*

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

        // Carga los detalles del Medicamento y verifica si está Guardado en local
        viewModel.cargarDetalle(args.idMed)
        viewModel.checkSaved(args.idMed)

        viewModel.isLoading.observe(viewLifecycleOwner) { loading ->
            val pb = binding.progressDetail
            pb.animate().cancel()
            if (loading) {
                pb.alpha = 0f
                pb.visibility = View.VISIBLE
                pb.animate().alpha(1f).setDuration(200).start()
            } else {
                pb.animate().alpha(0f).setDuration(200).withEndAction {
                    pb.visibility = View.GONE
                    pb.alpha = 1f
                }.start()
            }
        }

        viewModel.detalle.observe(viewLifecycleOwner) { detalle ->
            if (detalle != null) {
                mostrarDetalles(detalle)
                binding.scrollContent.visibility = View.VISIBLE
            }
        }

        viewModel.error.observe(viewLifecycleOwner) { error ->
            if (error != null) Snackbar.make(binding.root, error, Snackbar.LENGTH_LONG)
                .setAnchorView(requireActivity().findViewById(R.id.bottom_nav))
                .show()
        }

        setupToolbar()

        // FAB para Equivalencias Farmacéuticas
        binding.fabEquivalencias.setOnClickListener {
            findNavController().navigate(
                DetailFragmentDirections.actionDetailFragmentToEquivalenciasBottomSheet(args.idMed)
            )
        }
    }

    // Menú de Guardado
    private fun setupToolbar() {
        requireActivity().addMenuProvider(object : MenuProvider {
            override fun onCreateMenu(menu: Menu, menuInflater: MenuInflater) {
                menuInflater.inflate(R.menu.detail_bar, menu)
            }

            // Maneja estado de Guardado
            override fun onPrepareMenu(menu: Menu) {
                val saved = viewModel.isSaved.value == true
                menu.findItem(R.id.action_guardar)?.setIcon(
                    if (saved) R.drawable.ic_bookmark_saved else R.drawable.ic_bookmark_icon
                )
            }

            // Acción del Menú
            override fun onMenuItemSelected(menuItem: MenuItem): Boolean {
                return when (menuItem.itemId) {
                    R.id.action_guardar -> {
                        if (viewModel.isSaved.value == true) {
                            viewModel.eliminarMed(args.idMed)
                            Snackbar.make(binding.root, getString(R.string.snack_eliminado), 1000)
                                .setAnchorView(requireActivity().findViewById(R.id.bottom_nav))
                                .show()
                        } else {
                            viewModel.guardarMed()
                            Snackbar.make(binding.root, getString(R.string.snack_guardado), 1000)
                                .setAnchorView(requireActivity().findViewById(R.id.bottom_nav))
                                .show()
                        }
                        true
                    }
                    else -> false
                }
            }
        }, viewLifecycleOwner, Lifecycle.State.RESUMED)

        // Observer del estado de Guardado
        viewModel.isSaved.observe(viewLifecycleOwner) {
            requireActivity().invalidateMenu()
        }
    }

    // Mostrar la información del Medicamento seleccionado
    private fun mostrarDetalles(detalle: MedicamentoDetalleDto) {
        binding.detalle = detalle
        binding.executePendingBindings()

        // Registro: Ocultar si es Portugal (id_pt != registro)
        binding.rowRegPais.isVisible = detalle.iso_code != "PT"
        binding.textLabelRegPais.text = getString(registroResIdFor(detalle.iso_code))
        binding.textRegPais.text = detalle.reg_pais
        val paisResId = paisResIdFor(detalle.iso_code)
        if (paisResId != null) binding.textNomPais.text = getString(paisResId)

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

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
