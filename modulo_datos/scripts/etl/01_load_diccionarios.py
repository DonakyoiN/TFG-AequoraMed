import sys
import os
from db_conn import get_connection

# Insertar Países
def insert_paises(cursor):
    print("Insertando países...")
    paises = [
        ('ES', 'España'),
        ('CL', 'Chile'),
        ('CA', 'Canadá'),
        ('US', 'Estados Unidos'),
        ('PT', 'Portugal')
    ]
    cursor.execute("SELECT iso_code FROM med.pais")
    existing = {row[0] for row in cursor.fetchall()}
    to_insert = [p for p in paises if p[0] not in existing]
    
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.pais (iso_code, nom_pais)
            VALUES (%s, %s)
        """, to_insert)

# Insertar códigos ATC
def insert_atc(cursor):
    print("Extrayendo e insertando ATCs con sus descripciones (Mapeo heurístico)...")
    
    atc_desc_es = {}
    atc_desc_en = {}
    atc_set = set()

    # ESPAÑA -> desc_es
    cursor.execute("SELECT atc, principios_activos FROM fuentes.spain_med WHERE atc IS NOT NULL")
    for atc_val, pa_val in cursor.fetchall():
        if not atc_val: continue
        atc_parts = [v.strip() for v in atc_val.replace('/', ',').split(',')]
        pa_parts = []
        if pa_val:
            pa_parts = [v.strip().upper() for v in pa_val.replace(' y ', '/').replace('+', '/').split('/')]

        for i, code in enumerate(atc_parts):
            if code:
                atc_set.add(code)
                if not pa_parts: continue
                if len(atc_parts) == len(pa_parts):
                    atc_desc_es[code] = pa_parts[i]
                else:
                    atc_desc_es[code] = ' / '.join(pa_parts)

    # USA -> desc_en
    cursor.execute("SELECT id_atc, name_ingredient FROM fuentes.usa_med WHERE id_atc IS NOT NULL")
    for atc_val, pa_val in cursor.fetchall():
        if not atc_val: continue
        atc_parts = [v.strip() for v in atc_val.replace('/', ',').split(',')]
        pa_parts = []
        if pa_val:
            pa_parts = [v.strip().upper() for v in pa_val.replace(' AND ', '/').replace(' and ', '/').replace('+', '/').split('/')]

        for i, code in enumerate(atc_parts):
            if code:
                atc_set.add(code)
                if not pa_parts: continue
                if len(atc_parts) == len(pa_parts):
                    atc_desc_en[code] = pa_parts[i]
                else:
                    atc_desc_en[code] = ' / '.join(pa_parts)

    # CANADA -> desc_en
    cursor.execute("SELECT atc_number, ingredient_name FROM fuentes.canada_med WHERE atc_number IS NOT NULL")
    for atc_val, pa_val in cursor.fetchall():
        if not atc_val: continue
        atc_parts = [v.strip() for v in atc_val.replace('/', ',').split(',')]
        pa_parts = []
        if pa_val:
            pa_parts = [v.strip().upper() for v in pa_val.replace(' AND ', '/').replace(' and ', '/').replace('+', '/').split('/')]

        for i, code in enumerate(atc_parts):
            if code:
                atc_set.add(code)
                if code not in atc_desc_en:
                    if not pa_parts: continue
                    if len(atc_parts) == len(pa_parts):
                        atc_desc_en[code] = pa_parts[i]
                    else:
                        atc_desc_en[code] = ' / '.join(pa_parts)
                    
    cursor.execute("SELECT code_atc FROM med.atc")
    existing = {row[0] for row in cursor.fetchall()}
    to_insert = []
    
    for code in sorted(list(atc_set)):
        if code not in existing:
            desc_es = atc_desc_es.get(code)
            desc_en = atc_desc_en.get(code)
            to_insert.append((
                code,
                desc_es.title() if desc_es else None,
                desc_en.title() if desc_en else None
            ))
    
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.atc (code_atc, desc_es, desc_en)
            VALUES (%s, %s, %s)
        """, to_insert)

