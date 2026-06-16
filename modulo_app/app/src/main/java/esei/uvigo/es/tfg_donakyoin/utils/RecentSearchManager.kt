package esei.uvigo.es.tfg_donakyoin.utils
import android.content.Context
import org.json.JSONArray

class RecentSearchManager(context: Context) {

    private val prefs = context.getSharedPreferences("recent_searches", Context.MODE_PRIVATE)
    private val KEY = "searches"
    private val MAX = 10

    // Obtener Búsquedas Recientes
    fun getSearches(): List<String> {
        val json = prefs.getString(KEY, null) ?: return emptyList()
        return try {
            val arr = JSONArray(json)
            (0 until arr.length()).map { arr.getString(it) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    // Añadir Búsqueda
    fun addSearch(query: String) {
        val list = getSearches().toMutableList()
        list.remove(query)
        list.add(0, query)
        if (list.size > MAX) list.removeAt(list.size - 1)
        save(list)
    }

    // Eliminar Búsqueda
    fun removeSearch(query: String) {
        val list = getSearches().toMutableList()
        list.remove(query)
        save(list)
    }

    // Función para Guardar lista de Búsquedas
    private fun save(list: List<String>) {
        prefs.edit().putString(KEY, JSONArray(list).toString()).apply()
    }
}
