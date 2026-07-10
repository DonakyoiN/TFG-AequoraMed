# TFG - Desarrollo de una Aplicación de Equivalencias Farmacéuticas Internacional

Aplicación móvil Android para consultar medicamentos de cinco países (España, Chile, Portugal, Canadá y Estados Unidos) y obtener sus equivalencias internacionales a partir de datos oficiales de las agencias reguladoras. Las correspondencias se establecen por **código ATC** y **principio activo**.

Trabajo de Fin de Grado — Grado en Ingeniería Informática  
Escola Superior de Enxeñaría Informática, Universidade de Vigo. Curso 2025/2026.  
**Autor:** Marcelo Antonio Véliz Ossandón
**Código TFG**: EI 25/26-123
---

## Contenido del directorio

El directorio de entrega tiene la siguiente estructura raíz:

```
Entrega_TFG_MarceloAntonioVelizOssandon/
├── src/                                                # Código fuentes completo
├── Distribuibles/
│   └── AequoraMed.apk                                  # APK instalable de la app
├── Documentacion_TFG_MarceloAntonioVelizOssandon.pdf   # Memoria del TFG en formato PDF
└── README.md                                           # Archivo de información
```

Contenido de `src/`:

```
src/
├── modulo_datos/                                        # ETL (Python): extrae y normaliza los datos
│   ├── database/
│   │   └── db_med.sql                                   # DDL completo: esquemas, extensiones, tablas e índices
│   ├── scripts/
│   │   ├── database.py                                  # Conexión a la BD compartida por todos los scripts
│   │   ├── fuentes_externas/                            # Extracción por país (rellena el esquema `fuentes`)
│   │   │   ├── data/
│   │   │   │   ├── lista_infomed.csv                    # Dataset ISP Chile
│   │   │   │   └── Productos_RECETA_SIMPLE.csv          # Dataset INFARMED Portugal
│   │   │   ├── spain_med.py                             # AEMPS — Agencia Española de Medicamentos
│   │   │   ├── chile_med.py                             # ISP Chile (CSV local)
│   │   │   ├── portugal_med.py                          # INFARMED Portugal (CSV local)
│   │   │   ├── canada_med.py                            # Health Canada API
│   │   │   ├── usa_fda.py                               # openFDA API
│   │   │   └── usa_rxnorm.py                            # NIH RxNorm API
│   │   ├── etl/                                         # Transformación y carga al esquema `med`
│   │   │   ├── load_diccionarios.py                     # Carga países, formas, vías, principios activos y ATCs
│   │   │   ├── load_medicamentos.py                     # Carga los medicamentos normalizados de cada país
│   │   │   └── load_relaciones.py                       # Carga relaciones medicamento-ATC y medicamento-principio_activo
│   │   └── test_preliminar/
│   │       └── test_equivalencias.py                    # Validación preliminar del algoritmo de equivalencias
│   ├── requirements.txt
│   └── .env                                             # Credenciales BD (no incluido)
├── modulo_api/                                          # API REST (FastAPI)
│   ├── app/
│   │   ├── database.py                                  # Conexión psycopg2 con RealDictCursor
│   │   ├── models/                                      # Modelos Pydantic (respuestas JSON)
│   │   │   ├── atc.py
│   │   │   ├── equivalencia.py
│   │   │   ├── forma_farmaceutica.py
│   │   │   ├── medicamento.py
│   │   │   ├── pais.py
│   │   │   ├── principio_activo.py
│   │   │   └── via_administracion.py
│   │   └── routers/
│   │       ├── medicamentos.py                          # GET /medicamentos/buscar, /medicamentos/id_med
│   │       └── equivalencias.py                         # GET /equivalencias/id_med (algoritmo ATC/PA)
│   ├── tests/
│   │   ├── conftest.py                                  # Fixture de TestClient con scope de sesión
│   │   └── test_api.py                                  # 20 tests de búsqueda, detalle, equivalencias
│   ├── main.py                                          # Punto de entrada Uvicorn + routers auxiliares
│   ├── requirements.txt
│   └── .env                                             # Credenciales BD (no incluido)
└── modulo_app/                                          # App Android (Kotlin, MVVM)
    ├── app/
    │   ├── build.gradle
    │   ├── proguard-rules.pro
    │   └── src/
    │       ├── androidTest/java/.../
    │       │   └── MedDaoTest.kt                        # 5 tests instrumentados (Room)
    │       ├── test/java/.../
    │       │   └── MedMapperTest.kt                     # 4 tests unitarios (MedMapper)
    │       └── main/java/esei/uvigo/es/tfg_donakyoin/
    │           ├── App.kt                               # Clase Application que aplica tema oscuro/claro al arrancar
    │           ├── MainActivity.kt                      # NavHostFragment + BottomNavigationView
    │           ├── adapters/
    │           │   ├── EquivalenciaAdapter.kt
    │           │   └── MedAdapter.kt
    │           ├── database/                            # Room (consulta offline)
    │           │   ├── MedDao.kt
    │           │   └── MedDb.kt                         # Singleton Room que define la BD y expone MedDao
    │           ├── entities/
    │           │   └── MedEntity.kt                     
    │           ├── fragments/                           # Fragment con la Vistas para Búsqueda, Detalle, Filtro, Equivalencias, Guardados y Ajustes
    │           │   ├── DetailFragment.kt                # Detalle de Medicamentos
    │           │   ├── EquivalenciasBottomSheet.kt      # Equivalencias Farmacéuticas
    │           │   ├── FilterBottomSheet.kt             # Filtrado de Búsqueda
    │           │   ├── LocalDetailFragment.kt           # Detalle de Medicamentos Guardados
    │           │   ├── SavedFragment.kt                 # Lista de Medicamentos Guardados
    │           │   ├── SearchFragment.kt                # Buscador de Medicamentos
    │           │   └── SettingsFragment.kt              # Ajustes de la Aplicación
    │           ├── models/                              # DTOs Moshi / Retrofit
    │           │   ├── AtcDto.kt
    │           │   ├── EquivalenciaDto.kt
    │           │   ├── FormaFarmaceuticaDto.kt
    │           │   ├── MedicamentoDto.kt
    │           │   ├── PaisDto.kt
    │           │   ├── PrincipioActivoDto.kt
    │           │   └── ViaAdministracionDto.kt
    │           ├── network/
    │           │   ├── ApiService.kt                    # Interfaz Retrofit de la API
    │           │   └── RetrofitClient.kt                # BASE_URL y configuración Moshi
    │           ├── repository/
    │           │   └── MedRepository.kt                 # Fuente única de verdad (API + Room)
    │           ├── utils/
    │           │   ├── CountryUtils.kt                  # Mapeo de ISO code a nombre e icono de bandera
    │           │   ├── MedMapper.kt                     # Mapeo de los datos de DTO a MedEntity (Room) y viceversa
    │           │   ├── PrefsManager.kt                  # SharedPreferences (idioma, tema)
    │           │   └── RecentSearchManager.kt
    │           └── viewmodel/
    │               └── MedViewModel.kt                  # ViewModel compartido por todos los fragments
    ├── gradle/
    │   ├── libs.versions.toml                           # Catálogo de versiones de dependencias
    │   └── wrapper/
    │       └── gradle-wrapper.properties
    ├── build.gradle
    ├── settings.gradle
    └── gradle.properties
```

