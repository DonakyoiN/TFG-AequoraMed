
-- Tabla para almacenar los medicamentos de CIMA Rest API para España
CREATE TABLE spain_med(
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
CREATE TABLE chile_med (
    registro                TEXT,
    nombre_comercial        TEXT,
    fecha_registro          TEXT,
    empresa                 TEXT,
    principio_activo        TEXT,
    control_legal           TEXT,

    PRIMARY KEY (registro)
);

-- Tabla para almacenar los medicamentos del Drug Product Database (DPD) para Canadá
CREATE TABLE canada_med(
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
CREATE TABLE usa_med(
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
CREATE TABLE portugal_med(
    id_ptmet                SERIAL,
    active_substance        TEXT,
    product_name            TEXT,
    dose_form               TEXT,
    strength                TEXT,
    ma_holder               TEXT,
    ma_status               TEXT,
    marketing               TEXT,

    PRIMARY KEY (id_ptmet )
);