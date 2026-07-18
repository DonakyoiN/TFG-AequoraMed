# AequoraMed

[![Android](https://img.shields.io/badge/Platform-Android%208.0%2B-brightgreen)](https://developer.android.com)
[![Kotlin](https://img.shields.io/badge/Kotlin-2.2.20-purple)](https://kotlinlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://python.org)
[![License](https://img.shields.io/github/license/DonakyoiN/TFG-AequoraMed)](LICENSE)

**AequoraMed** es una aplicación móvil Android que permite buscar medicamentos registrados en **España, Chile, Portugal, Canadá y Estados Unidos** y encontrar sus equivalencias internacionales a partir de datos oficiales de las agencias reguladoras de cada país.

Trabajo de Fin de Grado 25/26 — Escola Superior de Enxeñaría Informática, Universidade de Vigo.

**Autor:** [@DonakyoiN](https://github.com/DonakyoiN)

> **Nota:** Las equivalencias que muestra AequoraMed son **correspondencias informativas** basadas en **código ATC** y **principio activo**. No son bioequivalencias ni sustituyen el criterio de un profesional sanitario.

---

## Capturas

Búsqueda de medicamentos por nombre en cinco países, ficha completa con código ATC y principios activos, y equivalencias internacionales filtradas por país destino.

<p align="center">
  <img src="assets/screenshots/Screenshot_Busqueda_Med.jpg" width="220" alt="Búsqueda">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/screenshots/Screenshot_Detalle_Med.jpg" width="220" alt="Detalle de medicamento">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/screenshots/Screenshot_Equivalencia_Med.jpg" width="220" alt="Equivalencias internacionales">
</p>

---

## Arquitectura

El proyecto se divide en tres módulos independientes que colaboran entre sí:

<p align="center">
  <img src="assets/TFG_ArquitecturaSistema.png" alt="Arquitectura del sistema">
</p>

| Módulo | Tecnología | Responsabilidad |
|--------|-----------|-----------------|
| `modulo_datos` | Python, pandas | Extrae y normaliza datos de 5 agencias reguladoras oficiales |
| `modulo_api` | FastAPI, psycopg2 | Expone la búsqueda y el algoritmo de equivalencias vía REST |
| `modulo_app` | Kotlin, MVVM, Room | App Android con búsqueda, detalle, equivalencias y modo offline |

### Estructura del repositorio

```
modulo_datos/
├── database/
│   └── db_med.sql                     # DDL completo: esquemas, extensiones, tablas e índices
├── scripts/
│   ├── database.py                    # Conexión compartida por todos los scripts
│   ├── fuentes_externas/              # Extracción por país (esquema fuentes)
│   │   ├── data/
│   │   │   ├── lista_infomed.csv      # Dataset ISP Chile
│   │   │   └── Productos_RECETA_SIMPLE.csv  # Dataset INFARMED Portugal
│   │   ├── spain_med.py              # AEMPS
│   │   ├── chile_med.py              # ISP Chile
│   │   ├── portugal_med.py           # INFARMED
│   │   ├── canada_med.py             # Health Canada API
│   │   ├── usa_fda.py                # openFDA API
│   │   └── usa_rxnorm.py             # NIH RxNorm API
│   └── etl/                          # Transformación y carga al esquema med
│       ├── load_diccionarios.py
│       ├── load_medicamentos.py
│       └── load_relaciones.py
└── requirements.txt

modulo_api/
├── app/
│   ├── database.py                   # Conexión psycopg2 con RealDictCursor
│   ├── models/                       # Modelos Pydantic (respuestas JSON)
│   └── routers/
│       ├── medicamentos.py           # GET /medicamentos/buscar, /medicamentos/{id}
│       └── equivalencias.py          # GET /equivalencias/{id} (algoritmo ATC/PA)
├── tests/
│   ├── conftest.py
│   └── test_api.py                   # 20 tests de búsqueda, detalle y equivalencias
├── main.py
└── requirements.txt

modulo_app/app/src/main/java/esei/uvigo/es/tfg_donakyoin/
├── fragments/                        # Búsqueda, Detalle, Equivalencias, Guardados, Ajustes
├── viewmodel/MedViewModel.kt         # ViewModel compartido por todos los fragments
├── repository/MedRepository.kt       # Fuente única de verdad (API + Room)
├── database/                         # Room: MedDao + MedDb
├── network/                          # Retrofit + Moshi
├── models/                           # DTOs de la API
└── utils/                            # CountryUtils, MedMapper, PrefsManager
```

---

## Stack tecnológico

| Ámbito | Tecnología |
|--------|-----------|
| Base de Datos | PostgreSQL 18 + extensiones `unaccent`, `pg_trgm` |
| API | Python 3.14, FastAPI 0.136, Uvicorn, Pydantic 2, psycopg2 |
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

Para conectar a la base de datos de **Render**, sustituye `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` y `DB_NAME` con los valores del panel de Render, y cambia `DB_SSLMODE=require`.

---

## Despliegue en local

### Requisitos

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

>**Windows:** se recomienda usar **WSL** y seguir las instrucciones de Linux. La instalación nativa requiere arrancar el servicio `postgresql-x64-XX` desde `services.msc` o pgAdmin.

Con el servidor activo, crea la base de datos y aplica el DDL:

```bash
sudo -u postgres createdb <nombre_db>
sudo -u postgres psql -d <nombre_db> -f modulo_datos/database/db_med.sql
```

> En instalaciones donde tu usuario ya tiene un rol PostgreSQL con permisos de superusuario, puedes omitir `sudo -u postgres`.

El script crea los dos esquemas (`fuentes` y `med`), activa las extensiones `unaccent` y `pg_trgm`, define `f_unaccent` y crea todas las tablas e índices.

### 2. Cargar los datos

Desde `modulo_datos/`, con el `.env` configurado:

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

Desde `modulo_api/`, con el `.env` configurado:

```bash
cd modulo_api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```

La API queda disponible en `http://localhost:8000`.  
La documentación interactiva (Swagger UI) en `http://localhost:8000/docs`.

### 4. App Android

1. Abre `modulo_app/` en **Android Studio**.
2. Localiza `app/src/main/java/esei/uvigo/es/tfg_donakyoin/network/RetrofitClient.kt` y ajusta `BASE_URL` según el entorno:
   - Emulador Android → `http://10.0.2.2:8000/`
   - Dispositivo físico en la misma red → `http://<IP-local-del-equipo>:8000/`
   - API desplegada en Render → la URL pública del Web Service
3. Compila y ejecuta en un emulador o dispositivo con **Android 8.0 (API 26) o superior**.

> **Error de jlink:** si Gradle falla con un error relacionado con `jlink` o la JVM, detén el daemon y vuelve a ejecutar:
> ```bash
> ./gradlew --stop
> ```
> Es frecuente si tienes extensiones de Java en Visual Studio Code.

---

## Despliegue en Render

El backend de producción se compone de dos servicios: una **base de datos PostgreSQL gestionada** y un **Web Service** con la API.

### Paso 1: Crear la base de datos PostgreSQL

1. En el panel de Render, crea un nuevo servicio **PostgreSQL**.
2. Una vez creado, anota la **External Database URL** (formato `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`).

### Paso 2: Aplicar el DDL e inicializar los datos

Desde tu equipo local, aplica el DDL apuntando a Render:

```bash
psql "postgresql://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=require" -f modulo_datos/database/db_med.sql
```

Luego ejecuta el ETL con el `.env` de `modulo_datos` configurado con los valores de Render (`DB_SSLMODE=require`).

### Paso 3: Crear el Web Service (API)

1. En Render, crea un nuevo **Web Service** y conéctalo al repositorio.
2. Configura el servicio:

   | Campo | Valor |
   |-------|-------|
   | **Root directory** | `modulo_api` |
   | **Runtime** | Python 3 |
   | **Build command** | `pip install -r requirements.txt` |
   | **Start command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

3. En **Environment Variables**, añade las variables del `.env` con los valores de la BD de Render, usando la **Internal Database URL** para `DB_HOST`.

4. Una vez activo, verifica que la API responde en `https://<tu-url>.onrender.com/docs`.

### Paso 4: Conectar la app Android

En `RetrofitClient.kt`, actualiza `BASE_URL` con la URL pública del Web Service y recompila.

> **Tier gratuito de Render:** los Web Services en el plan Free se suspenden tras 15 minutos de inactividad. La primera petición tras una suspensión puede tardar 30-60 segundos (cold start).

---

## Pruebas

### API (pytest)

Requiere la API conectada a una base de datos con datos cargados. Desde `modulo_api/` con el entorno activado:

```bash
pytest -v
```

Los 20 tests cubren los tres endpoints: búsqueda (cinco modos y cuatro filtros), detalle de medicamento y equivalencias (por ATC, por principio activo, inferencia para Chile y Portugal, filtro por país destino y búsqueda cross-idioma).

### App Android

```bash
# Tests unitarios (no requieren dispositivo)
cd modulo_app
./gradlew test

# Tests instrumentados (requieren emulador o dispositivo conectado)
./gradlew connectedAndroidTest
```
---

## Licencia

Distribuido bajo la licencia especificada en el archivo [LICENSE](LICENSE).
