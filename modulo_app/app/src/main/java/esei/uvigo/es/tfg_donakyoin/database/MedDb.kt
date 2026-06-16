package esei.uvigo.es.tfg_donakyoin.database
import esei.uvigo.es.tfg_donakyoin.entities.*
import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [MedEntity::class, MedDetailEntity::class], version = 1)
abstract class MedDb: RoomDatabase() {

    // MedDao
    abstract fun medDao(): MedDao

    companion object {
        @Volatile
        private var INSTANCE: MedDb? = null

        fun getInstance(context: android.content.Context): MedDb {
            if (INSTANCE == null) {
                synchronized(this) {
                    if (INSTANCE == null) {
                        val created = androidx.room.Room.databaseBuilder(
                            context.applicationContext,
                            MedDb::class.java,
                            "med.db"

                        )
                            .fallbackToDestructiveMigration()
                            .build()
                        INSTANCE = created
                    }
                }
            }
            return INSTANCE!!
        }
    }

}