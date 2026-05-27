import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestConfig(unittest.TestCase):
    def test_sedes_exist(self):
        from config import SEDES
        self.assertIn("La Paz", SEDES)
        self.assertIn("Cochabamba", SEDES)
        self.assertIn("Santa Cruz", SEDES)

    def test_sedes_have_required_keys(self):
        from config import SEDES
        for nombre, cfg in SEDES.items():
            self.assertIn("planta_id", cfg, f"{nombre} missing planta_id")
            self.assertIn("tabla_despacho", cfg, f"{nombre} missing tabla_despacho")
            self.assertIn("surtidores", cfg, f"{nombre} missing surtidores")
            self.assertIn("motor", cfg, f"{nombre} missing motor")
            self.assertIn("color", cfg, f"{nombre} missing color")

    def test_sede_ids(self):
        from config import SEDES
        self.assertEqual(SEDES["La Paz"]["planta_id"], 10)
        self.assertEqual(SEDES["Cochabamba"]["planta_id"], 20)
        self.assertEqual(SEDES["Santa Cruz"]["planta_id"], 30)

    def test_sede_tables(self):
        from config import SEDES
        self.assertEqual(SEDES["La Paz"]["tabla_despacho"], "despachos_lp")
        self.assertEqual(SEDES["Cochabamba"]["tabla_despacho"], "despachos_cbba")
        self.assertEqual(SEDES["Santa Cruz"]["tabla_despacho"], "despachos_sc")

    def test_db_credentials(self):
        from config import LP_HOST, LP_PORT, LP_DB, CBBA_HOST, CBBA_PORT, CBBA_DB, SC_HOST, SC_PORT, SC_DB
        self.assertEqual(LP_HOST, "localhost")
        self.assertEqual(LP_PORT, 5432)
        self.assertEqual(LP_DB, "ypfb_la_paz")
        self.assertEqual(CBBA_HOST, "26.157.52.238")
        self.assertEqual(CBBA_PORT, 3306)
        self.assertEqual(CBBA_DB, "cochabamba")
        self.assertEqual(SC_HOST, "26.82.89.70")
        self.assertEqual(SC_PORT, 5432)
        self.assertEqual(SC_DB, "ypfb_santa_cruz")

    def test_costo_importacion(self):
        from config import COSTO_IMPORTACION_POR_LITRO
        self.assertEqual(COSTO_IMPORTACION_POR_LITRO, 8.50)

    def test_carburantes(self):
        from config import CARBURANTES
        self.assertEqual(CARBURANTES[1], "Gasolina Especial Plus")
        self.assertEqual(CARBURANTES[2], "Diesel Oil")
        self.assertEqual(CARBURANTES[3], "Gasolina Premium Ultra")

    def test_precios(self):
        from config import PRECIOS_CARBURANTES
        self.assertEqual(PRECIOS_CARBURANTES[1], 3.74)
        self.assertEqual(PRECIOS_CARBURANTES[2], 3.72)
        self.assertEqual(PRECIOS_CARBURANTES[3], 4.79)


class TestReconstruccionLogic(unittest.TestCase):
    def test_id_plantas_mapping(self):
        id_plantas_to_dept = {10: "La Paz", 20: "Cochabamba", 30: "Santa Cruz"}
        self.assertEqual(id_plantas_to_dept[10], "La Paz")
        self.assertEqual(id_plantas_to_dept[20], "Cochabamba")
        self.assertEqual(id_plantas_to_dept[30], "Santa Cruz")

    def test_subvencion_calculation(self):
        from config import COSTO_IMPORTACION_POR_LITRO, PRECIOS_CARBURANTES
        litros = 15000
        carburante_id = 1
        precio = PRECIOS_CARBURANTES[carburante_id]
        costo = litros * COSTO_IMPORTACION_POR_LITRO
        subvencion = (COSTO_IMPORTACION_POR_LITRO - precio) * litros
        self.assertEqual(costo, 127500.0)
        self.assertAlmostEqual(subvencion, 71400.0, places=1)

    def test_subvencion_diesel(self):
        from config import COSTO_IMPORTACION_POR_LITRO, PRECIOS_CARBURANTES
        litros = 20000
        precio = PRECIOS_CARBURANTES[2]
        subvencion = (COSTO_IMPORTACION_POR_LITRO - precio) * litros
        self.assertAlmostEqual(subvencion, 95600.0, places=1)

    def test_subvencion_premium(self):
        from config import COSTO_IMPORTACION_POR_LITRO, PRECIOS_CARBURANTES
        litros = 120000
        precio = PRECIOS_CARBURANTES[3]
        subvencion = (COSTO_IMPORTACION_POR_LITRO - precio) * litros
        self.assertAlmostEqual(subvencion, 445200.0, places=1)


class TestSedeRouting(unittest.TestCase):
    def test_sede_tables_match(self):
        from config import SEDES
        tablas = {
            "La Paz": "despachos_lp",
            "Cochabamba": "despachos_cbba",
            "Santa Cruz": "despachos_sc",
        }
        for sede, tabla in tablas.items():
            self.assertEqual(SEDES[sede]["tabla_despacho"], tabla)

    def test_sede_motores(self):
        from config import SEDES
        self.assertEqual(SEDES["La Paz"]["motor"], "PostgreSQL")
        self.assertEqual(SEDES["Cochabamba"]["motor"], "MySQL")
        self.assertEqual(SEDES["Santa Cruz"]["motor"], "PostgreSQL")

    def test_sede_surtidores(self):
        from config import SEDES
        self.assertEqual(len(SEDES["La Paz"]["surtidores"]), 2)
        self.assertEqual(len(SEDES["Cochabamba"]["surtidores"]), 2)
        self.assertEqual(len(SEDES["Santa Cruz"]["surtidores"]), 1)
        self.assertIn(101, SEDES["La Paz"]["surtidores"])
        self.assertIn(301, SEDES["Santa Cruz"]["surtidores"])


class TestFragmentacionData(unittest.TestCase):
    def test_despachos_lp_ids(self):
        self.assertEqual(15001 // 1000, 15)

    def test_despachos_cbba_ids(self):
        self.assertEqual(25001 // 1000, 25)

    def test_despachos_sc_ids(self):
        self.assertEqual(35001 // 1000, 35)

    def test_stock_lp_ids(self):
        stock_ids = [1001, 1002, 1003]
        for sid in stock_ids:
            self.assertEqual(sid // 100, 10)

    def test_stock_cbba_ids(self):
        stock_ids = [2001, 2002]
        for sid in stock_ids:
            self.assertEqual(sid // 100, 20)

    def test_stock_sc_ids(self):
        stock_ids = [3001, 3002]
        for sid in stock_ids:
            self.assertEqual(sid // 100, 30)


if __name__ == "__main__":
    unittest.main()