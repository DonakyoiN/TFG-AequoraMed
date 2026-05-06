# TFG — Aplicación de Equivalencias Farmacéuticas Internacional

Aplicación móvil Android (Kotlin) respaldada por una API REST (FastAPI + PostgreSQL) que permite buscar medicamentos de 5 países y encontrar sus equivalencias internacionales por código ATC o principio activo.

**Países cubiertos:** España (ES), Chile (CL), Canadá (CA), Estados Unidos (US), Portugal (PT)

---

## Estructura del Repositorio

```
TFG-DonakyoiN/
├── modulo_api/      # API REST — FastAPI + PostgreSQL
├── modulo_app/      # App Android — Kotlin + Retrofit + Navigation
├── modulo_datos/    # Scripts ETL y esquemas de base de datos
└── docs/            # Documentación, diagramas y memoria LaTeX
```

---

## Módulo API (`modulo_api`)

### Stack técnico
- **FastAPI** 0.136.1 + **Pydantic** 2.13.3
- **PostgreSQL** vía `psycopg2-binary`
- Base de datos con esquemas: `fuentes` (datos brutos), `med` (datos procesados), `app`

### Endpoints actuales

| Método | Ruta | Descripción | Estado |
|--------|------|-------------|--------|
| `GET` | `/` | Health check | ✅ Correcto |
| `GET` | `/paises` | Lista los 5 países disponibles | ✅ Correcto |
| `GET` | `/medicamentos/busqueda_comercial` | Búsqueda por nombre comercial o laboratorio | ⚠️ Refactorizar |
| `GET` | `/medicamentos/id_med` | Detalle completo de un medicamento por ID | ✅ Correcto |
| `GET` | `/equivalencias/{id_med}` | Equivalencias internacionales (ATC + Principio Activo) | ✅ Correcto |

### Lógica de equivalencias

El endpoint `/equivalencias/{id_med}` aplica una estrategia de dos niveles:

1. **`por_atc`** (criterio primario): medicamentos de otros países con el mismo código ATC. Solo aplica a países con datos ATC: ES, CA, US.
2. **`por_principio_activo`** (criterio secundario): medicamentos que comparten principio activo y no aparecen ya en `por_atc`. Cubre CL y PT, que no tienen ATC asignado.

Esta separación ya está lista para el BottomSheet de la app Android.

---

### Cambios pendientes en la API

#### 1. Refactorizar el endpoint de búsqueda

**Problema:** `busqueda_comercial` solo busca por nombre comercial o laboratorio. La app necesita buscar también por principio activo y por código ATC, además de soportar filtros adicionales y paginación.

**Acción:** renombrar a `/medicamentos/buscar` con los siguientes parámetros:

```
GET /medicamentos/buscar
  ?q=             string (mín. 2 chars, obligatorio)
  &modo=          todo | nombre | principio_activo | atc   (default: todo)
  &pais=          ISO code, repetible (?pais=ES&pais=CL)   (opcional)
  &forma=         string ILIKE sobre forma farmacéutica     (opcional)
  &via=           string ILIKE sobre vía de administración  (opcional)
  &laboratorio=   string ILIKE sobre laboratorio            (opcional)
  &limit=         int, default 50, max 200
  &offset=        int, default 0 (paginación)
```

Lógica SQL según `modo`:
- `nombre` → `m.nom_comercial ILIKE %q%`
- `principio_activo` → JOIN `med.contiene` + `med.principio_activo` → `pa.nom_estandar ILIKE %q%`
- `atc` → JOIN `med.identificado_por` + `med.atc` → `a.code_atc ILIKE %q%`
- `todo` → OR de los tres anteriores

#### 2. Nuevos endpoints de catálogo

Necesarios para que la app Android construya dinámicamente los filtros (ChipGroups / dropdowns) sin hardcodear valores.

```
GET /formas_farmaceuticas   → list[FormaFarmaceuticaResponse]
GET /vias_administracion    → list[ViaAdministracionResponse]
```

#### Archivos a crear / modificar

```
modulo_api/app/
  models/
    forma_farmaceutica.py      ← nuevo
    via_administracion.py      ← nuevo
  routers/
    medicamentos.py            ← refactorizar busqueda_comercial → buscar
    catalogos.py               ← nuevo (formas + vias)
main.py                        ← registrar router catalogos
```

---

## Módulo App (`modulo_app`)

### Stack técnico
- **Kotlin** — Android Studio
- **Retrofit 2** + **Moshi** (red)
- **Navigation Component** + Safe Args (navegación entre fragments)
- **ViewModel** + **StateFlow/LiveData** (MVVM)
- **Room** (caché local, si aplica)
- **DataBinding**
- **Glide** (imágenes)
- `minSdk 26` / `targetSdk 36`

### Pantallas previstas

