package esei.uvigo.es.tfg_donakyoin.utils
import android.content.Context

class PrefsManager(context: Context) {

    private val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

    // Verificar Modo Oscuro
    fun isDarkMode(): Boolean = prefs.getBoolean("dark_mode", false)

    // Aplicar Modo Oscuro
    fun setDarkMode(enabled: Boolean) = prefs.edit().putBoolean("dark_mode", enabled).apply()

    // Obtener Idioma Actual - Default: Español
    fun getLanguage(): String = prefs.getString("language", "es") ?: "es"

    // Aplicar Idioma
    fun setLanguage(lang: String) = prefs.edit().putString("language", lang).apply()
}
