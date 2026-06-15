package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.adapters.MedAdapter
import esei.uvigo.es.tfg_donakyoin.databinding.FragmentSavedBinding
import esei.uvigo.es.tfg_donakyoin.viewmodel.MedViewModel
import esei.uvigo.es.tfg_donakyoin.*
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.databinding.DataBindingUtil
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager

class SavedFragment : Fragment() {

    // Binding
    private var _binding: FragmentSavedBinding? = null
    private val binding get() = _binding!!
    // ViewModel
    private val viewModel: MedViewModel by activityViewModels()
    // Adapter
    private lateinit var adapter: MedAdapter

    // onCreateView para SavedFragment
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = DataBindingUtil.inflate(inflater, R.layout.fragment_saved, container, false)
        return binding.root
    }

    // onViewCreated para el binding del RecyclerView
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = MedAdapter { med ->
            val action = SavedFragmentDirections.actionSavedFragmentToLocalDetailFragment(med.id_med)
            findNavController().navigate(action)
        }

        binding.rvGuardados.layoutManager = LinearLayoutManager(requireContext())
        binding.rvGuardados.adapter = adapter

        viewModel.cargarGuardados()

        viewModel.medicamentosGuardados.observe(viewLifecycleOwner) { meds ->
            if (meds.isEmpty()) mostrarEstado("No tienes medicamentos guardados")
            else {
                adapter.submitList(meds)
                mostrarLista()
            }
        }
    }

    private fun mostrarLista() {
        binding.rvGuardados.visibility = View.VISIBLE
        binding.tvEstado.visibility = View.GONE
    }

    private fun mostrarEstado(mensaje: String) {
        binding.tvEstado.text = mensaje
        binding.tvEstado.visibility = View.VISIBLE
        binding.rvGuardados.visibility = View.GONE
    }

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
