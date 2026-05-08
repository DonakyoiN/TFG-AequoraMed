package esei.uvigo.es.tfg_donakyoin.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import esei.uvigo.es.tfg_donakyoin.databinding.ItemMedicamentoBinding
import esei.uvigo.es.tfg_donakyoin.models.MedicamentoDto

class MedAdapter(
    private val onClickListener: (MedicamentoDto) -> Unit
) : ListAdapter<MedicamentoDto, MedAdapter.MedViewHolder>(MedDiffCallback) {

    // MedViewHolder
    class MedViewHolder(private val binding: ItemMedicamentoBinding) : RecyclerView.ViewHolder(binding.root) {

        fun bind(med: MedicamentoDto) {
            binding.med = med
            binding.tvForma.text =
                listOfNotNull(med.forma_farmaceutica, med.via_administracion).joinToString(" · ")
            binding.executePendingBindings()
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MedViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        val binding = ItemMedicamentoBinding.inflate(inflater, parent, false)
        return MedViewHolder(binding)
    }

    override fun onBindViewHolder(holder: MedViewHolder, position: Int) {
        val med = getItem(position)
        holder.bind(med)
        holder.itemView.setOnClickListener { onClickListener(med) }
    }

    // DiffCallBack para ListAdapter
    companion object MedDiffCallback : DiffUtil.ItemCallback<MedicamentoDto>() {

        override fun areItemsTheSame(oldItem: MedicamentoDto, newItem: MedicamentoDto): Boolean {
            return oldItem.id_med == newItem.id_med
        }

        override fun areContentsTheSame(oldItem: MedicamentoDto, newItem: MedicamentoDto): Boolean {
            return oldItem == newItem
        }
    }
}
