import psycopg2
import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv

# Consultas SQL
COUNTRY_QUERIES = {
    'España': ("SELECT 'España' as pais, principios_activos as principio_activo, atc as atc_code, nombre as nombre_comercial, labtitular as laboratorio, 1 as has_atc FROM fuentes.spain_med", 'España'),
    'Chile': ("SELECT 'Chile' as pais, principio_activo, 'N/A' as atc_code, nombre_comercial, empresa as laboratorio, 0 as has_atc FROM fuentes.chile_med", 'Chile'),
    'Canadá': ("SELECT 'Canadá' as pais, ingredient_name as principio_activo, atc_number as atc_code, brand_name as nombre_comercial, company_name as laboratorio, 1 as has_atc FROM fuentes.canada_med", 'Canadá'),
    'Estados Unidos': ("SELECT 'Estados Unidos' as pais, name_ingredient as principio_activo, id_atc as atc_code, brand_name as nombre_comercial, sponsor_name as laboratorio, 1 as has_atc FROM fuentes.usa_med", 'Estados Unidos'),
    'Portugal': ("SELECT 'Portugal' as pais, active_substance as principio_activo, 'N/A' as atc_code, product_name as nombre_comercial, ma_holder as laboratorio, 0 as has_atc FROM fuentes.portugal_med", 'Portugal')
}

def get_connection():
    load_dotenv()
    db_name = os.getenv("DB_NAME", "db_med")
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASS", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    
    return psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )

