import sys
import os
from db_conn import get_connection


def load_data_maps(cursor):
    # Obtener datos de País: id_pais y código ISO
    cursor.execute("SELECT iso_code, id_pais FROM med.pais")
    dict_pais = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Obtener datos de Medicamentos: id_med, id_pais y reg_pais
    cursor.execute("SELECT id_pais, reg_pais, id_med FROM med.medicamento")
    dict_med = {(row[0], row[1]): row[2] for row in cursor.fetchall()}
    
    # Obtener datos de ATCs: id_atc y Código ATC
    cursor.execute("SELECT code_atc, id_atc FROM med.atc")
    dict_atc = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Obtener datos de Principios Activos: id_pa y nombres estándar
    cursor.execute("SELECT nom_estandar, id_pa FROM med.principio_activo")
    dict_pa = {row[0]: row[1] for row in cursor.fetchall()}
    
    return dict_pais, dict_med, dict_atc, dict_pa

# Insertar relaciones Medicamento-ATC
def insert_identificado_por(cursor, dict_pais, dict_med, dict_atc):
    print("Insertando relaciones Medicamento - ATC...")
    to_insert = []
    
    # Consultas por País
    queries = [
        ('ES', "SELECT nregistro, atc FROM fuentes.spain_med WHERE atc IS NOT NULL"),
        ('CA', "SELECT drug_code, atc_number FROM fuentes.canada_med WHERE atc_number IS NOT NULL"),
        ('US', "SELECT application_number, id_atc FROM fuentes.usa_med WHERE id_atc IS NOT NULL")
    ]
    
    for code_pais, query in queries:
        id_pais = dict_pais.get(code_pais)
        cursor.execute(query)
        for reg, val in cursor.fetchall():
            if not val or not reg: continue
            id_med = dict_med.get((id_pais, str(reg)))
            if not id_med: continue
            parts = [v.strip() for v in val.replace('/', ',').split(',')]
            for p in parts:
                if p and p in dict_atc:
                    to_insert.append((id_med, dict_atc[p]))
    
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.identificado_por (id_med, id_atc)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, list(set(to_insert))) # set para quitar duplicados en el scope de Python

# Insertar relaciones Medicamento - Principio Activo
def insert_contiene(cursor, dict_pais, dict_med, dict_pa):
    print("Insertando relaciones Medicamento - Principio Activo...")
    to_insert = []
    
    # Consultas por País
    queries = [
        ('ES', "SELECT nregistro, principios_activos FROM fuentes.spain_med WHERE principios_activos IS NOT NULL"),
        ('CL', "SELECT registro, principio_activo FROM fuentes.chile_med WHERE principio_activo IS NOT NULL"),
        ('CA', "SELECT drug_code, ingredient_name FROM fuentes.canada_med WHERE ingredient_name IS NOT NULL"),
        ('US', "SELECT application_number as r_pais, name_ingredient FROM fuentes.usa_med WHERE name_ingredient IS NOT NULL"),
        ('PT', "SELECT id_ptmet::TEXT, active_substance FROM fuentes.portugal_med WHERE active_substance IS NOT NULL")
    ]
    
    for code_pais, query in queries:
        id_pais = dict_pais.get(code_pais)
        cursor.execute(query)
        for row in cursor.fetchall():
            reg, val = row
            if not reg or not val: continue
            id_med = dict_med.get((id_pais, str(reg)))
            if not id_med: continue
            
            val = val.replace(' y ', '/').replace(' AND ', '/').replace(' and ', '/').replace('+', '/')
            parts = [v.strip().upper() for v in val.split('/')]
            for p in parts:
                if p and p in dict_pa:
                    # Null para dosis_valor y dosis_unit por el momento - Probablemente lo termine quitando estos atributos
                    to_insert.append((id_med, dict_pa[p], None, None))
                    
    if to_insert:
        dedup_set = set(to_insert)
        cursor.executemany("""
            INSERT INTO med.contiene (id_med, id_pa, dosis_valor, dosis_unit)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, list(dedup_set))

def insert_asociado_con(cursor):
    print("Inhiriendo asociación ATC - Principio Activo...")
    
    cursor.execute("""
        INSERT INTO med.asociado_con (id_atc, id_pa)
        SELECT DISTINCT i.id_atc, c.id_pa 
        FROM med.identificado_por i
        JOIN med.contiene c ON i.id_med = c.id_med
        ON CONFLICT DO NOTHING
    """)

def main():
    conn = get_connection()
    if conn is None: return
    try:
        cursor = conn.cursor()
        
        # Limpieza de datos para actualizar relaciones
        cursor.execute("TRUNCATE med.identificado_por CASCADE")
        cursor.execute("TRUNCATE med.contiene CASCADE")
        cursor.execute("TRUNCATE med.asociado_con CASCADE")
        
        dict_pais, dict_med, dict_atc, dict_pa = load_data_maps(cursor)
        
        insert_identificado_por(cursor, dict_pais, dict_med, dict_atc)
        insert_contiene(cursor, dict_pais, dict_med, dict_pa)
        insert_asociado_con(cursor)
        
        conn.commit()
        print("Registros N:M insertados correctamente.")
    except Exception as e:
        conn.rollback()
        print(f"Error procesando relaciones M:N: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
