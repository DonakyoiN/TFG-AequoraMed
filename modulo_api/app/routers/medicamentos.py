from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Literal
from psycopg2.extensions import connection
from app.database import get_db
from app.models.medicamento import MedicamentoResumen, MedicamentoDetalle

# Definición de la ruta /medicamentos
router = APIRouter(
    prefix="/medicamentos",
    tags=["Medicamentos"]
)

# Endpoint de Búsqueda Global de Medicamentos
@router.get("/buscar", response_model=list[MedicamentoResumen])
def buscar_medicamentos(
    q: str = Query(min_length=2, description="Texto a buscar"),
    modo: Literal["todo", "nombre", "principio_activo", "atc", "registro"] = Query(default="todo", description="Campo sobre el que buscar"),
    pais: list[str] | None = Query(default=None, description="Filtrar por código ISO del país, repetible (?pais=ES&pais=CL)"),
    forma: str | None = Query(default=None, description="Filtrar por forma farmacéutica (ILIKE)"),
    via: str | None = Query(default=None, description="Filtrar por vía de administración (ILIKE)"),
    laboratorio: str | None = Query(default=None, description="Filtrar por laboratorio (ILIKE)"),
    limit: int = Query(default=50, ge=1, le=200, description="Número máximo de resultados"),
    offset: int = Query(default=0, ge=0, description="Desplazamiento para paginación"),
    db: connection = Depends(get_db),
):
    """
    Búsqueda global de medicamentos.
    - modo=nombre: Búsqueda por Nombre Comercial del medicamento.
    - modo=principio_activo: Búsqueda por Principio Activo del medicamento.
    - modo=atc: Búsqueda por Código ATC del medicamento.
    - modo=registro: Búsqueda por Número de Registro del país (reg_pais).
    - modo=todo (defecto): OR de los cuatro criterios anteriores.
    Admite filtros adicionales por país, forma farmacéutica, vía y laboratorio, más paginación.
    """
    q_like = f"%{q}%"

    # Cláusulas WHERE según el modo de búsqueda - Insensible a mayúsculas/acentos con extensión unaccent
    if modo == "nombre":
        where_busqueda = "f_unaccent(m.nom_comercial) ILIKE f_unaccent(%(q)s)"
    elif modo == "principio_activo":
        where_busqueda = "EXISTS (SELECT 1 FROM med.contiene c JOIN med.principio_activo pa ON c.id_pa = pa.id_pa WHERE c.id_med = m.id_med AND f_unaccent(pa.nom_estandar) ILIKE f_unaccent(%(q)s))"
    elif modo == "atc":
        where_busqueda = "EXISTS (SELECT 1 FROM med.identificado_por ip JOIN med.atc a ON ip.id_atc = a.id_atc WHERE ip.id_med = m.id_med AND a.code_atc ILIKE %(q)s)"
    elif modo == "registro":
        where_busqueda = "m.reg_pais ILIKE %(q)s"
    else:
        where_busqueda = """(
            f_unaccent(m.nom_comercial) ILIKE f_unaccent(%(q)s)
            OR m.reg_pais ILIKE %(q)s
            OR EXISTS (SELECT 1 FROM med.contiene c JOIN med.principio_activo pa ON c.id_pa = pa.id_pa WHERE c.id_med = m.id_med AND f_unaccent(pa.nom_estandar) ILIKE f_unaccent(%(q)s))
            OR EXISTS (SELECT 1 FROM med.identificado_por ip JOIN med.atc a ON ip.id_atc = a.id_atc WHERE ip.id_med = m.id_med AND a.code_atc ILIKE %(q)s)
        )"""

    # Consulta con los detalles del Medicamento
    sql = f"""
        SELECT
            m.id_med, m.nom_comercial, m.laboratorio,
            p.iso_code, p.nom_pais,
            ff.descripcion AS forma_farmaceutica,
            va.descripcion AS via_administracion
        FROM med.medicamento m
        JOIN med.pais p ON m.id_pais = p.id_pais
        LEFT JOIN med.forma_farmaceutica ff ON m.id_forma = ff.id_forma
        LEFT JOIN med.via_administracion va ON m.id_via = va.id_via
        WHERE {where_busqueda}
    """
    params: dict = {"q": q_like}

    if pais:
        sql += " AND p.iso_code = ANY(%(pais)s)"
        params["pais"] = [p.upper() for p in pais]

    if forma:
        sql += " AND f_unaccent(ff.descripcion) ILIKE f_unaccent(%(forma)s)"
        params["forma"] = f"%{forma}%"

    if via:
        sql += " AND f_unaccent(va.descripcion) ILIKE f_unaccent(%(via)s)"
        params["via"] = f"%{via}%"

    if laboratorio:
        sql += " AND f_unaccent(m.laboratorio) ILIKE f_unaccent(%(laboratorio)s)"
        params["laboratorio"] = f"%{laboratorio}%"

    sql += " ORDER BY m.nom_comercial LIMIT %(limit)s OFFSET %(offset)s"
    params["limit"] = limit
    params["offset"] = offset

    with db.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [MedicamentoResumen(**row) for row in rows]

# Endpoint de Búsqueda de un Medicamento mediante ID
@router.get("/id_med", response_model=MedicamentoDetalle)
def detalle_medicamento(id_med: int, db: connection = Depends(get_db)):
    
    """
    Devuelve los detalles completos del Medicamento según su ID dentro de la Base de Datos. 
    Contiene información del código ATC y el Principio Activo.
    """

    with db.cursor() as cur:
        # Consulta de Búsqueda - Detalles del Medicamento
        cur.execute(
            """
            SELECT
                m.id_med, m.nom_comercial, m.laboratorio,
                m.reg_pais, m.dosaje,
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
    