---

## Stack tecnológico

| Ámbito | Tecnología |
|--------|-----------|
| Base de datos | PostgreSQL 18 + extensiones `unaccent`, `pg_trgm` |
| Backend | Python 3.14, FastAPI 0.136, Uvicorn, Pydantic 2, psycopg2 |
| ETL | Python 3.14, `requests`, `pandas`, `numpy` |
| Aplicación | Kotlin, Android SDK 35, Retrofit 2, Moshi, Room, Material 3 |
| Despliegue | Render (PostgreSQL gestionado + Web Service con la API) |

---

## Configuración (.env)

`modulo_datos` y `modulo_api` leen sus credenciales de un archivo `.env` en la raíz de cada módulo. Crea un `.env` en **cada uno** de los dos directorios antes de ejecutar nada:

```env
DB_NAME=<nombre_db>
DB_USER=<user_db>
DB_PASS=<tu_contraseña>
DB_HOST=localhost
DB_PORT=5432
DB_SSLMODE=prefer
```

Para conectar a la base de datos de **Render**, sustituye `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` y `DB_NAME` con los valores que Render muestra en el panel de la base de datos, y cambia `DB_SSLMODE=require`.

---

## Despliegue en local

### Prerrequisitos

- PostgreSQL 18 o superior instalado y en ejecución.
- Python 3.14 o superior.
- Android Studio (para compilar y ejecutar la app).

