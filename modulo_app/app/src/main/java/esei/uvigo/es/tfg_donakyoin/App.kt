package esei.uvigo.es.tfg_donakyoin
import android.app.Application
import androidx.appcompat.app.AppCompatDelegate
import esei.uvigo.es.tfg_donakyoin.utils.PrefsManager

class App : Application() {
    override fun onCreate() {
        super.onCreate()
        AppCompatDelegate.setDefaultNightMode(
            if (PrefsManager(this).isDarkMode()) AppCompatDelegate.MODE_NIGHT_YES
            else AppCompatDelegate.MODE_NIGHT_NO
        )
    }
}
