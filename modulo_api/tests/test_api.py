import pytest
from fastapi.testclient import TestClient


# =============================================================================
# Búsqueda (GET /medicamentos/buscar)
# =============================================================================

# Buscar medicamentos mediante Nombre Comercial: Nurofen
def test_buscar_modo_nombre(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "nurofen", "modo": "nombre"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all("nom_comercial" in m and "iso_code" in m for m in data)

# Buscar medicamentos mediante Principio Activo: Paracetamol
def test_buscar_modo_principio_activo(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "paracetamol", "modo": "principio_activo"})
    assert r.status_code == 200
    assert len(r.json()) > 0

# Buscar medicamentos mediante ATC: M01AE01
def test_buscar_modo_atc(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "M01AE01", "modo": "atc"})
    assert r.status_code == 200
    assert len(r.json()) > 0

# Buscar medicamentos mediante Número de Registro: F-14035/24 (Chile)
def test_buscar_modo_registro(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "F-14035/24", "modo": "registro"})
    assert r.status_code == 200
    assert len(r.json()) > 0

# Buscar Aspirina en búsqueda general
def test_buscar_modo_todo(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "aspirina", "modo": "todo"})
    assert r.status_code == 200
    assert len(r.json()) > 0

# Búsqueda con Filtro de País
def test_buscar_filtro_pais(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "modo": "nombre", "pais": "ES"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(m["iso_code"] == "ES" for m in data)

# Búsqueda con Filtro de Forma Farmacéutica
def test_buscar_filtro_forma(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "forma": "comprimido"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(
        m["forma_farmaceutica"] is not None and "comprimido" in m["forma_farmaceutica"].lower()
        for m in data
    )

# Búsqueda con Filtro de Vía de Administración
def test_buscar_filtro_via(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "via": "oral"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(
        m["via_administracion"] is not None and "oral" in m["via_administracion"].lower()
        for m in data
    )

# Búsqueda con Filtro de Laboratorio
def test_buscar_filtro_laboratorio(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "laboratorio": "cinfa"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(
        m["laboratorio"] is not None and "cinfa" in m["laboratorio"].lower()
        for m in data
    )

# Búsqueda con todos los Filtros combinados — Amitron 500 MG Cápsulas Duras (ES)
def test_buscar_filtro_combinado(client: TestClient):
    r = client.get("/medicamentos/buscar", params={
        "q": "amitron",
        "modo": "nombre",
        "pais": "ES",
        "forma": "cápsula dura",
        "via": "oral",
        "laboratorio": "torlan",
    })
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(m["iso_code"] == "ES" for m in data)
    assert all(m["laboratorio"] is not None and "torlan" in m["laboratorio"].lower() for m in data)
    assert all(m["forma_farmaceutica"] is not None and "cápsula" in m["forma_farmaceutica"].lower() for m in data)
    assert all(m["via_administracion"] is not None and "oral" in m["via_administracion"].lower() for m in data)

# Búsqueda con parámetros insuficientes (un solo carácter)
def test_buscar_longitud_minima(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "a", "modo": "nombre"})
    assert r.status_code == 422

# Búsqueda con límite de resultados
def test_buscar_limit(client: TestClient):
    r = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "limit": 5})
    assert r.status_code == 200
    assert len(r.json()) <= 5


# =============================================================================
# Detalle (GET /medicamentos/id_med)
# =============================================================================

# Obtención de los detalles de un medicamento existente
def test_detalle_medicamento_existente(client: TestClient):
    r_list = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "modo": "todo", "limit": 1})
    id_med = r_list.json()[0]["id_med"]
    r = client.get("/medicamentos/id_med", params={"id_med": id_med})
    assert r.status_code == 200
    data = r.json()
    assert "principios_activos" in data
    assert "codigos_atc" in data
    assert isinstance(data["principios_activos"], list)
    assert isinstance(data["codigos_atc"], list)

# Obtención de los detalles de un medicamento que no existe
def test_detalle_medicamento_inexistente(client: TestClient):
    r = client.get("/medicamentos/id_med", params={"id_med": 999999999})
    assert r.status_code == 404