> **Windows:** todos los comandos de esta sección asumen un entorno Unix. Se recomienda usar **WSL** (Windows Subsystem for Linux) y seguir las instrucciones tal como están.

### 1. Crear la base de datos

Asegúrate de que el servidor PostgreSQL está en ejecución antes de continuar.

**Linux**
```bash
sudo systemctl start postgresql
```

**macOS**
```bash
brew services start postgresql  # Homebrew
```

**Windows:** se recomienda usar **WSL** (Windows Subsystem for Linux) y seguir las instrucciones de Linux. La instalación nativa de PostgreSQL en Windows requiere arrancar manualmente el servicio `postgresql-x64-XX` desde `services.msc` o pgAdmin, y los comandos de terminal del resto de esta sección asumen un entorno Unix.

Con el servidor activo, crea la base de datos y aplica el DDL:

```bash
sudo -u postgres createdb <nombre_db>
sudo -u postgres psql -d <nombre_db> -f modulo_datos/database/db_med.sql
```

> En instalaciones donde tu usuario del sistema ya tiene un rol PostgreSQL con permisos de superusuario, puedes omitir `sudo -u postgres`.

El script `db_med.sql` crea los dos esquemas (`fuentes` y `med`), activa las extensiones `unaccent` y `pg_trgm`, define la función `f_unaccent` y crea todas las tablas e índices.

Para verificar que todo se creó correctamente (tablas de ambos esquemas, índices, extensiones y función `f_unaccent`):

```bash
sudo -u postgres psql -d <nombre_db> \
  -c "\dt med.*" \
  -c "\dt fuentes.*" \
  -c "\di med.*" \
  -c "\dx" \
  -c "\df f_unaccent"
```

### 2. Cargar los datos

Instala las dependencias y ejecuta los scripts desde la raíz de `modulo_datos/`, con el `.env` configurado. El proceso funciona igual apuntando a una base de datos local o a la de Render.

```bash
cd modulo_datos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Extracción desde las fuentes oficiales (rellena el esquema `fuentes`):
```bash
python -m scripts.fuentes_externas.spain_med
python -m scripts.fuentes_externas.chile_med
python -m scripts.fuentes_externas.portugal_med
python -m scripts.fuentes_externas.canada_med
python -m scripts.fuentes_externas.usa_fda
python -m scripts.fuentes_externas.usa_rxnorm
```

Carga normalizada al esquema `med`, en este orden:
```bash
python -m scripts.etl.load_diccionarios
python -m scripts.etl.load_medicamentos
python -m scripts.etl.load_relaciones
```


### 3. Levantar la API

Desde la raíz de `modulo_api/`, con el `.env` configurado:

```bash
cd modulo_api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```

La API queda disponible en `http://localhost:8000`.  
La documentación interactiva (Swagger UI) en `http://localhost:8000/docs`.

### 4. App Android

1. Abre la carpeta `modulo_app/` en **Android Studio**.
2. Localiza `app/src/main/java/esei/uvigo/es/tfg_donakyoin/network/RetrofitClient.kt` y ajusta `BASE_URL` según el entorno:
   - Emulador Android - `http://10.0.2.2:8000/`
   - Dispositivo físico en la misma red - `http://<IP-local-del-equipo>:8000/`
   - API desplegada en Render - la URL pública del Web Service.
3. Compila y ejecuta en un emulador o dispositivo con **Android 8.0 (API 26) o superior**.

> **Error de jlink:** si Gradle falla con un error relacionado con `jlink` o la JVM al compilar, detén el daemon desde la terminal de Android Studio y vuelve a ejecutar:
> ```bash
> ./gradlew --stop
> ```
> Esto es muy común si tienes extensiones de Java en Visual Studio Code.

### 5. Instalación directa
Si solo deseas probar la aplicación en un dispositivo Android o emulador sin necesidad de compilar el código fuente:

1. Copia el archivo `Distribuibles/AequoraMed.apk` en tu dispositivo o arrástralo al emulador.
2. Ejecútalo e instálalo (asegúrate de permitir la instalación desde orígenes desconocidos si el sistema lo solicita).

