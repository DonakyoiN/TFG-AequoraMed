package esei.uvigo.es.tfg_donakyoin.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.core.view.isVisible
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import esei.uvigo.es.tfg_donakyoin.R
import esei.uvigo.es.tfg_donakyoin.databinding.ItemEquivalenciaBinding
import esei.uvigo.es.tfg_donakyoin.models.EquivalenciaResumenDto

class EquivalenciaAdapter(
    private val onClickListener: (EquivalenciaResumenDto) -> Unit
) : ListAdapter<EquivalenciaResumenDto, EquivalenciaAdapter.EquivalenciaViewHolder>(EquivalenciaDiffCallback) {

    // EquivalenciaViewHolder
    class EquivalenciaViewHolder(private val binding: ItemEquivalenciaBinding) : RecyclerView.ViewHolder(binding.root) {

        fun bind(med: EquivalenciaResumenDto) {
            binding.med = med
            binding.tvForma.text = listOfNotNull(med.forma_farmaceutica, med.via_administracion).joinToString(" · ")
            // Badge de tipo de equivalencia
            val tipo = med.tipo_equivalencia
            binding.tvTipoEquivalencia.isVisible = tipo != null
            if (tipo != null) {
                val isAtc = tipo.contains("ATC")
                val bgRes = if (isAtc) R.drawable.bg_atc else R.drawable.bg_pa
                binding.tvTipoEquivalencia.background = ContextCompat.getDrawable(binding.root.context, bgRes)
            }
            // Banderas
            val flagRes = flagResFor(med.iso_code)
            if (flagRes != null) binding.ivBandera.setImageResource(flagRes)
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

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): EquivalenciaViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        val binding = ItemEquivalenciaBinding.inflate(inflater, parent, false)
        return EquivalenciaViewHolder(binding)
    }

    override fun onBindViewHolder(holder: EquivalenciaViewHolder, position: Int) {
        val med = getItem(position)
        holder.bind(med)
        holder.itemView.setOnClickListener { onClickListener(med) }
    }

    // DiffCallback para ListAdapter
    companion object EquivalenciaDiffCallback : DiffUtil.ItemCallback<EquivalenciaResumenDto>() {

        override fun areItemsTheSame(oldItem: EquivalenciaResumenDto, newItem: EquivalenciaResumenDto): Boolean {
            return oldItem.id_med == newItem.id_med
        }

        override fun areContentsTheSame(oldItem: EquivalenciaResumenDto, newItem: EquivalenciaResumenDto): Boolean {
            return oldItem == newItem
        }
    }
}
