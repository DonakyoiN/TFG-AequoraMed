from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg2.extensions import connection
from app.database import get_db
from app.models.medicamento import MedicamentoResumen, EquivalenciaResumen
from app.models.equivalencia import EquivalenciaResponse

# Definición de la ruta /equivalencias
router = APIRouter(
    prefix="/equivalencias", 
    tags=["Equivalencias Farmacéuticas"]
)

# Consulta Base con detalles de medicamentos
_MED_SELECT = """
    SELECT DISTINCT
        m.id_med, m.nom_comercial, m.laboratorio,
        p.iso_code, p.nom_pais,
        ff.descripcion AS forma_farmaceutica,
        va.descripcion AS via_administracion,
        m.dosaje
    FROM med.medicamento m
    JOIN med.pais p ON m.id_pais = p.id_pais
    LEFT JOIN med.forma_farmaceutica ff ON m.id_forma = ff.id_forma
    LEFT JOIN med.via_administracion va ON m.id_via = va.id_via
"""

# Tope de seguridad para no traer miles de filas del SQL
_SQL_CAP = 1000

# Definición del Límite de Búsqueda
def _limit_per_country(rows: list, n: int) -> list:
    """Devuelve los primeros n resultados por cada iso_code."""
    counts: dict = {}
    result = []
    for row in rows:
        iso = row["iso_code"]
        if counts.get(iso, 0) < n:
            result.append(row)
            counts[iso] = counts.get(iso, 0) + 1
    return result

# Endpoint de Equivalencia Farmacéutica según ID de Medicamento
@router.get("/id_med", response_model=EquivalenciaResponse)
def equivalencias_por_medicamento(
    id_med: int,
    pais: list[str] | None = Query(default=None, description="Filtrar equivalentes por código ISO del país destino (repetir para varios: ?pais=ES&pais=CL)"),
    limit: int = Query(default=100, ge=1, le=500, description="Máximo de resultados por país en cada lista"),
    db: connection = Depends(get_db),
):
    # Detalles del Endpoint dentro del DocStrings
    """
    Devuelve equivalencias internacionales de un medicamento.
    - por_atc: medicamentos de otros países que comparten código ATC (criterio primario).
    - por_principio_activo: medicamentos de otros países que comparten principio activo
      y no aparecen ya en por_atc (cubre países sin ATC asignado como Chile o Portugal).
    El parámetro limit aplica por país, no sobre el total.
    """
    with db.cursor() as cur:
        # Datos del Medicamento Origen
        cur.execute(
            _MED_SELECT + " WHERE m.id_med = %s",
            (id_med,),
        )
        origen = cur.fetchone()
        if not origen:
            raise HTTPException(status_code=404, detail="Medicamento no encontrado")

        iso_origen = origen["iso_code"]

        # Código ATC del Origen
        cur.execute(
            "SELECT id_atc FROM med.identificado_por WHERE id_med = %s",
            (id_med,),
        )
        atc_ids = [row["id_atc"] for row in cur.fetchall()]

        # Principio Activo del Origen
        cur.execute(
            "SELECT id_pa FROM med.contiene WHERE id_med = %s",
            (id_med,),
        )
        pa_ids = [row["id_pa"] for row in cur.fetchall()]

        # ATCs inferidos via asociado_con - Para Chile y Portugal
        # Solo se aceptan ATCs que tengan al menos un med monocomponente con ese PA,
        # para evitar arrastrar ATCs de combos (e.g. M01AE51 ibuprofen+codeine).
        if pa_ids:
            cur.execute(
                """
                SELECT DISTINCT ac.id_atc
                FROM med.asociado_con ac
                WHERE ac.id_pa = ANY(%s)
                AND ac.id_atc IN (
                    SELECT i.id_atc
                    FROM med.identificado_por i
                    WHERE i.id_med IN (
                        SELECT id_med FROM med.contiene
                        GROUP BY id_med HAVING COUNT(*) = 1
                    )
                    AND i.id_med IN (
                        SELECT id_med FROM med.contiene WHERE id_pa = ANY(%s)
                    )
                )
                """,
                (pa_ids, pa_ids),
            )
            pa_derived_atcs = [r["id_atc"] for r in cur.fetchall() if r["id_atc"] not in atc_ids]
        else:
            pa_derived_atcs = []

        all_atc_ids = atc_ids + pa_derived_atcs

        # --- Filtrado por Código ATC (directo {ES, CA, US} + inferido via PA {CL, PT}) ---
        por_atc = []
        ids_por_atc = []
        if all_atc_ids:
            sql_atc = (
                _MED_SELECT
                + """
                JOIN med.identificado_por ip ON m.id_med = ip.id_med
                WHERE ip.id_atc = ANY(%(atc_ids)s)
                  AND p.iso_code != %(iso_origen)s
                  AND m.id_med != %(id_med)s
                """
            )
            
            params_atc: dict = {"atc_ids": all_atc_ids, "iso_origen": iso_origen, "id_med": id_med}

            if pais:
                sql_atc += " AND p.iso_code = ANY(%(pais)s)"
                params_atc["pais"] = [p.upper() for p in pais]

            sql_atc += " ORDER BY p.nom_pais, m.nom_comercial LIMIT %(cap)s"
            params_atc["cap"] = _SQL_CAP
            cur.execute(sql_atc, params_atc)
            all_atc_rows = cur.fetchall()

            # ids_por_atc incluye TODOS los matches ATC para excluirlos correctamente de por_pa
            ids_por_atc = [row["id_med"] for row in all_atc_rows]
            por_atc = [EquivalenciaResumen(**row) for row in _limit_per_country(all_atc_rows, limit)]

        # --- Filtrado por Principio Activo {CL, PT} ---
        por_pa = []
        if pa_ids:
            sql_pa = (
                _MED_SELECT
                + """
                JOIN med.contiene c ON m.id_med = c.id_med
                WHERE c.id_pa = ANY(%(pa_ids)s)
                  AND p.iso_code != %(iso_origen)s
                  AND m.id_med != %(id_med)s
                """
            )

            params_pa: dict = {"pa_ids": pa_ids, "iso_origen": iso_origen, "id_med": id_med}

            if ids_por_atc:
                sql_pa += " AND m.id_med != ALL(%(ids_por_atc)s)"
                params_pa["ids_por_atc"] = ids_por_atc

            if pais:
                sql_pa += " AND p.iso_code = ANY(%(pais)s)"
                params_pa["pais"] = [p.upper() for p in pais]

            sql_pa += " ORDER BY p.nom_pais, m.nom_comercial LIMIT %(cap)s"
            params_pa["cap"] = _SQL_CAP
            cur.execute(sql_pa, params_pa)
            por_pa = [EquivalenciaResumen(**row) for row in _limit_per_country(cur.fetchall(), limit)]

    return EquivalenciaResponse(
        medicamento_origen=MedicamentoResumen(**origen),
        por_atc=por_atc,
        por_principio_activo=por_pa,
    )