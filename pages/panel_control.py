import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import SEDES, CARBURANTES, PRECIOS_CARBURANTES
from conexiones import get_conn_by_sede, get_conn_santacruz, get_engine_by_sede, get_engine_santacruz, estado_nodos
from protocolo_2pc import ejecutar_2pc
from reconstruccion import ejecutar_reconstruccion, obtener_datos_graficos

DARK = {"La Paz": "#003366", "Cochabamba": "#166534", "Santa Cruz": "#991b1b"}

def render():
    sede = st.session_state.get("sede_activa")
    if not sede:
        st.warning("No has seleccionado una sede. Regresa al inicio.")
        if st.button("Ir al Inicio"):
            st.session_state.pagina = "Inicio"
            st.rerun()
        return

    info = SEDES[sede]
    try:
        estado = estado_nodos()
    except Exception:
        estado = {k: False for k in SEDES.keys()}

    color = DARK.get(sede, "#003366")
    if sede in ["La Paz", "Cochabamba"]:
        _render_operador(sede, info, estado, color)
    else:
        _render_gerente(sede, info, estado, color)


def _safe_query(engine_func, query, params=None, fallback_conn_func=None):
    try:
        engine = engine_func()
        df = pd.read_sql_query(query, engine, params=params)
        engine.dispose()
        return df
    except Exception:
        try:
            engine.dispose()
        except Exception:
            pass
    if fallback_conn_func:
        conn = None
        try:
            conn = fallback_conn_func()
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            return df
        except Exception:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    return pd.DataFrame()


