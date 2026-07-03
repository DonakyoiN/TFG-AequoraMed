import psycopg2
import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv

load_dotenv()

# Consultas sobre la schema 'fuentes' (datos crudos pre-ETL)
# has_atc=1 → país con ATC propio (ES, CA, US) | has_atc=0 → sin ATC (CL, PT)
COUNTRY_QUERIES: dict[str, tuple[str, str]] = {
    'España':         ("SELECT 'España' AS pais, principios_activos AS principio_activo, atc AS atc_code, nombre AS nombre_comercial, labtitular AS laboratorio, 1 AS has_atc FROM fuentes.spain_med", 'España'),
    'Chile':          ("SELECT 'Chile' AS pais, principio_activo, 'N/A' AS atc_code, nombre_comercial, empresa AS laboratorio, 0 AS has_atc FROM fuentes.chile_med", 'Chile'),
    'Canadá':         ("SELECT 'Canadá' AS pais, ingredient_name AS principio_activo, atc_number AS atc_code, brand_name AS nombre_comercial, company_name AS laboratorio, 1 AS has_atc FROM fuentes.canada_med", 'Canadá'),
    'Estados Unidos': ("SELECT 'Estados Unidos' AS pais, name_ingredient AS principio_activo, id_atc AS atc_code, brand_name AS nombre_comercial, sponsor_name AS laboratorio, 1 AS has_atc FROM fuentes.usa_med", 'Estados Unidos'),
    'Portugal':       ("SELECT 'Portugal' AS pais, active_substance AS principio_activo, 'N/A' AS atc_code, product_name AS nombre_comercial, ma_holder AS laboratorio, 0 AS has_atc FROM fuentes.portugal_med", 'Portugal'),
}


def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "db_med"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )


def search(
    term: str,
    origen: str,
    objetivo: str,
    tree: ttk.Treeview,
    status_var: tk.StringVar,
) -> None:
    for item in tree.get_children():
        tree.delete(item)

    if not term.strip():
        messagebox.showwarning("Advertencia", "Por favor ingresa un término a buscar.")
        return

    status_var.set("Buscando en la base de datos...")
    tree.update()

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # CTE: origen siempre presente; objetivo solo si difiere
        queries_list = [COUNTRY_QUERIES[origen][0]]
        if origen != objetivo:
            queries_list.append(COUNTRY_QUERIES[objetivo][0])

        base_cte = f"WITH combinados AS ({' UNION ALL '.join(queries_list)})"
        origen_name = COUNTRY_QUERIES[origen][1]

        # --- Fase 1: Candidatos en el País Origen ---
        search_query = (
            base_cte
            + " SELECT DISTINCT principio_activo, atc_code, nombre_comercial"
            + " FROM combinados"
            + " WHERE pais = %s AND (nombre_comercial ILIKE %s OR principio_activo ILIKE %s OR atc_code ILIKE %s)"
        )
        cur.execute(search_query, (origen_name, f"%{term}%", f"%{term}%", f"%{term}%"))
        matches = cur.fetchall()

        if not matches:
            status_var.set(f"No se encontró ningún medicamento relacionado con '{term}' en {origen_name}.")
            return

        # Extraer ATCs y PAs de los candidatos encontrados
        atcs: set[str] = set()
        pas: set[str] = set()
        for pa, atc, _ in matches:
            if atc and atc.strip() and atc.strip() != 'N/A':
                atcs.add(atc.strip())
            if pa and pa.strip():
                pas.add(pa.strip())

        atcs_list = list(atcs)
        pas_list = list(pas)
        pa_params = [f"%{pa}%" for pa in pas_list]

        # --- Fase 2: Construcción del WHERE de Equivalencias ---
        # has_atc=1 (ES/CA/US): ATC directo; fallback a PA si el drug no tiene ATC en la row
        # has_atc=0 (CL/PT): solo por Principio Activo
        where_clauses: list[str] = []
        params: list = []

        if atcs_list:
            atc_placeholders = ', '.join(['%s'] * len(atcs_list))
            atc_cond = f"atc_code IN ({atc_placeholders})"

            if pas_list:
                pa_cond = f"({' OR '.join(['principio_activo ILIKE %s'] * len(pas_list))})"
                no_atc_row = "(atc_code IS NULL OR atc_code = '' OR atc_code = 'N/A')"

                where_clauses.append(f"(has_atc = 1 AND ({atc_cond} OR ({no_atc_row} AND {pa_cond})))")
                params.extend(atcs_list)
                params.extend(pa_params)

                where_clauses.append(f"(has_atc = 0 AND {pa_cond})")
                params.extend(pa_params)
            else:
                where_clauses.append(f"(has_atc = 1 AND {atc_cond})")
                params.extend(atcs_list)

        elif pas_list:
            where_clauses.append(f"({' OR '.join(['principio_activo ILIKE %s'] * len(pas_list))})")
            params.extend(pa_params)
        else:
            status_var.set("Error: No se extrajeron criterios válidos para la equivalencia.")
            return

        # --- Consulta Final de Equivalencias ---
        final_query = (
            base_cte
            + " SELECT pais, principio_activo, atc_code, nombre_comercial, laboratorio"
            + f" FROM combinados WHERE ({' OR '.join(where_clauses)})"
            + " ORDER BY pais DESC, nombre_comercial ASC"
        )
        cur.execute(final_query, tuple(params))
        results = cur.fetchall()

        for row in results:
            tree.insert("", "end", values=(row[0] or '', row[1] or '', row[2] or '', row[3] or '', row[4] or ''))

        status_var.set(f"'{term}' ({origen} → {objetivo}): {len(results)} resultados encontrados.")

    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error:\n{str(e)}")
        status_var.set("Error durante la ejecución.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def run_gui() -> None:
    root = tk.Tk()
    root.title("Herramienta de Validación de Equivalencias — Datos Crudos (fuentes.*)")
    root.geometry("1200x650")
    root.minsize(900, 500)

    countries = list(COUNTRY_QUERIES.keys())

    # Barra de Controles Superior
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

    ttk.Label(top_frame, text="Término:").pack(side=tk.LEFT, padx=(20, 5))
    term_var = tk.StringVar()
    ttk.Entry(top_frame, textvariable=term_var, width=25).pack(side=tk.LEFT, padx=5)

    status_var = tk.StringVar(value="Listo.")

    def _do_search() -> None:
        search(term_var.get(), cb_origen.get(), cb_objetivo.get(), tree, status_var)

    ttk.Button(top_frame, text="Buscar Equivalencias", command=_do_search).pack(side=tk.LEFT, padx=5)

    root.bind('<Return>', lambda _: _do_search())

    # Tabla de Resultados
    bottom_frame = ttk.Frame(root, padding=10)
    bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    columns = ("pais", "principio_activo", "atc_code", "nombre_comercial", "laboratorio")
    tree = ttk.Treeview(bottom_frame, columns=columns, show="headings", selectmode="browse")

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

    scrollbar = ttk.Scrollbar(bottom_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Barra de Estado
    ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W, padding=2).pack(side=tk.BOTTOM, fill=tk.X)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
