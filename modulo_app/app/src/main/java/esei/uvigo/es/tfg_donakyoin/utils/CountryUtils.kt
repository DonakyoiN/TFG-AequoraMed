package esei.uvigo.es.tfg_donakyoin.utils
import esei.uvigo.es.tfg_donakyoin.R

// Función para asignar Número de Registro según ISO Code
fun registroLabelFor(isoCode: String): String = when (isoCode.uppercase()) {
    "CA" -> "Drug Identification Number (DIN)"
    "US" -> "Application Number"
    else -> "Nº de Registro"
}

// Función para asignar ícono de Bandera según ISO Code
fun flagResFor(isoCode: String): Int? = when (isoCode.uppercase()) {
    "ES" -> R.drawable.ic_spain
    "CL" -> R.drawable.ic_chile
    "PT" -> R.drawable.ic_portugal
    "US" -> R.drawable.ic_usa
    "CA" -> R.drawable.ic_canada
    else -> null
}
