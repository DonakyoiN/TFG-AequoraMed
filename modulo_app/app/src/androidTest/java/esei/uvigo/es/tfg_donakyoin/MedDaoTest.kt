package esei.uvigo.es.tfg_donakyoin
import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import esei.uvigo.es.tfg_donakyoin.database.MedDao
import esei.uvigo.es.tfg_donakyoin.database.MedDb
import esei.uvigo.es.tfg_donakyoin.entities.MedDetailEntity
import esei.uvigo.es.tfg_donakyoin.entities.MedEntity
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MedDaoTest {

    private lateinit var db: MedDb
    private lateinit var dao: MedDao

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, MedDb::class.java)
            .allowMainThreadQueries()
            .build()
        dao = db.medDao()
    }

    @After
    fun tearDown() {
        db.close()
    }

    // Medicamento y Detalle de ejemplo: Nurofen (ES)
    private fun med(id: Int = 1) = MedEntity(
        id_med             = id,
        nom_comercial      = "Nurofen",
        laboratorio        = "Reckitt",
        iso_code           = "ES",
        nom_pais           = "España",
        forma_farmaceutica = "Comprimido Recubierto",
        via_administracion = "Vía Oral",
        savedAt            = 0L
    )

    private fun detail(id: Int = 1) = MedDetailEntity(
        id_med             = id,
        nom_comercial      = "Nurofen",
        reg_pais           = "60699",
        laboratorio        = "Reckitt",
        iso_code           = "ES",
        nom_pais           = "España",
        forma_farmaceutica = "Comprimido Recubierto",
        via_administracion = "Vía Oral",
        dosaje             = "400 mg",
        principios_activos = """[{"id_pa":1,"nom_estandar":"Ibuprofeno"}]""",
        codigos_atc        = """[{"id_atc":1,"code_atc":"M01AE01","desc_es":"Ibuprofeno","desc_en":"Ibuprofen"}]""",
        savedAt            = 0L
    )

    // Inserta un medicamento y verifica que getAllMeds lo devuelve con los campos correctos
    @Test
    fun test_insertarMed() = runBlocking {
        dao.insertMed(med())
        val all = dao.getAllMeds()
        assertEquals(1, all.size)
        assertEquals(1, all[0].id_med)
        assertEquals("Nurofen", all[0].nom_comercial)
        assertEquals("ES", all[0].iso_code)
    }

    // Verifica que isMedSaved devuelve false antes de guardar y true después
    @Test
    fun test_isMedSaved() = runBlocking {
        assertFalse(dao.isMedSaved(1))
        dao.insertMed(med())
        assertTrue(dao.isMedSaved(1))
    }

    // Elimina un medicamento y verifica que desaparece de la lista y de isMedSaved
    @Test
    fun test_eliminarMed() = runBlocking {
        dao.insertMed(med())
        dao.deleteMed(med())
        assertFalse(dao.isMedSaved(1))
        assertTrue(dao.getAllMeds().isEmpty())
    }

    // Guarda medicamento + detalle en transacción y verifica que ambos persisten
    @Test
    fun test_saveMedicamento() = runBlocking {
        dao.saveMedicamento(med(), detail())
        assertTrue(dao.isMedSaved(1))
        val d = dao.getDetail(1)
        assertNotNull(d)
        assertEquals("60699",  d!!.reg_pais)
        assertEquals("400 mg", d.dosaje)
    }

    // Elimina medicamento + detalle en transacción y verifica que ambos desaparecen
    @Test
    fun test_deleteMedicamento() = runBlocking {
        dao.saveMedicamento(med(), detail())
        dao.deleteMedicamento(med())
        assertFalse(dao.isMedSaved(1))
        assertNull(dao.getDetail(1))
        assertTrue(dao.getAllMeds().isEmpty())
    }
}
