
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
    registro TEXT,
    nombre_comercial TEXT,
    fecha_registro TEXT,
    empresa TEXT,
    principio_activo TEXT,
    control_legal TEXT,

    PRIMARY KEY (registro)
);