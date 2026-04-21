import sys
import os
from db_conn import get_connection

# Carga de los países, vías de administración y forma farmacéutica
def load_catalog_maps(cursor):
    # Diccionario con los datos de País
    cursor.execute("SELECT iso_code, id_pais FROM med.pais")
    dict_pais = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Diccionario con los datos para Forma Farmacéutica
    cursor.execute("SELECT descripcion, id_forma FROM med.forma_farmaceutica")
    dict_forma = {row[0].upper(): row[1] for row in cursor.fetchall()}
    
    # Diccionario con los daots para Vía de Administración
    cursor.execute("SELECT descripcion, id_via FROM med.via_administracion")
    dict_via = {row[0].upper(): row[1] for row in cursor.fetchall()}
    
    return dict_pais, dict_forma, dict_via

# Carga de datos de CIMA API Rest España
def insert_spain(cursor, dict_pais, dict_forma, dict_via):
    print("Insertando medicamentos de España...")
    id_pais = dict_pais.get('ES')
    cursor.execute("DELETE FROM med.medicamento WHERE id_pais = %s", (id_pais,))
    
    cursor.execute("""
        SELECT nregistro, nombre, labtitular, forma_farmaceutica, vias_administracion 
        FROM fuentes.spain_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        reg_pais, nom, lab, forma, vias = row
        if not reg_pais: continue
        id_f = dict_forma.get(forma.strip().upper()) if forma and forma.strip() else None
        id_v = None
        if vias and vias.strip():
            id_v = dict_via.get(vias.split(',')[0].strip().upper())
        to_insert.append((id_pais, str(reg_pais), nom, lab, id_f, id_v))
        
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, id_forma, id_via)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, to_insert)

# Carga de datos de ISPCh Chile
def insert_chile(cursor, dict_pais):
    print("Insertando medicamentos de Chile...")
    id_pais = dict_pais.get('CL')
    cursor.execute("DELETE FROM med.medicamento WHERE id_pais = %s", (id_pais,))
    
    cursor.execute("""
        SELECT registro, nombre_comercial, empresa 
        FROM fuentes.chile_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        reg_pais, nom, lab = row
        if not reg_pais: continue
        to_insert.append((id_pais, str(reg_pais), nom, lab, None, None))
        
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, id_forma, id_via)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, to_insert)

# Carga de datos de CanadaHealth Canadá
def insert_canada(cursor, dict_pais, dict_forma, dict_via):
    print("Insertando medicamentos de Canadá...")
    id_pais = dict_pais.get('CA')
    cursor.execute("DELETE FROM med.medicamento WHERE id_pais = %s", (id_pais,))
    
    cursor.execute("""
        SELECT drug_code, brand_name, company_name, pharmaceutical_form, route_administration 
        FROM fuentes.canada_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        reg_pais, nom, lab, forma, vias = row
        if not reg_pais: continue
        id_f = dict_forma.get(forma.strip().upper()) if forma and forma.strip() else None
        id_v = None
        if vias and vias.strip():
            id_v = dict_via.get(vias.split(',')[0].strip().upper())
        to_insert.append((id_pais, str(reg_pais), nom, lab, id_f, id_v))
        
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, id_forma, id_via)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, to_insert)

# Carga de datos RxNorm+DrugsFDA Estados Unidos
def insert_usa(cursor, dict_pais, dict_forma, dict_via):
    print("Insertando medicamentos de Estados Unidos...")
    id_pais = dict_pais.get('US')
    cursor.execute("DELETE FROM med.medicamento WHERE id_pais = %s", (id_pais,))
    
    cursor.execute("""
        SELECT application_number, brand_name, sponsor_name, dosage_form, route_administration 
        FROM fuentes.usa_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        app, nom, lab, forma, vias = row
        reg_pais = app
        if not reg_pais: continue
        
        id_f = dict_forma.get(forma.strip().upper()) if forma and forma.strip() else None
        id_v = None
        if vias and vias.strip():
            id_v = dict_via.get(vias.split(',')[0].strip().upper())
        to_insert.append((id_pais, str(reg_pais), nom, lab, id_f, id_v))
        
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, id_forma, id_via)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, to_insert)

# Carga de datos de Infamed Portugal
def insert_portugal(cursor, dict_pais, dict_forma):
    print("Insertando medicamentos de Portugal...")
    id_pais = dict_pais.get('PT')
    cursor.execute("DELETE FROM med.medicamento WHERE id_pais = %s", (id_pais,))
    
    cursor.execute("""
        SELECT id_ptmet, product_name, ma_holder, dose_form 
        FROM fuentes.portugal_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        reg_pais, nom, lab, forma = row
        if not reg_pais: continue
        id_f = dict_forma.get(forma.strip().upper()) if forma and forma.strip() else None
        to_insert.append((id_pais, str(reg_pais), nom, lab, id_f, None))
        
    if to_insert:
        cursor.executemany("""
            INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, id_forma, id_via)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, to_insert)

def main():
    conn = get_connection()
    if conn is None: return
    try:
        cursor = conn.cursor()
        dict_pais, dict_forma, dict_via = load_catalog_maps(cursor)
        
        insert_spain(cursor, dict_pais, dict_forma, dict_via)
        insert_chile(cursor, dict_pais)
        insert_canada(cursor, dict_pais, dict_forma, dict_via)
        insert_usa(cursor, dict_pais, dict_forma, dict_via)
        insert_portugal(cursor, dict_pais, dict_forma)
        
        conn.commit()
        print("Registros de medicamentos insertados correctamente.")
    except Exception as e:
        conn.rollback()
        print(f"Error insertando tabla de medicamentos: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
