import re
from psycopg2.extras import execute_values
from scripts.database import get_connection

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
        SELECT nregistro, nombre, labtitular, forma_farmaceutica, vias_administracion, dosis
        FROM fuentes.spain_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        reg_pais, nom, lab, forma, vias, dosis = row
        if not reg_pais: continue
        id_f = dict_forma.get(forma.strip().upper()) if forma and forma.strip() else None
        id_v = None
        if vias and vias.strip():
            id_v = dict_via.get(vias.split(',')[0].strip().upper())
        dosaje = dosis.strip().lower() if dosis and dosis.strip() else None
        to_insert.append((id_pais, str(reg_pais), nom, lab, dosaje, id_f, id_v))

    if to_insert:
        execute_values(cursor, "INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, dosaje, id_forma, id_via) VALUES %s", to_insert)

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
        to_insert.append((id_pais, str(reg_pais), nom, lab, None, None, None))

    if to_insert:
        execute_values(cursor, "INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, dosaje, id_forma, id_via) VALUES %s", to_insert)

# Carga de datos de CanadaHealth Canadá
def insert_canada(cursor, dict_pais, dict_forma, dict_via):
    print("Insertando medicamentos de Canadá...")
    id_pais = dict_pais.get('CA')
    cursor.execute("DELETE FROM med.medicamento WHERE id_pais = %s", (id_pais,))

    cursor.execute("""
        SELECT din, brand_name, company_name, pharmaceutical_form, route_administration, strength
        FROM fuentes.canada_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        reg_pais, nom, lab, forma, vias, strength = row
        if not reg_pais: continue
        id_f = dict_forma.get(forma.strip().upper()) if forma and forma.strip() else None
        id_v = None
        if vias and vias.strip():
            id_v = dict_via.get(vias.split(',')[0].strip().upper())
        dosaje = strength.strip().lower() if strength and strength.strip() and strength.strip() != 'N/A' else None
        to_insert.append((id_pais, str(reg_pais), nom, lab, dosaje, id_f, id_v))

    if to_insert:
        execute_values(cursor, "INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, dosaje, id_forma, id_via) VALUES %s", to_insert)

# Carga de datos RxNorm+DrugsFDA Estados Unidos
def insert_usa(cursor, dict_pais, dict_forma, dict_via):
    print("Insertando medicamentos de Estados Unidos...")
    id_pais = dict_pais.get('US')
    cursor.execute("DELETE FROM med.medicamento WHERE id_pais = %s", (id_pais,))

    cursor.execute("""
        SELECT application_number, brand_name, sponsor_name, dosage_form, route_administration, strength
        FROM fuentes.usa_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        reg_pais, nom, lab, forma, vias, strength = row
        if not reg_pais: continue
        id_f = dict_forma.get(forma.strip().upper()) if forma and forma.strip() else None
        id_v = None
        if vias and vias.strip():
            id_v = dict_via.get(vias.split(',')[0].strip().upper())
        if strength and strength.strip() and strength.strip() != 'N/A':
            dosaje = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', strength.strip().lower())
        else:
            dosaje = None
        to_insert.append((id_pais, str(reg_pais), nom, lab, dosaje, id_f, id_v))

    if to_insert:
        execute_values(cursor, "INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, dosaje, id_forma, id_via) VALUES %s", to_insert)

# Carga de datos de Infamed Portugal
def insert_portugal(cursor, dict_pais, dict_forma):
    print("Insertando medicamentos de Portugal...")
    id_pais = dict_pais.get('PT')
    cursor.execute("DELETE FROM med.medicamento WHERE id_pais = %s", (id_pais,))

    cursor.execute("""
        SELECT id_ptmet, product_name, ma_holder, dose_form, strength
        FROM fuentes.portugal_med
    """)
    to_insert = []
    for row in cursor.fetchall():
        reg_pais, nom, lab, forma, strength = row
        if not reg_pais: continue
        id_f = dict_forma.get(forma.strip().upper()) if forma and forma.strip() else None
        dosaje = strength.strip().lower() if strength and strength.strip() and strength.strip() != 'N/A' else None
        to_insert.append((id_pais, str(reg_pais), nom.upper() if nom else nom, lab, dosaje, id_f, None))

    if to_insert:
        execute_values(cursor, "INSERT INTO med.medicamento (id_pais, reg_pais, nom_comercial, laboratorio, dosaje, id_forma, id_via) VALUES %s", to_insert)

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
