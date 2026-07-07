package esei.uvigo.es.tfg_donakyoin.fragments
import esei.uvigo.es.tfg_donakyoin.adapters.MedAdapter
import esei.uvigo.es.tfg_donakyoin.databinding.FragmentSavedBinding
import esei.uvigo.es.tfg_donakyoin.viewmodel.MedViewModel
import esei.uvigo.es.tfg_donakyoin.*
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.graphics.Canvas
import androidx.annotation.DrawableRes
import androidx.core.content.ContextCompat
import androidx.core.view.isVisible
import androidx.databinding.DataBindingUtil
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.ItemTouchHelper
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.snackbar.Snackbar

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

        touchGestures()
        viewModel.cargarGuardados()

        viewModel.medicamentosGuardados.observe(viewLifecycleOwner) { meds ->
            if (meds.isEmpty()) mostrarEstado(getString(R.string.saved_vacio), R.drawable.ic_saved_home)
            else {
                adapter.submitList(meds)
                mostrarLista()
            }
        }
    }

    // Interacciones con Gestos
    private fun touchGestures() {

        val helper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
            0,
            ItemTouchHelper.LEFT
        ) {
            // Bloquea si el item es null
            override fun getMovementFlags(
                recyclerView: RecyclerView,
                viewHolder: RecyclerView.ViewHolder
            ): Int {
                val position = viewHolder.bindingAdapterPosition
                if (adapter.currentList.getOrNull(position) == null) return 0
                return super.getMovementFlags(recyclerView, viewHolder)
            }

            // Sin drag
            override fun onMove(
                recyclerView: RecyclerView,
                viewHolder: RecyclerView.ViewHolder,
                target: RecyclerView.ViewHolder
            ): Boolean = false

            // Deslizar a la izquierda: Eliminar
            override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
                val position = viewHolder.bindingAdapterPosition
                val med = adapter.currentList.getOrNull(position) ?: return
                viewModel.eliminarMed(med.id_med)
                Snackbar.make(binding.rvGuardados, getString(R.string.snack_eliminado), Snackbar.LENGTH_SHORT).show()
            }

            // Limpia posición al soltar
            override fun clearView(recyclerView: RecyclerView, viewHolder: RecyclerView.ViewHolder) {
                super.clearView(recyclerView, viewHolder)
                viewHolder.itemView.translationX = 0f
            }

            // Dibuja fondo e ícono durante el swipe
            override fun onChildDraw(
                c: Canvas,
                recyclerView: RecyclerView,
                viewHolder: RecyclerView.ViewHolder,
                dX: Float, dY: Float,
                actionState: Int,
                isCurrentlyActive: Boolean
            ) {
                val deleteIcon = ContextCompat.getDrawable(requireContext(), R.drawable.ic_delete_swipe)
                val deleteBackground = ContextCompat.getDrawable(requireContext(), R.drawable.bg_swipe_delete)

                if (dX == 0f && !isCurrentlyActive) {
                    super.onChildDraw(c, recyclerView, viewHolder, dX, dY, actionState, false)
                    return
                }

                if (actionState == ItemTouchHelper.ACTION_STATE_SWIPE && dX < 0) {
                    val itemView = viewHolder.itemView
                    val iconMargin = (itemView.height - (deleteIcon?.intrinsicHeight ?: 0)) / 2

                    deleteBackground?.setBounds(itemView.right + dX.toInt(), itemView.top, itemView.right, itemView.bottom)
                    deleteBackground?.draw(c)

                    deleteIcon?.let {
                        val iconRight = itemView.right - iconMargin
                        val iconLeft = iconRight - it.intrinsicWidth
                        it.setBounds(iconLeft, itemView.top + iconMargin, iconRight, itemView.bottom - iconMargin)
                        it.draw(c)
                    }
                }
                super.onChildDraw(c, recyclerView, viewHolder, dX, dY, actionState, isCurrentlyActive)
            }
        })
        helper.attachToRecyclerView(binding.rvGuardados)
    }

    // Mostrar lista de guardados
    private fun mostrarLista() {
        binding.rvGuardados.isVisible = true
        binding.tvEstado.isVisible = false
        binding.ivEstado.isVisible = false
    }

    // Mostrar ícono Vacío
    private fun mostrarEstado(mensaje: String, @DrawableRes iconRes: Int) {
        binding.ivEstado.setImageResource(iconRes)
        binding.ivEstado.isVisible = true
        binding.tvEstado.text = mensaje
        binding.tvEstado.isVisible = true
        binding.rvGuardados.isVisible = false
    }

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