def _render_operador(sede, info, estado, color):
    motor = info["motor"]
    puerto = "5432" if motor == "PostgreSQL" else "3306"
    connected = estado.get(sede, False)
    dot = "#166534" if connected else "#dc2626"
    status = "Conectado" if connected else "Desconectado"

    st.markdown(f"""<div style="background:{color};border-radius:10px;padding:14px 20px;margin-bottom:12px;">
        <h2 style="color:#ffffff;margin:0;font-size:1.15rem;font-weight:700;">Operador Regional — {sede}</h2>
        <p style="color:#ffffffcc;margin:2px 0 0 0;font-size:0.8rem;">{info["planta_nombre"]} · {info["badge"]} · Puerto {puerto}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{dot};margin-right:4px;"></span> <span style="color:#18181b;font-weight:600;">{status}</span> <span style="color:#52525b;">· {motor} · Puerto {puerto}</span>', unsafe_allow_html=True)

    if not connected:
        st.warning(f"Nodo {sede} no disponible. Verifica la conexion.")

    col_form, col_datos = st.columns(2)

    with col_form:
        st.markdown("### Registrar Nuevo Despacho")
        surtidor_map = {v: k for k, v in info["surtidores"].items()}
        surtidor_sel = st.selectbox("Surtidor destino", list(surtidor_map.keys()), key=f"sel_surt_{sede}")
        id_surtidor = surtidor_map[surtidor_sel]

        carb_map = {v: k for k, v in CARBURANTES.items()}
        carb_sel = st.selectbox("Tipo de carburante", list(carb_map.keys()), key=f"sel_carb_{sede}")
        id_carburante = carb_map[carb_sel]

        litros = st.number_input("Litros solicitados", min_value=1000, step=1000, key=f"num_litros_{sede}")
        placa = st.text_input("Placa cisterna", placeholder="Ej: 2345-PKD", key=f"txt_placa_{sede}")

        if st.button("APROBAR DESPACHO — Protocolo 2PC", key=f"btn_desp_{sede}", type="primary", use_container_width=True):
            if not placa:
                st.error("La placa del cisterna es obligatoria")
            elif litros <= 0:
                st.error("Los litros deben ser mayores a 0")
            else:
                with st.spinner("Ejecutando Protocolo 2PC..."):
                    resultado = ejecutar_2pc(sede, id_surtidor, id_carburante, litros, placa.upper())
                st.session_state.log_2pc = resultado.get("log", [])
                with st.expander("Log del Protocolo 2PC", expanded=True):
                    for step in st.session_state.log_2pc:
                        tag = "[OK]" if step["estado"] == "ok" else "[FAIL]"
                        det = f" ({step['detalle']})" if "detalle" in step else ""
                        bold = "**" if step["estado"] != "ok" else ""
                        st.markdown(f"`{tag}` {bold}{step['paso']}{det}{bold}")
                if resultado["ok"]:
                    st.success(f"Despacho registrado. ID: {resultado.get('id_despacho', 'N/A')}")
                else:
                    st.error("Transaccion fallida. Revisa el log.")

    with col_datos:
        st.markdown(f"### Fragmento Local — {sede}")
        tab_s, tab_p, tab_d = st.tabs(["Stock", "Pedidos", "Despachos"])
        with tab_s:
            df = _safe_query(lambda: get_engine_by_sede(sede), "SELECT s.id_stock, p.nombre_planta, c.nombre as carburante, s.stock_disponible_litros FROM stock_plantas s JOIN plantas p ON s.id_plantas = p.id_plantas JOIN carburantes c ON s.id_carburante = c.id_carburante WHERE s.id_plantas = %s", params=(info["planta_id"],), fallback_conn_func=lambda: get_conn_by_sede(sede))
            if not df.empty:
                st.dataframe(df, hide_index=True)
            else:
                st.info("No se pudieron consultar los datos de stock. Verifica la conexion.")
        with tab_p:
            df = _safe_query(lambda: get_engine_by_sede(sede), "SELECT * FROM pedidos_web", fallback_conn_func=lambda: get_conn_by_sede(sede))
            if not df.empty:
                st.dataframe(df, hide_index=True)
            else:
                st.info("No se pudieron consultar los pedidos. Verifica la conexion.")
        with tab_d:
            df = _safe_query(lambda: get_engine_by_sede(sede), f"SELECT * FROM {info['tabla_despacho']}", fallback_conn_func=lambda: get_conn_by_sede(sede))
            if not df.empty:
                st.dataframe(df, hide_index=True)
            else:
                st.info("No se pudieron consultar los despachos. Verifica la conexion.")

    st.markdown("---")
    if st.button("Intentar acceder a datos financieros", key=f"btn_fin_{sede}"):
        st.error("ACCESO DENEGADO: Datos confidenciales centralizados en la Sede Central — Santa Cruz")


def _render_gerente(sede, info, estado, color):
    st.markdown(f"""<div style="background:{color};border-radius:10px;padding:14px 20px;margin-bottom:12px;">
        <h2 style="color:#ffffff;margin:0;font-size:1.15rem;font-weight:700;">Gerente Nacional — Sede Central</h2>
        <p style="color:#ffffffcc;margin:2px 0 0 0;font-size:0.8rem;">{info["planta_nombre"]} · Nodo Coordinador Padre</p>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(3)
    nodos_info = [("La Paz", "PostgreSQL"), ("Cochabamba", "MySQL"), ("Santa Cruz", "PostgreSQL")]
    for i, (nombre, motor) in enumerate(nodos_info):
        with cols[i]:
            dot = "#166534" if estado.get(nombre, False) else "#dc2626"
            st_text = "Online" if estado.get(nombre, False) else "Offline"
            st.markdown(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{dot};margin-right:4px;"></span><span style="color:#18181b;font-weight:600;">{nombre}</span> <span style="color:#52525b;">({motor}) — {st_text}</span>', unsafe_allow_html=True)

    tab_log, tab_fin, tab_rec = st.tabs(["Logistica Local", "Boveda Financiera", "Reconstruccion Global"])

    with tab_log:
        st.markdown("### Registrar Despacho — Planta Palmasola")
        surtidor_map = {v: k for k, v in info["surtidores"].items()}
        surtidor_sel = st.selectbox("Surtidor destino", list(surtidor_map.keys()), key="sel_surt_sc")
        id_surtidor = surtidor_map[surtidor_sel]
        carb_map = {v: k for k, v in CARBURANTES.items()}
        carb_sel = st.selectbox("Tipo de carburante", list(carb_map.keys()), key="sel_carb_sc")
        id_carburante = carb_map[carb_sel]
        litros = st.number_input("Litros solicitados", min_value=1000, step=1000, key="num_litros_sc")
        placa = st.text_input("Placa cisterna", placeholder="Ej: 9822-XPT", key="txt_placa_sc")

        if st.button("APROBAR DESPACHO — Protocolo 2PC", key="btn_desp_sc", type="primary", use_container_width=True):
            if not placa:
                st.error("La placa del cisterna es obligatoria")
            elif litros <= 0:
                st.error("Los litros deben ser mayores a 0")
            else:
                with st.spinner("Ejecutando Protocolo 2PC..."):
                    resultado = ejecutar_2pc(sede, id_surtidor, id_carburante, litros, placa.upper())
                st.session_state.log_2pc = resultado.get("log", [])
                with st.expander("Log del Protocolo 2PC", expanded=True):
                    for step in st.session_state.log_2pc:
                        tag = "[OK]" if step["estado"] == "ok" else "[FAIL]"
                        det = f" ({step['detalle']})" if "detalle" in step else ""
                        bold = "**" if step["estado"] != "ok" else ""
                        st.markdown(f"`{tag}` {bold}{step['paso']}{det}{bold}")
                if resultado["ok"]:
                    st.success(f"Despacho registrado. ID: {resultado.get('id_despacho', 'N/A')}")
                else:
                    st.error("Transaccion fallida. Revisa el log.")

        df = _safe_query(get_engine_santacruz, "SELECT * FROM despachos_sc", fallback_conn_func=get_conn_santacruz)
        if not df.empty:
            st.dataframe(df, hide_index=True)

    with tab_fin:
        st.markdown("""<div style="border:1px solid #991b1b;border-radius:8px;padding:10px 14px;background:#fef2f2;margin-bottom:10px;">
            <strong style="color:#991b1b;">DESPACHOS_FINANZAS</strong> — Datos Macroeconomicos Confidenciales<br>
            <span style="color:#52525b;font-size:0.8rem;">Nivel de Acceso: Solo Sede Central</span>
        </div>""", unsafe_allow_html=True)

        df = _safe_query(get_engine_santacruz, "SELECT * FROM despachos_finanzas ORDER BY id_despacho", fallback_conn_func=get_conn_santacruz)
        if not df.empty:
            df_disp = df.copy()
            df_disp["costo_importacion_real"] = df_disp["costo_importacion_real"].apply(lambda x: f"Bs. {x:,.2f}")
            df_disp["subvencion_asumida_bs"] = df_disp["subvencion_asumida_bs"].apply(lambda x: f"Bs. {x:,.2f}")
            st.dataframe(df_disp, hide_index=True)
            st.markdown(f"**Total Subvencion Acumulada:** Bs. {df['subvencion_asumida_bs'].sum():,.2f}")
            st.markdown(f"**Total Costo Importacion:** Bs. {df['costo_importacion_real'].sum():,.2f}")
        else:
            st.info("No se pudieron consultar los datos financieros. Verifica la conexion a Santa Cruz.")

    with tab_rec:
        st.markdown("### Reconstruccion Distribuida Hibrida")
        st.caption("Union horizontal de los 3 fragmentos operativos + Junta vertical con la tabla financiera central.")

        if st.button("EJECUTAR RECONSTRUCCION DISTRIBUIDA", key="btn_reconstruir", type="primary", use_container_width=True):
            progress = st.progress(0, text="Iniciando reconstruccion...")
            import time
            time.sleep(0.5)
            progress.progress(20, text="Extrayendo datos La Paz (PostgreSQL)...")
            time.sleep(0.6)
            progress.progress(40, text="Extrayendo datos Cochabamba (MySQL)...")
            time.sleep(0.6)
            progress.progress(60, text="Extrayendo datos Santa Cruz (PostgreSQL)...")
            time.sleep(0.6)
            progress.progress(80, text="pd.concat() — Union horizontal...")
            time.sleep(0.4)
            progress.progress(95, text="pd.merge() — Junta vertical...")
            time.sleep(0.4)

            resultado = ejecutar_reconstruccion()
            progress.progress(100, text="Completado")

            if resultado["ok"]:
                st.session_state.df_reconstruido = resultado["df_final"]
                for nodo, disponible in resultado["nodos_disponibles"].items():
                    tag = "Online" if disponible else "Offline"
                    st.markdown(f"- **{nodo}**: {tag}")
                st.info(f"Reconstruccion completada en **{resultado['tiempo_segundos']}s**")
                if resultado.get("error"):
                    st.warning(resultado["error"])

                df_final = resultado["df_final"]
                if df_final is not None and not df_final.empty:
                    st.markdown("#### Tabla DESPACHOS Reconstruida al 100%")
                    cc = {}
                    for col in df_final.columns:
                        if col in ["litros_despachados", "id_despacho", "id_pedido", "id_plantas"]:
                            cc[col] = st.column_config.NumberColumn(format="%d")
                        elif col in ["costo_importacion_real", "subvencion_asumida_bs"]:
                            cc[col] = st.column_config.NumberColumn(format="Bs. %,.2f")
                        elif col == "fecha_despacho":
                            cc[col] = st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm")
                    st.dataframe(df_final, hide_index=True, column_config=cc)

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Litros", f"{df_final['litros_despachados'].sum():,}")
                    m2.metric("Costo Importacion", f"Bs. {df_final['costo_importacion_real'].sum():,.2f}")
                    m3.metric("Subvencion Asumida", f"Bs. {df_final['subvencion_asumida_bs'].sum():,.2f}")
                    m4.metric("Despachos", f"{len(df_final)}")

                    df_barras, df_donut = obtener_datos_graficos(df_final)
                    if df_barras is not None:
                        st.markdown("#### Abastecimiento por Departamento (Litros)")
                        colores = {"La Paz": "#003366", "Cochabamba": "#166534", "Santa Cruz": "#991b1b"}
                        fig = go.Figure()
                        for dept in df_barras["Departamento"].unique():
                            fila = df_barras[df_barras["Departamento"] == dept]
                            fig.add_trace(go.Bar(x=fila["Departamento"], y=fila["Litros Despachados"], name=dept, marker_color=colores.get(dept, "#003366"), text=fila["Litros Despachados"].apply(lambda x: f"{x:,}"), textposition="outside"))
                        fig.update_layout(xaxis_title="Departamento", yaxis_title="Litros Despachados", showlegend=False, height=380, margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor="white")
                        st.plotly_chart(fig, use_container_width=True)

                    if df_donut is not None:
                        st.markdown("#### Distribucion de Subvencion Fiscal por Carburante")
                        fig2 = go.Figure(data=[go.Pie(labels=df_donut["Carburante"], values=df_donut["Subvencion (Bs.)"], hole=0.5, marker_colors=["#003366", "#166534", "#991b1b"], textinfo="label+percent", texttemplate="%{label}<br>Bs. %{value:,.2f}<br>(%{percent})", hovertemplate="%{label}: Bs. %{value:,.2f}<extra></extra>")])
                        fig2.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), showlegend=True, plot_bgcolor="white")
                        st.plotly_chart(fig2, use_container_width=True)
            else:
                progress.empty()
                st.error(f"{resultado['error']}")

        elif st.session_state.get("df_reconstruido") is not None:
            df_final = st.session_state.df_reconstruido
            st.success("Datos de la ultima reconstruccion disponibles")
            cc = {}
            for col in df_final.columns:
                if col in ["litros_despachados", "id_despacho", "id_pedido", "id_plantas"]:
                    cc[col] = st.column_config.NumberColumn(format="%d")
                elif col in ["costo_importacion_real", "subvencion_asumida_bs"]:
                    cc[col] = st.column_config.NumberColumn(format="Bs. %,.2f")
                elif col == "fecha_despacho":
                    cc[col] = st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm")
            st.dataframe(df_final, hide_index=True, column_config=cc)