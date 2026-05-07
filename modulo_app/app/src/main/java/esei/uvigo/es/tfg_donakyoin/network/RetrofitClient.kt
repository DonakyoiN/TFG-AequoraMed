package esei.uvigo.es.tfg_donakyoin.network
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory

object RetrofitClient {

   // Localhost mientras la API no esté desplegada
    private const val BASE_URL = "http://10.0.2.2:8000/"
    private val moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(MoshiConverterFactory.create(moshi)).build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}