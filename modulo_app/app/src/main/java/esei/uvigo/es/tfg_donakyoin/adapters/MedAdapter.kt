package esei.uvigo.es.tfg_donakyoin.adapters
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import esei.uvigo.es.tfg_donakyoin.R
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
            // Banderas
            val flagRes = flagResFor(med.iso_code)
            if (flagRes != null) {
                binding.ivBandera.setImageResource(flagRes)
                binding.ivBandera.visibility = View.VISIBLE
            } else {
                binding.ivBandera.visibility = View.GONE
            }
            binding.executePendingBindings()
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
