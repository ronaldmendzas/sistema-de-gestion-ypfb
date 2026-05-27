from datetime import datetime
from config import SEDES, CARBURANTES, PRECIOS_CARBURANTES, COSTO_IMPORTACION_POR_LITRO
from conexiones import get_conn_by_sede, get_conn_santacruz


def ejecutar_2pc(sede, id_surtidor, id_carburante, litros, placa):
    log_steps = []
    info_sede = SEDES[sede]
    planta_id = info_sede["planta_id"]
    precio_surtidor = PRECIOS_CARBURANTES[id_carburante]

    conn_local = None
    conn_sc = None

    try:
        conn_local = get_conn_by_sede(sede)
        log_steps.append({"paso": f"Verificando conexion nodo local ({sede})...", "estado": "ok"})
    except Exception as e:
        log_steps.append({"paso": f"Verificando conexion nodo local ({sede})... FALLO", "estado": "error", "detalle": str(e)})
        return {"fase": "PREPARE", "ok": False, "log": log_steps}

    try:
        conn_sc = get_conn_santacruz()
        log_steps.append({"paso": "Verificando conexion Nodo SC (Finanzas)...", "estado": "ok"})
    except Exception as e:
        log_steps.append({"paso": "Verificando conexion Nodo SC (Finanzas)... FALLO", "estado": "error", "detalle": str(e)})
        conn_local.close()
        return {"fase": "PREPARE", "ok": False, "log": log_steps}

    try:
        cur_local = conn_local.cursor()
        tabla_stock = "stock_plantas"
        query_stock = f"SELECT stock_disponible_litros FROM {tabla_stock} WHERE id_plantas = %s AND id_carburante = %s"
        cur_local.execute(query_stock, (planta_id, id_carburante))
        row = cur_local.fetchone()
        cur_local.close()

        if row is None:
            log_steps.append({"paso": f"No se encontro stock para id_plantas={planta_id}, id_carburante={id_carburante}", "estado": "error"})
            conn_local.close()
            conn_sc.close()
            return {"fase": "PREPARE", "ok": False, "log": log_steps}

        stock_actual = row[0] if isinstance(row, (list, tuple)) else row["stock_disponible_litros"]
        stock_formateado = f"{stock_actual:,}"

        if litros > stock_actual:
            log_steps.append({"paso": f"Stock insuficiente: disponible {stock_formateado} litros, solicitado {litros:,}", "estado": "error"})
            conn_local.close()
            conn_sc.close()
            return {"fase": "PREPARE", "ok": False, "log": log_steps}

        log_steps.append({"paso": f"Stock disponible: {stock_formateado} litros", "estado": "ok"})
        log_steps.append({"paso": "Todos los nodos listos \u2192 COMMIT", "estado": "ok"})
    except Exception as e:
        log_steps.append({"paso": f"Error consultando stock local: {str(e)}", "estado": "error"})
        conn_local.close()
        conn_sc.close()
        return {"fase": "PREPARE", "ok": False, "log": log_steps}

    id_pedido = None
    id_despacho = None

    try:
        conn_local.autocommit(False)
        cur_local = conn_local.cursor()
        tabla_despacho = info_sede["tabla_despacho"]
        es_mysql = sede == "Cochabamba"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query_pedido = "INSERT INTO pedidos_web (id_surtidor, id_carburante, cantidad_litros_solicitados, fecha_solicitud, estado) VALUES (%s, %s, %s, %s, %s)"
        cur_local.execute(query_pedido, (id_surtidor, id_carburante, litros, now, "Despachado"))

        if es_mysql:
            id_pedido = cur_local.lastrowid
        else:
            cur_local.execute("SELECT lastval()")
            id_pedido = cur_local.fetchone()[0]

        log_steps.append({"paso": f"INSERT en pedidos_web local (id_pedido={id_pedido})...", "estado": "ok"})

        query_despacho = f"INSERT INTO {tabla_despacho} (id_pedido, id_plantas, litros_despachados, fecha_despacho, placa_cisterna) VALUES (%s, %s, %s, %s, %s)"
        cur_local.execute(query_despacho, (id_pedido, planta_id, litros, now, placa))

        if es_mysql:
            id_despacho = cur_local.lastrowid
        else:
            cur_local.execute("SELECT lastval()")
            id_despacho = cur_local.fetchone()[0]

        log_steps.append({"paso": f"INSERT en {tabla_despacho} local (id_despacho={id_despacho})...", "estado": "ok"})

        query_stock_update = "UPDATE stock_plantas SET stock_disponible_litros = stock_disponible_litros - %s WHERE id_plantas = %s AND id_carburante = %s"
        cur_local.execute(query_stock_update, (litros, planta_id, id_carburante))
        log_steps.append({"paso": f"Stock descontado: -{litros:,} litros", "estado": "ok"})

        conn_local.commit()
        log_steps.append({"paso": f"INSERT en {info_sede['motor']} local confirmado", "estado": "ok"})
    except Exception as e:
        conn_local.rollback()
        log_steps.append({"paso": f"Error en INSERT local: {str(e)}", "estado": "error"})
        try:
            conn_local.close()
            conn_sc.close()
        except Exception:
            pass
        return {"fase": "COMMIT", "ok": False, "log": log_steps}

    try:
        costo_importacion = litros * COSTO_IMPORTACION_POR_LITRO
        subvencion = (COSTO_IMPORTACION_POR_LITRO - precio_surtidor) * litros

        conn_sc.autocommit(False)
        cur_sc = conn_sc.cursor()
        query_finanzas = "INSERT INTO despachos_finanzas (id_despacho, costo_importacion_real, subvencion_asumida_bs) VALUES (%s, %s, %s)"
        cur_sc.execute(query_finanzas, (id_despacho, costo_importacion, subvencion))
        conn_sc.commit()
        cur_sc.close()

        log_steps.append({"paso": f"INSERT en despachos_finanzas SC (id_despacho={id_despacho})...", "estado": "ok"})
        log_steps.append({"paso": f"Costo importacion: Bs. {costo_importacion:,.2f} | Subvencion: Bs. {subvencion:,.2f}", "estado": "ok"})
        log_steps.append({"paso": "\u2705 TRANSACCION 2PC COMPLETADA", "estado": "ok"})

        return {
            "fase": "COMMIT",
            "ok": True,
            "log": log_steps,
            "id_pedido": id_pedido,
            "id_despacho": id_despacho,
            "costo_importacion": costo_importacion,
            "subvencion": subvencion,
        }
    except Exception as e:
        conn_sc.rollback()
        log_steps.append({"paso": f"Error en INSERT finanzas SC: {str(e)}", "estado": "error"})
        log_steps.append({"paso": "\u274c ROLLBACK - Revirtiendo insercion local", "estado": "error"})

        try:
            cur_rollback = conn_local.cursor()
            cur_rollback.execute(f"DELETE FROM {tabla_despacho} WHERE id_despacho = %s", (id_despacho,))
            cur_rollback.execute("DELETE FROM pedidos_web WHERE id_pedido = %s", (id_pedido,))
            cur_rollback.execute("UPDATE stock_plantas SET stock_disponible_litros = stock_disponible_litros + %s WHERE id_plantas = %s AND id_carburante = %s", (litros, planta_id, id_carburante))
            conn_local.commit()
            cur_rollback.close()
            log_steps.append({"paso": "Rollback manual ejecutado en nodo local", "estado": "error"})
        except Exception as rollback_err:
            log_steps.append({"paso": f"Error en rollback manual: {str(rollback_err)}", "estado": "error"})

        return {"fase": "COMMIT", "ok": False, "log": log_steps}
    finally:
        try:
            if conn_local and not conn_local.closed:
                conn_local.close()
        except Exception:
            pass
        try:
            if conn_sc and conn_sc.closed == 0:
                conn_sc.close()
        except Exception:
            pass