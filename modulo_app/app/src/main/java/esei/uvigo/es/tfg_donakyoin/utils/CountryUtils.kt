package esei.uvigo.es.tfg_donakyoin.utils
import esei.uvigo.es.tfg_donakyoin.R

// Función para asignar Número de Registro según ISO Code
fun registroResIdFor(isoCode: String): Int = when (isoCode.uppercase()) {
    "CA" -> R.string.registro_canada
    "US" -> R.string.registro_usa
    else -> R.string.registro_default
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

// Función para asignar nombre de País según ISO Code
fun paisResIdFor(isoCode: String): Int? = when (isoCode.uppercase()) {
    "ES" -> R.string.pais_es
    "CL" -> R.string.pais_cl
    "PT" -> R.string.pais_pt
    "US" -> R.string.pais_us
    "CA" -> R.string.pais_ca
    else -> null
}
