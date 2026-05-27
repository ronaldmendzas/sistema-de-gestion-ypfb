import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import SEDES, CARBURANTES, PRECIOS_CARBURANTES
from conexiones import get_conn_by_sede, get_conn_santacruz, get_engine_by_sede, get_engine_santacruz, estado_nodos
from protocolo_2pc import ejecutar_2pc
from reconstruccion import ejecutar_reconstruccion, obtener_datos_graficos


def render():
    sede = st.session_state.get("sede_activa")
    if not sede:
        st.warning("No has seleccionado una sede. Regresa al inicio para seleccionar.")
        if st.button("Ir al Inicio"):
            st.session_state.pagina = "Inicio"
            st.rerun()
        return

    info = SEDES[sede]
    try:
        estado = estado_nodos()
    except Exception:
        estado = {k: False for k in SEDES.keys()}

    if sede in ["La Paz", "Cochabamba"]:
        _render_operador_regional(sede, info, estado)
    elif sede == "Santa Cruz":
        _render_gerente_nacional(sede, info, estado)


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


def _render_operador_regional(sede, info, estado):
    color = info["color"]
    motor = info["motor"]
    puerto = "5432" if motor == "PostgreSQL" else "3306"

    st.markdown(f"""
    <div style="background:{color};border-radius:10px;padding:16px 20px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div>
                <h2 style="color:#fff;margin:0;font-size:1.2rem;font-weight:700;">Operador Regional - {sede}</h2>
                <p style="color:#ffffffaa;margin:2px 0 0 0;font-size:0.8rem;">{info['planta_nombre']} · {info['badge']} · Puerto {puerto}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    indicador = "Conectado" if estado.get(sede, False) else "Desconectado"
    dot_color = "#198754" if estado.get(sede, False) else "#ef4444"
    st.markdown(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{dot_color};margin-right:6px;"></span>**{indicador}** · {motor} · Puerto {puerto}', unsafe_allow_html=True)

    if not estado.get(sede, False):
        st.warning(f"Nodo {sede} no disponible. Verifica la conexion.")

    col_form, col_datos = st.columns(2)

    with col_form:
        st.markdown("### Registrar Nuevo Despacho")
        surtidores = info["surtidores"]
        surtidor_nombres = {v: k for k, v in surtidores.items()}
        surtidor_seleccionado = st.selectbox("Surtidor destino", list(surtidor_nombres.keys()), key=f"sel_surt_{sede}")
        id_surtidor = surtidor_nombres[surtidor_seleccionado]

        carburante_nombres = {v: k for k, v in CARBURANTES.items()}
        carburante_seleccionado = st.selectbox("Tipo de carburante", list(carburante_nombres.keys()), key=f"sel_carb_{sede}")
        id_carburante = carburante_nombres[carburante_seleccionado]

        litros = st.number_input("Litros solicitados", min_value=1000, step=1000, key=f"num_litros_{sede}")
        placa = st.text_input("Placa cisterna", placeholder="Ej: 2345-PKD", key=f"txt_placa_{sede}")

        if st.button("APROBAR DESPACHO - Protocolo 2PC", key=f"btn_despacho_{sede}", type="primary", use_container_width=True):
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
                        icon = "OK" if step["estado"] == "ok" else "FAIL"
                        detalle = f" ({step['detalle']})" if "detalle" in step else ""
                        if step["estado"] == "ok":
                            st.markdown(f"`[{icon}]` {step['paso']}{detalle}")
                        else:
                            st.markdown(f"`[{icon}]` **{step['paso']}**{detalle}")

                if resultado["ok"]:
                    st.success(f"Despacho registrado. ID Despacho: {resultado.get('id_despacho', 'N/A')}")
                else:
                    st.error("Transaccion fallida. Revisa el log.")

    with col_datos:
        st.markdown(f"### Fragmento Local - {sede}")
        tab_stock, tab_pedidos, tab_despachos = st.tabs(["Stock Local", "Pedidos Locales", "Despachos Locales"])

        with tab_stock:
            df = _safe_query(
                lambda: get_engine_by_sede(sede),
                "SELECT s.id_stock, p.nombre_planta, c.nombre as carburante, s.stock_disponible_litros FROM stock_plantas s JOIN plantas p ON s.id_plantas = p.id_plantas JOIN carburantes c ON s.id_carburante = c.id_carburante WHERE s.id_plantas = %s",
                params=(info["planta_id"],),
                fallback_conn_func=lambda: get_conn_by_sede(sede)
            )
            if not df.empty:
                st.dataframe(df, hide_index=True)
            else:
                st.info("No se pudieron consultar los datos de stock local.")

        with tab_pedidos:
            df = _safe_query(lambda: get_engine_by_sede(sede), "SELECT * FROM pedidos_web", fallback_conn_func=lambda: get_conn_by_sede(sede))
            if not df.empty:
                st.dataframe(df, hide_index=True)
            else:
                st.info("No se pudieron consultar los pedidos locales.")

        with tab_despachos:
            df = _safe_query(lambda: get_engine_by_sede(sede), f"SELECT * FROM {info['tabla_despacho']}", fallback_conn_func=lambda: get_conn_by_sede(sede))
            if not df.empty:
                st.dataframe(df, hide_index=True)
            else:
                st.info("No se pudieron consultar los despachos locales.")

    st.markdown("---")
    if st.button("Intentar acceder a datos financieros", key=f"btn_finanzas_{sede}"):
        st.error("ACCESO DENEGADO: Datos confidenciales centralizados en la Sede Central - Santa Cruz")


def _render_gerente_nacional(sede, info, estado):
    color = info["color"]

    st.markdown(f"""
    <div style="background:{color};border-radius:10px;padding:16px 20px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div>
                <h2 style="color:#fff;margin:0;font-size:1.2rem;font-weight:700;">Gerente Nacional · Sede Central</h2>
                <p style="color:#ffffffaa;margin:2px 0 0 0;font-size:0.8rem;">{info['planta_nombre']} · Nodo Coordinador Padre</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    nodos = [("La Paz", "PostgreSQL"), ("Cochabamba", "MySQL"), ("Santa Cruz", "PostgreSQL")]
    for col, (nombre, motor) in zip([c1, c2, c3], nodos):
        with col:
            dot_color = "#198754" if estado.get(nombre, False) else "#ef4444"
            status = "Online" if estado.get(nombre, False) else "Offline"
            st.markdown(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{dot_color};margin-right:6px;"></span>**{nombre}** ({motor}) - {status}', unsafe_allow_html=True)

    tab_logistica, tab_finanzas, tab_reconstruccion = st.tabs([
        "Logistica Local Palmasola",
        "Boveda Financiera Central",
        "Reconstruccion Global Hibrida",
    ])

    with tab_logistica:
        st.markdown("### Registrar Despacho - Planta Palmasola")
        surtidores = info["surtidores"]
        surtidor_nombres = {v: k for k, v in surtidores.items()}
        surtidor_seleccionado = st.selectbox("Surtidor destino", list(surtidor_nombres.keys()), key="sel_surt_sc")
        id_surtidor = surtidor_nombres[surtidor_seleccionado]

        carburante_nombres = {v: k for k, v in CARBURANTES.items()}
        carburante_seleccionado = st.selectbox("Tipo de carburante", list(carburante_nombres.keys()), key="sel_carb_sc")
        id_carburante = carburante_nombres[carburante_seleccionado]

        litros = st.number_input("Litros solicitados", min_value=1000, step=1000, key="num_litros_sc")
        placa = st.text_input("Placa cisterna", placeholder="Ej: 9822-XPT", key="txt_placa_sc")

        if st.button("APROBAR DESPACHO - Protocolo 2PC", key="btn_despacho_sc", type="primary", use_container_width=True):
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
                        icon = "OK" if step["estado"] == "ok" else "FAIL"
                        detalle = f" ({step['detalle']})" if "detalle" in step else ""
                        if step["estado"] == "ok":
                            st.markdown(f"`[{icon}]` {step['paso']}{detalle}")
                        else:
                            st.markdown(f"`[{icon}]` **{step['paso']}**{detalle}")

                if resultado["ok"]:
                    st.success(f"Despacho registrado. ID Despacho: {resultado.get('id_despacho', 'N/A')}")
                else:
                    st.error("Transaccion fallida. Revisa el log.")

        df = _safe_query(get_engine_santacruz, "SELECT * FROM despachos_sc", fallback_conn_func=get_conn_santacruz)
        if not df.empty:
            st.dataframe(df, hide_index=True)

    with tab_finanzas:
        st.markdown("""
        <div style="border:1px solid #CC0000;border-radius:8px;padding:12px 16px;background:#FFF5F5;margin-bottom:12px;">
            <strong style="color:#CC0000;">DESPACHOS_FINANZAS</strong> — Datos Macroeconomicos Confidenciales<br>
            <span style="color:#71717a;font-size:0.8rem;">Nivel de Acceso: Solo Sede Central</span>
        </div>
        """, unsafe_allow_html=True)

        df = _safe_query(get_engine_santacruz, "SELECT * FROM despachos_finanzas ORDER BY id_despacho", fallback_conn_func=get_conn_santacruz)
        if not df.empty:
            df_display = df.copy()
            df_display["costo_importacion_real"] = df_display["costo_importacion_real"].apply(lambda x: f"Bs. {x:,.2f}")
            df_display["subvencion_asumida_bs"] = df_display["subvencion_asumida_bs"].apply(lambda x: f"Bs. {x:,.2f}")
            st.dataframe(df_display, hide_index=True)
            total_sub = df["subvencion_asumida_bs"].sum()
            total_cos = df["costo_importacion_real"].sum()
            st.markdown(f"**Total Subvencion Acumulada:** Bs. {total_sub:,.2f}")
            st.markdown(f"**Total Costo Importacion:** Bs. {total_cos:,.2f}")
        else:
            st.info("No se pudieron consultar los datos financieros. Verifica la conexion a Santa Cruz.")

    with tab_reconstruccion:
        st.markdown("### Reconstruccion Distribuida Hibrida")
        st.markdown("Ejecuta la union de los 3 fragmentos operativos y la junta con la tabla financiera central.")

        if st.button("EJECUTAR RECONSTRUCCION DISTRIBUIDA", key="btn_reconstruir", type="primary", use_container_width=True):
            progress_text = st.empty()
            progress_bar = st.progress(0, text="Extrayendo datos La Paz (PostgreSQL)...")
            progress_bar.progress(15, text="Extrayendo datos La Paz (PostgreSQL)...")
            import time
            time.sleep(0.8)
            progress_bar.progress(35, text="Extrayendo datos Cochabamba (MySQL)...")
            time.sleep(0.8)
            progress_bar.progress(55, text="Extrayendo datos Santa Cruz (PostgreSQL)...")
            time.sleep(0.8)
            progress_bar.progress(75, text="Ejecutando pd.concat() - Union horizontal...")
            time.sleep(0.5)
            progress_bar.progress(90, text="Ejecutando pd.merge() - Junta vertical...")
            time.sleep(0.5)

            resultado = ejecutar_reconstruccion()
            progress_bar.progress(100, text="Reconstruccion completada")
            progress_text.empty()

            if resultado["ok"]:
                st.session_state.df_reconstruido = resultado["df_final"]
                for nodo, disponible in resultado["nodos_disponibles"].items():
                    icon = "Online" if disponible else "Offline"
                    st.markdown(f"- **{nodo}**: {icon}")
                st.info(f"Reconstruccion completada en **{resultado['tiempo_segundos']}s**")
                if resultado.get("error"):
                    st.warning(resultado["error"])

                df_final = resultado["df_final"]
                if df_final is not None and not df_final.empty:
                    st.markdown("#### Tabla DESPACHOS Reconstruida al 100%")
                    column_config = {}
                    for col in df_final.columns:
                        if col in ["litros_despachados", "id_despacho", "id_pedido", "id_plantas"]:
                            column_config[col] = st.column_config.NumberColumn(format="%d")
                        elif col in ["costo_importacion_real", "subvencion_asumida_bs"]:
                            column_config[col] = st.column_config.NumberColumn(format="Bs. %,.2f")
                        elif col == "fecha_despacho":
                            column_config[col] = st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm")
                    st.dataframe(df_final, hide_index=True, column_config=column_config)

                    total_litros = df_final["litros_despachados"].sum()
                    total_costo = df_final["costo_importacion_real"].sum()
                    total_subvencion = df_final["subvencion_asumida_bs"].sum()
                    total_despachos = len(df_final)

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Litros", f"{total_litros:,}")
                    m2.metric("Costo Importacion", f"Bs. {total_costo:,.2f}")
                    m3.metric("Subvencion Asumida", f"Bs. {total_subvencion:,.2f}")
                    m4.metric("Despachos", f"{total_despachos}")

                    df_barras, df_donut = obtener_datos_graficos(df_final)
                    if df_barras is not None:
                        st.markdown("#### Abastecimiento por Departamento (Litros)")
                        colores = {"La Paz": "#003366", "Cochabamba": "#198754", "Santa Cruz": "#CC0000"}
                        fig_barras = go.Figure()
                        for dept in df_barras["Departamento"].unique():
                            fila = df_barras[df_barras["Departamento"] == dept]
                            fig_barras.add_trace(go.Bar(x=fila["Departamento"], y=fila["Litros Despachados"], name=dept, marker_color=colores.get(dept, "#003366"), text=fila["Litros Despachados"].apply(lambda x: f"{x:,}"), textposition="outside"))
                        fig_barras.update_layout(xaxis_title="Departamento", yaxis_title="Litros", showlegend=False, height=380, margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor="white")
                        st.plotly_chart(fig_barras, use_container_width=True)

                    if df_donut is not None:
                        st.markdown("#### Distribucion de Subvencion Fiscal por Carburante")
                        fig_donut = go.Figure(data=[go.Pie(labels=df_donut["Carburante"], values=df_donut["Subvencion (Bs.)"], hole=0.5, marker_colors=["#003366", "#198754", "#CC0000"], textinfo="label+percent", texttemplate="%{label}<br>Bs. %{value:,.2f}<br>(%{percent})", hovertemplate="%{label}: Bs. %{value:,.2f}<extra></extra>")])
                        fig_donut.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), showlegend=True, plot_bgcolor="white")
                        st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.error(f"{resultado['error']}")

        elif st.session_state.get("df_reconstruido") is not None:
            df_final = st.session_state.df_reconstruido
            st.success("Datos de la ultima reconstruccion disponibles")
            column_config = {}
            for col in df_final.columns:
                if col in ["litros_despachados", "id_despacho", "id_pedido", "id_plantas"]:
                    column_config[col] = st.column_config.NumberColumn(format="%d")
                elif col in ["costo_importacion_real", "subvencion_asumida_bs"]:
                    column_config[col] = st.column_config.NumberColumn(format="Bs. %,.2f")
                elif col == "fecha_despacho":
                    column_config[col] = st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm")
            st.dataframe(df_final, hide_index=True, column_config=column_config)