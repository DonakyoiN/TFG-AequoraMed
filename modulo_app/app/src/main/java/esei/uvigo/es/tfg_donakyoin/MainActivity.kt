package esei.uvigo.es.tfg_donakyoin
import android.content.Context
import android.content.res.Configuration
import android.os.Bundle
import esei.uvigo.es.tfg_donakyoin.utils.PrefsManager
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import java.util.Locale
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.NavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    // NavController
    private lateinit var navController: NavController

    companion object {
        var pendingThemeChange = false
    }

    override fun attachBaseContext(newBase: Context) {
        val prefs = PrefsManager(newBase)

        AppCompatDelegate.setDefaultNightMode(
            if (prefs.isDarkMode()) AppCompatDelegate.MODE_NIGHT_YES
            else AppCompatDelegate.MODE_NIGHT_NO
        )

        val config = Configuration(newBase.resources.configuration)
        config.setLocale(Locale(prefs.getLanguage()))
        super.attachBaseContext(newBase.createConfigurationContext(config))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        // Fade-in tras recreate de tema/idioma para evitar parpadeos
        if (pendingThemeChange) {
            pendingThemeChange = false
            val root = findViewById<android.view.View>(R.id.main)
            root.alpha = 0f
            root.post { root.animate().alpha(1f).setDuration(200).start() }
        }

        // Insets para configurar: Barra Superior + Barra de Navegación
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, 0, systemBars.right, 0)
            insets
        }

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.app_bar)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(0, systemBars.top, 0, 0)
            insets
        }

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.bottom_nav)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(0, 0, 0, systemBars.bottom)
            insets
        }

        // Manejo de la Navegación
        val navHostFragment = supportFragmentManager.findFragmentById(R.id.navHostFragment) as NavHostFragment
        navController = navHostFragment.navController
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)
        bottomNav.setupWithNavController(navController)

        // No vuelve al inicio tras cambiar Ajuste
        if (intent.getBooleanExtra("navigate_to_settings", false)) {
            bottomNav.selectedItemId = R.id.settingsFragment
        }

        // Toolbar
        val toolbar = findViewById<MaterialToolbar>(R.id.toolbar)
        setSupportActionBar(toolbar)
        val appBarConfig = AppBarConfiguration(
            setOf(R.id.searchFragment, R.id.savedFragment, R.id.settingsFragment)
        )
        setupActionBarWithNavController(navController, appBarConfig)
    }

    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp() || super.onSupportNavigateUp()
    }
}