# =============================================================================
# Equivalencias (GET /equivalencias/id_med)
# =============================================================================

# Obtención de Equivalencias por Código ATC
def test_equivalencias_por_atc(client: TestClient):
    # Buscar por ATC M01AE01 en ES garantiza que el medicamento tiene ese código asignado
    r_list = client.get("/medicamentos/buscar", params={"q": "M01AE01", "modo": "atc", "pais": "ES", "limit": 1})
    id_med = r_list.json()[0]["id_med"]
    r = client.get("/equivalencias/id_med", params={"id_med": id_med})
    assert r.status_code == 200
    data = r.json()
    assert "por_atc" in data and "por_principio_activo" in data
    assert len(data["por_atc"]) > 0

# Obtención de Equivalencias por Principio Activo directo — Paracetamol (ES → CL/PT)
def test_equivalencias_por_pa(client: TestClient):
    # Paracetamol tiene ATC en ES (N02BE01), para CA/US van a por_atc
    # CL/PT comparten el mismo id_pa, aparecen en por_principio_activo
    r_list = client.get("/medicamentos/buscar", params={"q": "paracetamol", "modo": "principio_activo", "pais": "ES", "limit": 1})
    if not r_list.json():
        pytest.skip("No se encontró paracetamol en España")
    id_med = r_list.json()[0]["id_med"]
    r = client.get("/equivalencias/id_med", params={"id_med": id_med})
    assert r.status_code == 200
    data = r.json()
    assert len(data["por_principio_activo"]) > 0

# Obtención de Equivalencias por Inferencia — Chile (sin ATC propio)
def test_equivalencias_puente_pa_cl(client: TestClient):
    # Ibuprofeno de Chile (sin ATC propio) → equivalentes vía puente PA→ATC (asociado_con)
    r_list = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "modo": "nombre", "pais": "CL", "limit": 1})
    if not r_list.json():
        pytest.skip("No se encontró ibuprofeno en Chile")
    id_med = r_list.json()[0]["id_med"]
    r = client.get("/equivalencias/id_med", params={"id_med": id_med})
    assert r.status_code == 200
    data = r.json()
    assert len(data["por_atc"]) > 0 or len(data["por_principio_activo"]) > 0

# Obtención de Equivalencias por Inferencia — Portugal (sin ATC propio)
def test_equivalencias_puente_pa_pt(client: TestClient):
    # Ibuprofeno de Portugal (sin ATC propio) → equivalentes vía puente PA→ATC (asociado_con)
    r_list = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "modo": "nombre", "pais": "PT", "limit": 1})
    if not r_list.json():
        pytest.skip("No se encontró ibuprofeno en Portugal")
    id_med = r_list.json()[0]["id_med"]
    r = client.get("/equivalencias/id_med", params={"id_med": id_med})
    assert r.status_code == 200
    data = r.json()
    assert len(data["por_atc"]) > 0 or len(data["por_principio_activo"]) > 0

# Obtención de Equivalencias de diferentes idiomas - Caso Ibuprofeno/Ibuprofen
def test_equivalencias_cross_idioma(client: TestClient):
    r_list = client.get("/medicamentos/buscar", params={"q": "M01AE01", "modo": "atc", "pais": "ES", "limit": 1})
    id_med = r_list.json()[0]["id_med"]
    r = client.get("/equivalencias/id_med", params={"id_med": id_med})
    assert r.status_code == 200
    isos = {m["iso_code"] for m in r.json()["por_atc"]}
    assert "CA" in isos or "US" in isos

# Filtrar equivalencias a un país concreto
def test_equivalencias_filtro_destino(client: TestClient):
    # Filtrar equivalencias de ibuprofeno ES solo a Chile
    r_list = client.get("/medicamentos/buscar", params={"q": "ibuprofeno", "modo": "nombre", "pais": "ES", "limit": 1})
    id_med = r_list.json()[0]["id_med"]
    r = client.get("/equivalencias/id_med", params={"id_med": id_med, "pais": "CL"})
    assert r.status_code == 200
    data = r.json()
    todos = data["por_atc"] + data["por_principio_activo"]
    assert all(m["iso_code"] == "CL" for m in todos)
