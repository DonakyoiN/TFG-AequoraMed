package esei.uvigo.es.tfg_donakyoin.fragments
import android.os.Bundle
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.widget.FrameLayout
import androidx.core.graphics.ColorUtils
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.Fragment
import com.google.android.material.color.MaterialColors
import com.google.android.material.progressindicator.CircularProgressIndicator
import esei.uvigo.es.tfg_donakyoin.MainActivity
import esei.uvigo.es.tfg_donakyoin.R
import esei.uvigo.es.tfg_donakyoin.databinding.FragmentSettingsBinding
import esei.uvigo.es.tfg_donakyoin.utils.PrefsManager

class SettingsFragment : Fragment() {

    // ViewBinding
    private var _binding: FragmentSettingsBinding? = null
    private val binding get() = _binding!!
    // Preferencias de Configuración
    private lateinit var prefs: PrefsManager
    // Flag de Estado
    private var isRelaunching = false

    // onCreateView para SettingsFragment
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentSettingsBinding.inflate(inflater, container, false)
        return binding.root
    }

    // onViewCreated para el view binding con el Layout
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        prefs = PrefsManager(requireContext())

        binding.switchDarkMode.isChecked = prefs.isDarkMode()
        binding.chipGroupIdioma.check(if (prefs.getLanguage() == "en") R.id.chip_en else R.id.chip_es)

        // Cambio de Tema
        binding.switchDarkMode.setOnCheckedChangeListener { _, isChecked ->
            if (isRelaunching) return@setOnCheckedChangeListener
            prefs.setDarkMode(isChecked)
            relaunchWithOverlay()
        }

        // Cambio de Idioma
        binding.chipGroupIdioma.setOnCheckedStateChangeListener { _, checkedIds ->
            if (isRelaunching || checkedIds.isEmpty()) return@setOnCheckedStateChangeListener
            val newLang = if (checkedIds.first() == R.id.chip_en) "en" else "es"
            if (newLang == prefs.getLanguage()) return@setOnCheckedStateChangeListener
            prefs.setLanguage(newLang)
            relaunchWithOverlay()
        }
    }

    // Muestra overlay de carga y relanza MainActivity con el cambio aplicado
    private fun relaunchWithOverlay() {
        isRelaunching = true
        val activity = requireActivity()
        val rootView = activity.window.decorView as ViewGroup
        val bgColor = MaterialColors.getColor(activity, android.R.attr.colorBackground, android.graphics.Color.WHITE)

        // Overlay con fondo del tema actual
        val overlay = FrameLayout(activity).apply {
            setBackgroundColor(bgColor)
            alpha = 0f
            layoutParams = ViewGroup.LayoutParams(MATCH_PARENT, MATCH_PARENT)
        }
        // Indicador de carga centrado
        val progress = CircularProgressIndicator(activity).apply {
            isIndeterminate = true
            layoutParams = FrameLayout.LayoutParams(WRAP_CONTENT, WRAP_CONTENT, Gravity.CENTER)
        }
        overlay.addView(progress)
        rootView.addView(overlay)

        // Sincroniza los iconos de barra de estado con el color del overlay
        val isLightBackground = ColorUtils.calculateLuminance(bgColor) > 0.5
        WindowInsetsControllerCompat(activity.window, rootView).apply {
            isAppearanceLightStatusBars = isLightBackground
            isAppearanceLightNavigationBars = isLightBackground
        }

        // Fade-in del overlay y relaunch al terminar
        overlay.animate()
            .alpha(1f)
            .setDuration(200)
            .withEndAction {
                activity.window.setWindowAnimations(0)
                MainActivity.pendingThemeChange = true
                activity.recreate()
            }
            .start()
    }

    // onDestroyView para limpieza de Vista
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
