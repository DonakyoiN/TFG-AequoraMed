
-- Tabla para almacenar las medicinas de CIMA Rest API para España
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