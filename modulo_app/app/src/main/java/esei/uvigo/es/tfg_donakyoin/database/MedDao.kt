package esei.uvigo.es.tfg_donakyoin.database
import esei.uvigo.es.tfg_donakyoin.entities.*
import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction

@Dao
interface MedDao {

    // MedRepository
    @Query("SELECT * FROM saved_med ORDER BY savedAt DESC")
    suspend fun getAllMeds(): List<MedEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMed(med: MedEntity)

    @Delete
    suspend fun deleteMed(med: MedEntity)

    @Query("SELECT EXISTS(SELECT 1 FROM saved_med WHERE id_med = :id)")
    suspend fun isMedSaved(id: Int): Boolean


    // MedDetailEntity
    @Query("SELECT * FROM saved_detail WHERE id_med = :id")
    suspend fun getDetail(id: Int): MedDetailEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDetail(detail: MedDetailEntity)

    @Query("DELETE FROM saved_detail WHERE id_med = :id")
    suspend fun deleteDetail(id: Int)


    // Transacciones para agrupar operaciones
    @Transaction
    suspend fun saveMedicamento(med: MedEntity, detail: MedDetailEntity) {
        insertMed(med)
        insertDetail(detail)
    }

    @Transaction
    suspend fun deleteMedicamento(med: MedEntity) {
        deleteMed(med)
        deleteDetail(med.id_med)
    }

}