# Insertar Principios Activos
def insert_principios_activos(cursor):
    print("Extrayendo e insertando Principios Activos...")
    queries = [
        "SELECT principios_activos FROM fuentes.spain_med WHERE principios_activos IS NOT NULL",
        "SELECT principio_activo FROM fuentes.chile_med WHERE principio_activo IS NOT NULL",
        "SELECT ingredient_name FROM fuentes.canada_med WHERE ingredient_name IS NOT NULL",
        "SELECT name_ingredient FROM fuentes.usa_med WHERE name_ingredient IS NOT NULL",
        "SELECT active_substance FROM fuentes.portugal_med WHERE active_substance IS NOT NULL"
    ]
    
    pa_set = set()
    for query in queries:
        cursor.execute(query)
        for row in cursor.fetchall():
            val = row[0]
            if not val: continue
            val = val.replace(' y ', '/').replace(' AND ', '/').replace(' and ', '/').replace('+', '/')
            parts = [v.strip().title() for v in val.split('/')]
            for p in parts:
                if p: pa_set.add(p)

    cursor.execute("SELECT nom_estandar FROM med.principio_activo")
    existing = {row[0] for row in cursor.fetchall()}
    to_insert = [(pa,) for pa in sorted(list(pa_set)) if pa not in existing]
    
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.principio_activo (nom_estandar)
            VALUES (%s)
        """, to_insert)

# Insertar formas y vías
def insert_formas_vias(cursor):
    print("Extrayendo e insertando Formas y Vías...")
    # Formas farmacéuticas
    q_formas = [
        "SELECT forma_farmaceutica FROM fuentes.spain_med WHERE forma_farmaceutica IS NOT NULL",
        "SELECT pharmaceutical_form FROM fuentes.canada_med WHERE pharmaceutical_form IS NOT NULL",
        "SELECT dosage_form FROM fuentes.usa_med WHERE dosage_form IS NOT NULL",
        "SELECT dose_form FROM fuentes.portugal_med WHERE dose_form IS NOT NULL"
    ]
    formas_set = set()
    for q in q_formas:
        cursor.execute(q)
        for row in cursor.fetchall():
            val = row[0]
            if val and val.strip(): formas_set.add(val.strip().title())
                
    cursor.execute("SELECT descripcion FROM med.forma_farmaceutica")
    existing_formas = {row[0] for row in cursor.fetchall()}
    to_insert_formas = [(f,) for f in sorted(list(formas_set)) if f not in existing_formas]
    
    if to_insert_formas:
        cursor.executemany("""
            INSERT INTO med.forma_farmaceutica (descripcion)
            VALUES (%s)
        """, to_insert_formas)
    
    # Vías de Administración
    q_vias = [
        "SELECT vias_administracion FROM fuentes.spain_med WHERE vias_administracion IS NOT NULL",
        "SELECT route_administration FROM fuentes.canada_med WHERE route_administration IS NOT NULL",
        "SELECT route_administration FROM fuentes.usa_med WHERE route_administration IS NOT NULL"
    ]
    vias_set = set()
    for q in q_vias:
        cursor.execute(q)
        for row in cursor.fetchall():
            val = row[0]
            if not val: continue
            for v in val.split(','):
                if v.strip(): vias_set.add(v.strip().title())

    cursor.execute("SELECT descripcion FROM med.via_administracion")
    existing_vias = {row[0] for row in cursor.fetchall()}
    to_insert_vias = [(v,) for v in sorted(list(vias_set)) if v not in existing_vias]
    
    if to_insert_vias:
        cursor.executemany("""
            INSERT INTO med.via_administracion (descripcion)
            VALUES (%s)
        """, to_insert_vias)

def main():
    conn = get_connection()
    if conn is None: return
    try:
        cursor = conn.cursor()
        insert_paises(cursor)
        insert_atc(cursor)
        insert_principios_activos(cursor)
        insert_formas_vias(cursor)
        conn.commit()
        print("Diccionarios cargados en la base de datos correctamente.")
    except Exception as e:
        conn.rollback()
        print(f"Error procesando diccionarios: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
