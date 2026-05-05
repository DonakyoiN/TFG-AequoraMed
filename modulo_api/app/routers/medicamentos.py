from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg2.extensions import connection
from app.database import get_db
from app.models.medicamento import MedicamentoResumen, MedicamentoDetalle


# Definición de la ruta /medicamentos
router = APIRouter(
    prefix="/medicamentos", 
    tags=["Medicamentos"]
)

# Endpoint de Búsqueda mediante Nombre Comercial o Principio Activo
@router.get("/busqueda_comercial", response_model=list[MedicamentoResumen])
def busqueda_comercial(
    q: str = Query(min_length=2, description="Nombre comercial o laboratorio"),
    pais: str | None = Query(default=None, description="Filtrar por código ISO del país (ES, CL, CA, US, PT)"),
    db: connection = Depends(get_db),
):
    # Consulta SQL de Búsqueda
    sql = """
        SELECT
            m.id_med, m.nom_comercial, m.laboratorio,
            p.iso_code, p.nom_pais,
            ff.descripcion AS forma_farmaceutica,
            va.descripcion AS via_administracion
        FROM med.medicamento m
        JOIN med.pais p ON m.id_pais = p.id_pais
        LEFT JOIN med.forma_farmaceutica ff ON m.id_forma = ff.id_forma
        LEFT JOIN med.via_administracion va ON m.id_via = va.id_via
        WHERE (
            m.nom_comercial ILIKE %(q)s
            OR m.laboratorio ILIKE %(q)s
        )
    """
    params: dict = {"q": f"%{q}%"}

    if pais:
        sql += " AND p.iso_code = %(pais)s"
        params["pais"] = pais.upper()

    sql += " ORDER BY m.nom_comercial LIMIT 50"

    with db.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [MedicamentoResumen(**row) for row in rows]

# Endpoint de Búsqueda de un Medicamento mediante ID
@router.get("/{id_med}", response_model=MedicamentoDetalle)
def detalle_medicamento(id_med: int, db: connection = Depends(get_db)):
    
    with db.cursor() as cur:
        # Consulta de Búsqueda - Detalles del Medicamento
        cur.execute(
            """
            SELECT
                m.id_med, m.nom_comercial, m.laboratorio,
                p.iso_code, p.nom_pais,
                ff.descripcion AS forma_farmaceutica,
                va.descripcion AS via_administracion
            FROM med.medicamento m
            JOIN med.pais p ON m.id_pais = p.id_pais
            LEFT JOIN med.forma_farmaceutica ff ON m.id_forma = ff.id_forma
            LEFT JOIN med.via_administracion va ON m.id_via = va.id_via
            WHERE m.id_med = %s
            """,
            (id_med,),
        )
        med = cur.fetchone()

    if not med:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado")

    with db.cursor() as cur:
        # Consulta de Búsqueda - Principio Activo
        cur.execute(
            """
            SELECT pa.id_pa, pa.nom_estandar
            FROM med.contiene c
            JOIN med.principio_activo pa ON c.id_pa = pa.id_pa
            WHERE c.id_med = %s
            """,
            (id_med,),
        )
        principios = cur.fetchall()

        # Consulta de Búsqueda - Código ATC
        cur.execute(
            """
            SELECT a.id_atc, a.code_atc, a.desc_es, a.desc_en
            FROM med.identificado_por ip
            JOIN med.atc a ON ip.id_atc = a.id_atc
            WHERE ip.id_med = %s
            """,
            (id_med,),
        )
        atcs = cur.fetchall()

    return MedicamentoDetalle(
        **med,
        principios_activos=[dict(p) for p in principios],
        codigos_atc=[dict(a) for a in atcs],
    )
    