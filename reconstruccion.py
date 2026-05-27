import time
import pandas as pd
from conexiones import get_engine_lapaz, get_engine_cochabamba, get_engine_santacruz


COLUMNAS_DESPACHOS = ["id_despacho", "id_pedido", "id_plantas", "litros_despachados", "fecha_despacho", "placa_cisterna"]


def obtener_despachos_lp():
    try:
        engine = get_engine_lapaz()
        df = pd.read_sql_query("SELECT * FROM despachos_lp", engine)
        df["fecha_despacho"] = pd.to_datetime(df["fecha_despacho"])
        for col in ["id_despacho", "id_pedido", "id_plantas", "litros_despachados"]:
            df[col] = df[col].astype("int64")
        engine.dispose()
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNAS_DESPACHOS)


def obtener_despachos_cbba():
    try:
        engine = get_engine_cochabamba()
        df = pd.read_sql_query("SELECT * FROM despachos_cbba", engine)
        df["fecha_despacho"] = pd.to_datetime(df["fecha_despacho"])
        for col in ["id_despacho", "id_pedido", "id_plantas", "litros_despachados"]:
            df[col] = df[col].astype("int64")
        engine.dispose()
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNAS_DESPACHOS)


def obtener_despachos_sc():
    try:
        engine = get_engine_santacruz()
        df = pd.read_sql_query("SELECT * FROM despachos_sc", engine)
        df["fecha_despacho"] = pd.to_datetime(df["fecha_despacho"])
        for col in ["id_despacho", "id_pedido", "id_plantas", "litros_despachados"]:
            df[col] = df[col].astype("int64")
        engine.dispose()
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNAS_DESPACHOS)


def obtener_finanzas_sc():
    try:
        engine = get_engine_santacruz()
        df = pd.read_sql_query("SELECT * FROM despachos_finanzas ORDER BY id_despacho", engine)
        df["id_despacho"] = df["id_despacho"].astype("int64")
        engine.dispose()
        return df
    except Exception:
        return pd.DataFrame(columns=["id_despacho", "costo_importacion_real", "subvencion_asumida_bs"])


def obtener_pedidos_por_sede(sede):
    from conexiones import get_engine_by_sede
    try:
        engine = get_engine_by_sede(sede)
        df = pd.read_sql_query("SELECT * FROM pedidos_web", engine)
        for col in ["id_pedido", "id_surtidor", "id_carburante", "cantidad_litros_solicitados"]:
            if col in df.columns:
                df[col] = df[col].astype("int64")
        engine.dispose()
        return df
    except Exception:
        return pd.DataFrame()


def ejecutar_reconstruccion():
    resultado = {
        "ok": False,
        "df_final": None,
        "tiempo_segundos": 0,
        "nodos_disponibles": {},
        "error": None,
    }

    inicio = time.time()

    df_lp = obtener_despachos_lp()
    resultado["nodos_disponibles"]["La Paz"] = not df_lp.empty

    df_cbba = obtener_despachos_cbba()
    resultado["nodos_disponibles"]["Cochabamba"] = not df_cbba.empty

    df_sc = obtener_despachos_sc()
    resultado["nodos_disponibles"]["Santa Cruz"] = not df_sc.empty

    dfs_operativos = []
    for nombre, df in [("La Paz", df_lp), ("Cochabamba", df_cbba), ("Santa Cruz", df_sc)]:
        if not df.empty:
            dfs_operativos.append(df)

    if not dfs_operativos:
        resultado["error"] = "No se pudo conectar a ningun nodo. Verifique la conexion VPN."
        resultado["tiempo_segundos"] = round(time.time() - inicio, 2)
        return resultado

    df_operativos = pd.concat(dfs_operativos, ignore_index=True)

    df_finanzas = obtener_finanzas_sc()
    if df_finanzas.empty:
        resultado["df_final"] = df_operativos
        resultado["ok"] = True
        resultado["tiempo_segundos"] = round(time.time() - inicio, 2)
        resultado["error"] = "Datos financieros no disponibles. Solo se reconstruyo la tabla operativa."
        return resultado

    df_final = pd.merge(df_operativos, df_finanzas, on="id_despacho", how="inner")

    id_plantas_to_dept = {10: "La Paz", 20: "Cochabamba", 30: "Santa Cruz"}
    df_final["departamento"] = df_final["id_plantas"].map(id_plantas_to_dept)

    resultado["df_final"] = df_final
    resultado["ok"] = True
    resultado["tiempo_segundos"] = round(time.time() - inicio, 2)
    return resultado


def obtener_datos_graficos(df_final):
    if df_final is None or df_final.empty:
        return None, None

    df_barras = df_final.groupby("departamento")["litros_despachados"].sum().reset_index()
    df_barras.columns = ["Departamento", "Litros Despachados"]

    id_carburante_map = {1: "Gasolina Especial Plus", 2: "Diesel Oil", 3: "Gasolina Premium Ultra"}

    try:
        from conexiones import get_engine_santacruz
        engine = get_engine_santacruz()
        df_pedidos_sc = pd.read_sql_query("SELECT id_pedido, id_carburante FROM pedidos_web", engine)
        engine.dispose()
        df_final_con_carburante = pd.merge(df_final, df_pedidos_sc, on="id_pedido", how="left")
        df_final_con_carburante["carburante"] = df_final_con_carburante["id_carburante"].map(id_carburante_map)
        df_donut = df_final_con_carburante.groupby("carburante")["subvencion_asumida_bs"].sum().reset_index()
        df_donut.columns = ["Carburante", "Subvencion (Bs.)"]
    except Exception:
        df_donut = df_final.groupby("departamento")["subvencion_asumida_bs"].sum().reset_index()
        df_donut.columns = ["Carburante", "Subvencion (Bs.)"]

    return df_barras, df_donut