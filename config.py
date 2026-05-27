LP_HOST = "localhost"
LP_PORT = 5432
LP_USER = "postgres"
LP_PASS = "1234"
LP_DB = "ypfb_la_paz"

CBBA_HOST = "26.157.52.238"
CBBA_PORT = 3306
CBBA_USER = "root"
CBBA_PASS = "root"
CBBA_DB = "cochabamba"

SC_HOST = "26.82.89.70"
SC_PORT = 5432
SC_USER = "postgres"
SC_PASS = "RosmerY06011996"
SC_DB = "ypfb_santa_cruz"

COSTO_IMPORTACION_POR_LITRO = 8.50

SEDES = {
    "La Paz": {
        "icono": "\U0001f3d4\ufe0f",
        "badge": "Nodo Homogeneo \u2022 PostgreSQL 17",
        "color": "#003366",
        "descripcion": "Occidente \u00b7 Planta Senkata \u00b7 Puerto 5432",
        "planta_id": 10,
        "planta_nombre": "Planta Senkata",
        "surtidores": {101: "Surtidor Volcan - Av. Montes", 102: "Surtidor San Pedro"},
        "tabla_despacho": "despachos_lp",
        "motor": "PostgreSQL",
    },
    "Cochabamba": {
        "icono": "\U0001f33f",
        "badge": "Nodo Heterogeneo \u2022 MySQL 8",
        "color": "#198754",
        "descripcion": "Valles \u00b7 Planta Valle Hermoso \u00b7 Puerto 3306",
        "planta_id": 20,
        "planta_nombre": "Planta Gualberto Villarroel",
        "surtidores": {201: "Surtidor Cala Cala", 202: "Surtidor Muyurina"},
        "tabla_despacho": "despachos_cbba",
        "motor": "MySQL",
    },
    "Santa Cruz": {
        "icono": "\U0001f3db\ufe0f",
        "badge": "Nodo Coordinador Padre \u2022 PostgreSQL 15+",
        "color": "#CC0000",
        "descripcion": "Oriente \u00b7 Planta Palmasola \u00b7 Puerto 5432",
        "planta_id": 30,
        "planta_nombre": "Planta Palmasola",
        "surtidores": {301: "Surtidor El Cristo"},
        "tabla_despacho": "despachos_sc",
        "motor": "PostgreSQL",
    },
}

CARBURANTES = {
    1: "Gasolina Especial Plus",
    2: "Diesel Oil",
    3: "Gasolina Premium Ultra",
}

PRECIOS_CARBURANTES = {1: 3.74, 2: 3.72, 3: 4.79}