```
MainActivity (host)
│
├── BusquedaFragment          ← pantalla principal
│     ├── SearchView (toolbar)
│     ├── ChipGroup de países (horizontal, scrolleable)
│     ├── Botón "Filtros" → FiltrosBottomSheet
│     └── RecyclerView de resultados
│           └── click en item → DetalleFragment
│
├── DetalleFragment
│     ├── Nombre comercial, laboratorio, país
│     ├── Forma farmacéutica, vía de administración
│     ├── Chips de principios activos
│     ├── Chips de códigos ATC
│     └── Botón "Ver equivalencias" → EquivalenciasBottomSheet
│
├── FiltrosBottomSheet (BottomSheetDialogFragment)
│     ├── Modo de búsqueda (RadioGroup)
│     ├── Forma farmacéutica (Spinner / ChipGroup)
│     ├── Vía de administración (Spinner / ChipGroup)
│     └── Campo de texto: Laboratorio
│
└── EquivalenciasBottomSheet (BottomSheetDialogFragment)
      ├── Sección "Por Código ATC"
      │     └── Lista de medicamentos equivalentes
      └── Sección "Por Principio Activo"
            └── Lista de medicamentos equivalentes
```

### Capa de red — estructura de ficheros

```
network/
  ApiClient.kt                 ← instancia Retrofit (singleton)
  ApiService.kt                ← interfaz con todos los endpoints
  model/
    PaisDto.kt
    MedicamentoResumenDto.kt
    MedicamentoDetalleDto.kt   ← incluye principios_activos y codigos_atc
    EquivalenciaResponseDto.kt ← incluye por_atc y por_principio_activo
    FormaFarmaceuticaDto.kt
    ViaAdministracionDto.kt
repository/
  MedicamentoRepository.kt    ← envuelve llamadas en Result<T>
```

### Interfaz Retrofit (`ApiService.kt`)

```kotlin
interface ApiService {

    @GET("paises")
    suspend fun getPaises(): List<PaisDto>

    @GET("medicamentos/buscar")
    suspend fun buscarMedicamentos(
        @Query("q") q: String,
        @Query("modo") modo: String = "todo",
        @Query("pais") pais: List<String>? = null,
        @Query("forma") forma: String? = null,
        @Query("via") via: String? = null,
        @Query("laboratorio") laboratorio: String? = null,
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0
    ): List<MedicamentoResumenDto>

    @GET("medicamentos/id_med")
    suspend fun getDetalleMedicamento(@Query("id_med") idMed: Int): MedicamentoDetalleDto

    @GET("equivalencias/{id_med}")
    suspend fun getEquivalencias(
        @Path("id_med") idMed: Int,
        @Query("pais") pais: List<String>? = null
    ): EquivalenciaResponseDto

    @GET("formas_farmaceuticas")
    suspend fun getFormasFarmaceuticas(): List<FormaFarmaceuticaDto>

    @GET("vias_administracion")
    suspend fun getViasAdministracion(): List<ViaAdministracionDto>
}
```

---

## Plan de implementación

### Fase 1 — API: ampliar búsqueda y añadir catálogos

1. Crear `models/forma_farmaceutica.py` y `models/via_administracion.py`
2. Crear `routers/catalogos.py` con `GET /formas_farmaceuticas` y `GET /vias_administracion`
3. Registrar el router en `main.py`
4. Refactorizar `routers/medicamentos.py`: endpoint `buscar` con los 3 modos, filtros adicionales y paginación
5. Verificar todo con Swagger UI (`/docs`)

### Fase 2 — Android: capa de red

1. Crear data classes Moshi para todos los DTOs
2. Implementar `ApiClient.kt` (Retrofit + Moshi + OkHttp)
3. Implementar `ApiService.kt`
4. Implementar `MedicamentoRepository.kt` con `Result<T>`

### Fase 3 — Android: BusquedaFragment

1. Crear navigation graph con `BusquedaFragment` y `DetalleFragment`
2. Layout de `BusquedaFragment` (SearchView + ChipGroup países + RecyclerView)
3. `BusquedaViewModel` con StateFlow para query, filtros y resultados
4. `MedicamentoAdapter` (RecyclerView + DiffUtil)
5. Búsqueda básica end-to-end funcional (sin filtros)
6. `FiltrosBottomSheet` + carga de catálogos (formas, vías)
7. Paginación: cargar más al llegar al final del RecyclerView (`offset += limit`)

### Fase 4 — Android: DetalleFragment + Equivalencias

1. Layout de `DetalleFragment` (datos completos del medicamento)
2. `DetalleViewModel` (llama a `getDetalleMedicamento`)
3. `EquivalenciasBottomSheet` con RecyclerView por secciones
4. `EquivalenciasAdapter` con `sealed class` para items de sección vs items de medicamento
5. Botón "Ver equivalencias" en `DetalleFragment` abre el BottomSheet

---

## Notas técnicas

- **Debounce en búsqueda:** aplicar ~400 ms en el `SearchView` antes de lanzar la llamada a la API para no saturar con cada pulsación de tecla.
- **Países con ATC:** ES, CA, US. Los países CL y PT solo aparecen en `por_principio_activo`.
- **Deduplicación de equivalencias:** ya gestionada en la API; la app solo necesita renderizar las dos listas tal como llegan.
- **Filtros vacíos en BottomSheet de equivalencias:** si `por_atc` está vacío, mostrar mensaje explicativo en lugar de sección vacía.
- **Codificación de principios activos:** están normalizados a mayúsculas en la base de datos (ETL). La búsqueda ILIKE lo maneja automáticamente.