def search(term, origen, objetivo, tree, status_var):
    # Limpiar tabla
    for item in tree.get_children():
        tree.delete(item)
        
    if not term.strip():
        messagebox.showwarning("Advertencia", "Por favor ingresa un término a buscar.")
        return
        
    status_var.set("Buscando en la base de datos...")
    
    # Asegurar actualización de UI
    tree.update()

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        queries_list = []
        if origen == objetivo:
            queries_list.append(COUNTRY_QUERIES[origen][0])
        else:
            queries_list.append(COUNTRY_QUERIES[origen][0])
            queries_list.append(COUNTRY_QUERIES[objetivo][0])
            
        base_query = f"WITH combinados AS ({' UNION ALL '.join(queries_list)})"
        
        origen_name = COUNTRY_QUERIES[origen][1]
        search_query = base_query + " SELECT DISTINCT principio_activo, atc_code, nombre_comercial FROM combinados WHERE pais = %s AND (nombre_comercial ILIKE %s OR principio_activo ILIKE %s OR atc_code ILIKE %s)"
        
        search_term = f"%{term}%"
        cur.execute(search_query, (origen_name, search_term, search_term, search_term))
        matches = cur.fetchall()
        
        if not matches:
            status_var.set(f"No se encontró ningún medicamento relacionado con '{term}' en {origen_name}.")
            return
            
        atcs = set()
        pas = set()
        
        for pa, atc, nom in matches:
            if atc and atc.strip() and atc.strip() != 'N/A':
                atcs.add(atc.strip())
            if pa and pa.strip():
                pas.add(pa.strip())
                
        atcs_list = list(atcs)
        pas_list = list(pas)
        
        atc_cond_template = ""
        if atcs_list:
            placeholders = ', '.join(['%s'] * len(atcs_list))
            atc_cond_template = f"atc_code IN ({placeholders})"
            
        pa_cond_template = ""
        pa_params = [f"%{pa}%" for pa in pas_list]
        if pas_list:
            pa_subconds = ["principio_activo ILIKE %s" for _ in pas_list]
            pa_cond_template = "(" + " OR ".join(pa_subconds) + ")"

        where_clauses = []
        params = []
        
        if atcs_list:
            if pa_cond_template:
                # Países CON ATC
                where_clauses.append(f"(has_atc = 1 AND ({atc_cond_template} OR (atc_code IS NULL OR atc_code = '' OR atc_code = 'N/A') AND {pa_cond_template}))")
                params.extend(atcs_list)
                params.extend(pa_params) 
                
                # Países SIN ATC
                where_clauses.append(f"(has_atc = 0 AND {pa_cond_template})")
                params.extend(pa_params)
            else:
                where_clauses.append(f"(has_atc = 1 AND {atc_cond_template})")
                params.extend(atcs_list)
        elif pa_cond_template:
            where_clauses.append(pa_cond_template)
            params.extend(pa_params)
        else:
            status_var.set("Error: No se extrajeron criterios válidos para la equivalencia.")
            return

        final_cond = " OR ".join(where_clauses)
        
        final_query = base_query + f" SELECT pais, principio_activo, atc_code, nombre_comercial, laboratorio FROM combinados WHERE {final_cond} ORDER BY pais DESC, nombre_comercial ASC"
        
        cur.execute(final_query, tuple(params))
        results = cur.fetchall()
        
        for row in results:
            tree.insert("", "end", values=(row[0] or '', row[1] or '', row[2] or '', row[3] or '', row[4] or ''))
            
        status_var.set(f"Busca '{term}' (Origen: {origen} -> Obj: {objetivo}). Encontradas {len(results)} equivalencias.")
        
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error:\n{str(e)}")
        status_var.set("Error durante la ejecución.")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def run_gui():
    root = tk.Tk()
    root.title("Buscador de Equivalencias Farmacéuticas (GUI)")
    root.geometry("1100x650")
    
    # Opciones de Paises
    countries = list(COUNTRY_QUERIES.keys())
    
    # Barra Superior
    top_frame = ttk.Frame(root, padding=10)
    top_frame.pack(side=tk.TOP, fill=tk.X)
    
    ttk.Label(top_frame, text="Origen:").pack(side=tk.LEFT, padx=5)
    cb_origen = ttk.Combobox(top_frame, values=countries, state="readonly", width=12)
    cb_origen.set("Chile")
    cb_origen.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(top_frame, text="Objetivo:").pack(side=tk.LEFT, padx=5)
    cb_objetivo = ttk.Combobox(top_frame, values=countries, state="readonly", width=12)
    cb_objetivo.set("España")
    cb_objetivo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(top_frame, text="Término a buscar (Ej: Paracetamol):").pack(side=tk.LEFT, padx=(20, 5))
    term_var = tk.StringVar()
    entry_term = ttk.Entry(top_frame, textvariable=term_var, width=30)
    entry_term.pack(side=tk.LEFT, padx=5)
    
    status_var = tk.StringVar(value="Listo.")
    
    btn_buscar = ttk.Button(top_frame, text="Buscar Equivalencias", command=lambda: search(term_var.get(), cb_origen.get(), cb_objetivo.get(), tree, status_var))
    btn_buscar.pack(side=tk.LEFT, padx=10)
    
    # Bindeo para la tecla Enter
    root.bind('<Return>', lambda event: search(term_var.get(), cb_origen.get(), cb_objetivo.get(), tree, status_var))
    
    # Tabla Inferior
    bottom_frame = ttk.Frame(root, padding=10)
    bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    columns = ("pais", "principio_activo", "atc_code", "nombre_comercial", "laboratorio")
    tree = ttk.Treeview(bottom_frame, columns=columns, show="headings", selectmode="browse")
    
    # Configurar columnas
    tree.heading("pais", text="País")
    tree.heading("principio_activo", text="Principio Activo")
    tree.heading("atc_code", text="Código ATC")
    tree.heading("nombre_comercial", text="Nombre Comercial")
    tree.heading("laboratorio", text="Laboratorio")
    
    tree.column("pais", width=100, anchor=tk.W)
    tree.column("principio_activo", width=300, anchor=tk.W)
    tree.column("atc_code", width=80, anchor=tk.CENTER)
    tree.column("nombre_comercial", width=350, anchor=tk.W)
    tree.column("laboratorio", width=200, anchor=tk.W)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(bottom_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Barra de Estado (Status Bar)
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W, padding=2)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    root.mainloop()

if __name__ == "__main__":
    run_gui()