> **Nota:** Esta versión del APK está preconfigurada para comunicarse directamente con la API desplegada en Render. Funcionará al instante siempre que el dispositivo tenga acceso a Internet y que el **servicio esté encendido** en Render, sin necesidad de configurar bases de datos ni levantar servidores locales.
---

## Despliegue en Render

El backend de producción se compone de dos servicios en Render: una **base de datos PostgreSQL gestionada** y un **Web Service** que ejecuta la API con Uvicorn.

### Paso 1: Crear la base de datos PostgreSQL en Render

1. En el panel de Render, crea un nuevo servicio **PostgreSQL**.
2. Asígnale un nombre a la base de datos y selecciona la región más cercana.
3. Una vez creado, Render muestra en el panel del servicio dos cadenas de conexión:
   - **Internal Database URL** — para el Web Service (comunicación interna dentro de Render, más rápida y sin coste de red).
   - **External Database URL** — para conectarte desde fuera de Render (tu equipo local, el ETL).
4. Anota la **External Database URL**; tiene este formato:
   ```
   postgresql://USER:PASSWORD@HOST:PORT/DATABASE
   ```

### Paso 2: Aplicar el DDL e inicializar los datos

**Opción 1:** Desde tu equipo local, aplica el DDL y carga los datos apuntando a la base de datos de Render. Usa la **External Database URL**:

```bash
psql "postgresql://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=require" -f modulo_datos/database/db_med.sql
```

> El panel de la base de datos en Render incluye la **External Database URL** completa lista para copiar.

**Opción 2:** Carga los datos ejecutando el ETL con el `.env` de `modulo_datos` apuntando a Render:

```env
DB_NAME=DATABASE
DB_USER=USER
DB_PASS=PASSWORD
DB_HOST=HOST
DB_PORT=PORT
DB_SSLMODE=require
```

### Paso 3: Crear el Web Service (API)

1. En Render, crea un nuevo **Web Service** y conéctalo al repositorio (o carga el código manualmente).
2. Configura el servicio:

   | Campo | Valor |
   |-------|-------|
   | **Root directory** | `modulo_api` |
   | **Runtime** | Python 3 |
   | **Build command** | `pip install -r requirements.txt` |
   | **Start command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

3. En **Environment Variables**, añade las mismas variables que el `.env`, pero con los valores de la base de datos de Render. Usa la **Internal Database URL** para conectar el Web Service a la BD (más eficiente que la externa):

   | Variable | Valor |
   |----------|-------|
   | `DB_NAME` | nombre de la BD en Render |
   | `DB_USER` | usuario de la BD en Render |
   | `DB_PASS` | contraseña de la BD en Render |
   | `DB_HOST` | host **interno** de la BD en Render |
   | `DB_PORT` | puerto interno (normalmente `5432`) |
   | `DB_SSLMODE` | `require` |

4. Despliega. Una vez activo, Render asigna una URL pública. Verifica que la API responde en `https://<tu-url>.onrender.com/docs`.

### Paso 4: Conectar la app Android a Render

En `RetrofitClient.kt`, cambia `BASE_URL` a la URL pública del Web Service:

```kotlin
private const val BASE_URL = "https://<tu-url>.onrender.com/"
```

Recompila e instala la app.

> **Nota sobre el tier gratuito de Render:** los Web Services en el plan Free se suspenden tras 15 minutos de inactividad. La primera petición tras una suspensión puede tardar 30-60 segundos en responder (cold start). Su uso continuado solo está disponible en planes de pago.

---

## Pruebas

### API (pytest)

La suite de pruebas requiere que la API esté conectada a una base de datos con datos cargados. Desde `modulo_api/` con el entorno activado y el `.env` configurado:

```bash
pytest -v
```

Los 20 tests cubren los tres endpoints principales: Búsqueda con sus cinco modos y cuatro filtros, detalle de medicamento, y equivalencias (por ATC, por principio activo, por inferencia para Chile y Portugal, filtro por país destino y búsqueda cross-idioma).

### App Android

Los tests de Android se ejecutan desde Android Studio o con Gradle:

```bash
# Tests unitarios (no requieren dispositivo)
cd modulo_app
./gradlew test

# Tests instrumentados (requieren emulador o dispositivo conectado)
./gradlew connectedAndroidTest
```
---

## Documentación

La memoria completa del TFG se encuentra en `Documentacion_TFG_MarceloAntonioVelizOssandon.pdf`, en la raíz del directorio de entrega.
