/*
  ||  DDL con la creación de Tablas para la base de datos ||
*/

-- FUENTES EXTERNAS
-- Tabla para almacenar los medicamentos de CIMA Rest API para España
CREATE TABLE fuentes.spain_med(
    nregistro               TEXT,
    atc                     TEXT,
    principios_activos      TEXT,
    nombre                  TEXT,
    labtitular              TEXT,
    dosis                   TEXT,
    vias_administracion     TEXT,
    forma_farmaceutica      TEXT,
    estado                  TEXT,
    cpresc                  TEXT,

    PRIMARY KEY (nregistro)
);

-- Tabla para almacenar los medicamentos deL ISPCh para Chile
CREATE TABLE fuentes.chile_med (
    registro                TEXT,
    nombre_comercial        TEXT,
    fecha_registro          TEXT,
    empresa                 TEXT,
    principio_activo        TEXT,
    control_legal           TEXT,

    PRIMARY KEY (registro)
);

-- Tabla para almacenar los medicamentos del Drug Product Database (DPD) para Canadá
CREATE TABLE fuentes.canada_med(
    drug_code                   TEXT,
    din                         TEXT,
    atc_number                  TEXT,
    ingredient_name             TEXT,
    brand_name                  TEXT,
    company_name                TEXT,
    class_name                  TEXT,
    strength                    TEXT,
    strength_unit               TEXT,
    route_administration        TEXT,
    pharmaceutical_form         TEXT,
    status                      TEXT,

    PRIMARY KEY (drug_code)
);

-- Tabla para almacernar los medicamentos de Estados Unidos: RxNorm + Drugs@FDA
CREATE TABLE fuentes.usa_med(
    rxnorm_id                   TEXT,
    application_number          TEXT,
    id_atc                      TEXT,
    name_ingredient             TEXT,
    brand_name                  TEXT,
    sponsor_name                TEXT,
    stength                     TEXT,
    route_administration        TEXT,
    dosage_form                 TEXT,
    marketing_status            TEXT,

    PRIMARY KEY (rxnorm_id, application_number)
);

-- Tabla para almacenar los medicamentos del INFAMED para Portugal
CREATE TABLE fuentes.portugal_med(
    id_ptmet                SERIAL,
    active_substance        TEXT,
    product_name            TEXT,
    dose_form               TEXT,
    strength                TEXT,
    ma_holder               TEXT,
    ma_status               TEXT,
    marketing               TEXT,

    PRIMARY KEY (id_ptmet)
);


-- MEDICAMENTOS
-- Tabla de Paises
CREATE TABLE med.pais(
    id_pais         SERIAL,
    iso_code        TEXT,
    nom_pais        TEXT,

    PRIMARY KEY (id_pais)
);

-- Tabla de codigos ATC
CREATE TABLE med.atc(
    id_atc          SERIAL,
    code_atc        TEXT,
    desc_es         TEXT,
    desc_en         TEXT,

    PRIMARY KEY (id_atc)
);

-- Tabla de Principios Activos
CREATE TABLE med.principio_activo(
    id_pa           SERIAL,
    nom_estandar    TEXT,
    nom_alterno     TEXT,

    PRIMARY KEY (id_pa)
);

-- Tabla de Formas Farmacéutica
CREATE TABLE med.forma_farmaceutica(
    id_forma        SERIAL,
    descripcion     TEXT,

    PRIMARY KEY (id_forma)
);

-- Tabla de Vías de Administración
CREATE TABLE med.via_administracion(
    id_via          SERIAL,
    descripcion     TEXT,

    PRIMARY KEY (id_via)
);

-- Tabla de Medicamentos
CREATE TABLE med.medicamento(
    id_med          SERIAL,
    id_atc          INT,
    id_pais         INT,
    reg_pais        TEXT,
    nom_comercial   TEXT,
    laboratorio     TEXT,
    id_forma        INT,
    id_via          INT,

    PRIMARY KEY (id_med),

    FOREIGN KEY (id_atc) REFERENCES med.atc (id_atc) ON DELETE CASCADE,
    FOREIGN KEY (id_pais) REFERENCES med.pais (id_pais) ON DELETE CASCADE,
    FOREIGN KEY (id_forma) REFERENCES med.forma_farmaceutica (id_forma) ON DELETE CASCADE,
    FOREIGN KEY (id_via) REFERENCES med.via_administracion (id_via) ON DELETE CASCADE     
);

-- Tabla N:M MEDICAMENTO-PRINCIPIO ACTIVO
CREATE TABLE med.contiene(
    id_med          INT,
    id_pa           INT,
    dosis_valor     FLOAT,
    dosis_unit      TEXT,

    PRIMARY KEY (id_med, id_pa),

    FOREIGN KEY (id_med) REFERENCES med.medicamento (id_med) ON DELETE CASCADE,
    FOREIGN KEY (id_pa) REFERENCES med.principio_activo (id_pa) ON DELETE CASCADE
);

