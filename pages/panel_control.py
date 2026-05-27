import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import SEDES, CARBURANTES, PRECIOS_CARBURANTES
from conexiones import get_conn_by_sede, get_conn_santacruz, get_engine_by_sede, get_engine_santacruz, estado_nodos
from protocolo_2pc import ejecutar_2pc
from reconstruccion import (
    ejecutar_reconstruccion,
    obtener_datos_graficos,
    obtener_pedidos_por_sede,
)


def render():
    sede = st.session_state.get("sede_activa")

    if not sede:
        st.warning("\u26a0\ufe0f No has seleccionado una sede. Regresa al inicio para seleccionar.")
        if st.button("\U0001f3e0 Ir al Inicio"):
            st.session_state.pagina = "Inicio"
            st.rerun()
        return

    info = SEDES[sede]
    estado = estado_nodos()

    if sede in ["La Paz", "Cochabamba"]:
        _render_operador_regional(sede, info, estado)
    elif sede == "Santa Cruz":
        _render_gerente_nacional(sede, info, estado)


def _render_operador_regional(sede, info, estado):
    color = info["color"]
    icono = info["icono"]
    motor = info["motor"]
    puerto = "5432" if motor == "PostgreSQL" else "3306"

    st.markdown(f"""
    <div style="background:{color}; border-radius:12px; padding:16px 24px; margin-bottom:20px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:2rem;">{icono}</span>
            <div>
                <h2 style="color:white; margin:0; font-size:1.4rem;">Operador Regional - {sede}</h2>
                <p style="color:#FFFFFFCC; margin:2px 0 0 0; font-size:0.85rem;">
                    {info['planta_nombre']} \u2022 {info['badge']}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    indicador = "\U0001f7e2 Conectado" if estado.get(sede, False) else "\U0001f534 Desconectado"
    st.markdown(f"**{indicador}** \u2022 {motor} \u2022 Puerto {puerto}")

    if not estado.get(sede, False):
        st.warning(f"\u26a0\ufe0f Nodo {sede} no disponible - Verifica la conexion a la base de datos local")

    col_form, col_datos = st.columns(2)

    with col_form:
        st.markdown("### \U0001f4cb Registrar Nuevo Despacho")

        surtidores = info["surtidores"]
        surtidor_nombres = {v: k for k, v in surtidores.items()}
        surtidor_seleccionado = st.selectbox("Surtidor destino", list(surtidor_nombres.keys()), key=f"sel_surt_{sede}")
        id_surtidor = surtidor_nombres[surtidor_seleccionado]

        carburante_nombres = {v: k for k, v in CARBURANTES.items()}
        carburante_seleccionado = st.selectbox("Tipo de carburante", list(carburante_nombres.keys()), key=f"sel_carb_{sede}")
        id_carburante = carburante_nombres[carburante_seleccionado]

        litros = st.number_input("Litros solicitados", min_value=1000, step=1000, key=f"num_litros_{sede}")
        placa = st.text_input("Placa cisterna", placeholder="Ej: 2345-PKD", key=f"txt_placa_{sede}")

        if st.button(f"\U0001f69b APROBAR DESPACHO - Ejecutar Protocolo 2PC", key=f"btn_despacho_{sede}", use_container_width=True):
            if not placa:
                st.error("\u274c La placa del cisterna es obligatoria")
            elif litros <= 0:
                st.error("\u274c Los litros deben ser mayores a 0")
            else:
                with st.spinner("\u23f3 Ejecutando Protocolo 2PC..."):
                    resultado = ejecutar_2pc(sede, id_surtidor, id_carburante, litros, placa.upper())

                st.session_state.log_2pc = resultado.get("log", [])

                with st.expander("\U0001f4dc Log del Protocolo 2PC", expanded=True):
                    for step in st.session_state.log_2pc:
                        estado_icon = "\u2705" if step["estado"] == "ok" else "\u274c"
                        detalle = f" ({step['detalle']})" if "detalle" in step else ""
                        if step["estado"] == "ok":
                            st.markdown(f"{estado_icon} {step['paso']}{detalle}")
                        else:
                            st.markdown(f"{estado_icon} **{step['paso']}**{detalle}")

                if resultado["ok"]:
                    st.success(f"\u2705 Despacho registrado exitosamente. ID Despacho: {resultado.get('id_despacho', 'N/A')}")
                else:
                    st.error(f"\u274c Transaccion fallida. Revisa el log para mas detalles.")

    with col_datos:
        st.markdown(f"### \U0001f4e6 Fragmento Local - {sede}")

        tab_stock, tab_pedidos, tab_despachos = st.tabs(["\U0001f4e5 Stock Local", "\U0001f4ec Pedidos Locales", "\U0001f69b Despachos Locales"])

        with tab_stock:
            try:
                engine = get_engine_by_sede(sede)
                df_stock = pd.read_sql_query(
                    "SELECT s.id_stock, p.nombre_planta, c.nombre as carburante, s.stock_disponible_litros "
                    "FROM stock_plantas s JOIN plantas p ON s.id_plantas = p.id_plantas "
                    "JOIN carburantes c ON s.id_carburante = c.id_carburante "
                    "WHERE s.id_plantas = %s",
                    engine,
                    params=(info["planta_id"],)
                )
                st.dataframe(df_stock, hide_index=True)
                engine.dispose()
            except Exception:
                try:
                    engine.dispose()
                except Exception:
                    pass
                try:
                    conn = get_conn_by_sede(sede)
                    df_stock = pd.read_sql_query(
                        "SELECT s.id_stock, p.nombre_planta, c.nombre as carburante, s.stock_disponible_litros "
                        "FROM stock_plantas s JOIN plantas p ON s.id_plantas = p.id_plantas "
                        "JOIN carburantes c ON s.id_carburante = c.id_carburante "
                        "WHERE s.id_plantas = %s", conn, params=(info["planta_id"],)
                    )
                    st.dataframe(df_stock, hide_index=True)
                    conn.close()
                except Exception as e2:
                    st.error(f"Error al consultar stock local: {e2}")

        with tab_pedidos:
            try:
                engine = get_engine_by_sede(sede)
                df_pedidos = pd.read_sql_query("SELECT * FROM pedidos_web", engine)
                st.dataframe(df_pedidos, hide_index=True)
                engine.dispose()
            except Exception:
                try:
                    engine.dispose()
                except Exception:
                    pass
                try:
                    conn = get_conn_by_sede(sede)
                    df_pedidos = pd.read_sql_query("SELECT * FROM pedidos_web", conn)
                    st.dataframe(df_pedidos, hide_index=True)
                    conn.close()
                except Exception as e:
                    st.error(f"Error al consultar pedidos locales: {e}")

        with tab_despachos:
            try:
                engine = get_engine_by_sede(sede)
                df_despachos = pd.read_sql_query(f"SELECT * FROM {info['tabla_despacho']}", engine)
                st.dataframe(df_despachos, hide_index=True)
                engine.dispose()
            except Exception:
                try:
                    engine.dispose()
                except Exception:
                    pass
                try:
                    conn = get_conn_by_sede(sede)
                    df_despachos = pd.read_sql_query(f"SELECT * FROM {info['tabla_despacho']}", conn)
                    st.dataframe(df_despachos, hide_index=True)
                    conn.close()
                except Exception as e:
                    st.error(f"Error al consultar despachos locales: {e}")

    st.markdown("---")
    if st.button("\U0001f512 Intentar acceder a datos financieros", key=f"btn_finanzas_{sede}"):
        st.error("\U0001f512 ACCESO DENEGADO: Datos confidenciales centralizados en la Sede Central - Santa Cruz")


def _render_gerente_nacional(sede, info, estado):
    color = info["color"]
    icono = info["icono"]

    st.markdown(f"""
    <div style="background:{color}; border-radius:12px; padding:16px 24px; margin-bottom:20px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:2rem;">{icono}</span>
            <div>
                <h2 style="color:white; margin:0; font-size:1.4rem;">\U0001f451 Gerente Nacional \u2022 Sede Central</h2>
                <p style="color:#FFFFFFCC; margin:2px 0 0 0; font-size:0.85rem;">
                    {info['planta_nombre']} \u2022 Nodo Coordinador Padre
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        indicador_lp = "\U0001f7e2" if estado.get("La Paz", False) else "\U0001f534"
        st.markdown(f"{indicador_lp} **La Paz** (PostgreSQL)")
    with c2:
        indicador_cb = "\U0001f7e2" if estado.get("Cochabamba", False) else "\U0001f534"
        st.markdown(f"{indicador_cb} **Cochabamba** (MySQL)")
    with c3:
        indicador_sc = "\U0001f7e2" if estado.get("Santa Cruz", False) else "\U0001f534"
        st.markdown(f"{indicador_sc} **Santa Cruz** (PostgreSQL)")

    tab_logistica, tab_finanzas, tab_reconstruccion = st.tabs([
        "\U0001f69b Logistica Local Palmasola",
        "\U0001f4b0 BOveda Financiera Central",
        "\U0001f310 Reconstruccion Global Hibrida",
    ])

    with tab_logistica:
        st.markdown("### \U0001f4cb Registrar Despacho - Planta Palmasola")

        surtidores = info["surtidores"]
        surtidor_nombres = {v: k for k, v in surtidores.items()}
        surtidor_seleccionado = st.selectbox("Surtidor destino", list(surtidor_nombres.keys()), key="sel_surt_sc")
        id_surtidor = surtidor_nombres[surtidor_seleccionado]

        carburante_nombres = {v: k for k, v in CARBURANTES.items()}
        carburante_seleccionado = st.selectbox("Tipo de carburante", list(carburante_nombres.keys()), key="sel_carb_sc")
        id_carburante = carburante_nombres[carburante_seleccionado]

        litros = st.number_input("Litros solicitados", min_value=1000, step=1000, key="num_litros_sc")
        placa = st.text_input("Placa cisterna", placeholder="Ej: 9822-XPT", key="txt_placa_sc")

        if st.button("\U0001f69b APROBAR DESPACHO - Ejecutar Protocolo 2PC", key="btn_despacho_sc", use_container_width=True):
            if not placa:
                st.error("\u274c La placa del cisterna es obligatoria")
            elif litros <= 0:
                st.error("\u274c Los litros deben ser mayores a 0")
            else:
                with st.spinner("\u23f3 Ejecutando Protocolo 2PC..."):
                    resultado = ejecutar_2pc(sede, id_surtidor, id_carburante, litros, placa.upper())

                st.session_state.log_2pc = resultado.get("log", [])

                with st.expander("\U0001f4dc Log del Protocolo 2PC", expanded=True):
                    for step in st.session_state.log_2pc:
                        estado_icon = "\u2705" if step["estado"] == "ok" else "\u274c"
                        detalle = f" ({step['detalle']})" if "detalle" in step else ""
                        if step["estado"] == "ok":
                            st.markdown(f"{estado_icon} {step['paso']}{detalle}")
                        else:
                            st.markdown(f"{estado_icon} **{step['paso']}**{detalle}")

                if resultado["ok"]:
                    st.success(f"\u2705 Despacho registrado exitosamente. ID Despacho: {resultado.get('id_despacho', 'N/A')}")
                else:
                    st.error("\u274c Transaccion fallida. Revisa el log para mas detalles.")

        try:
            engine = get_engine_santacruz()
            df_despachos_sc = pd.read_sql_query("SELECT * FROM despachos_sc", engine)
            st.dataframe(df_despachos_sc, hide_index=True)
            engine.dispose()
        except Exception:
            try:
                engine.dispose()
            except Exception:
                pass
            try:
                conn = get_conn_by_sede(sede)
                df_despachos_sc = pd.read_sql_query("SELECT * FROM despachos_sc", conn)
                st.dataframe(df_despachos_sc, hide_index=True)
                conn.close()
            except Exception as e:
                st.error(f"Error al consultar despachos locales: {e}")

    with tab_finanzas:
        st.markdown("""
        <div style="border:2px solid #CC0000; border-radius:10px; padding:15px; background:#FFEBEE; margin-bottom:15px;">
        <h3 style="color:#CC0000; margin:0;">\U0001f4b0 DESPACHOS_FINANZAS — Datos Macroeconomicos Confidenciales</h3>
        <p style="color:#6c757d; margin:5px 0 0 0; font-size:0.8rem;">\U0001f512 Nivel de Acceso: Solo Sede Central</p>
        </div>
        """, unsafe_allow_html=True)

        try:
            engine = get_engine_santacruz()
            df_finanzas = pd.read_sql_query("SELECT * FROM despachos_finanzas ORDER BY id_despacho", engine)
            engine.dispose()

            df_finanzas_display = df_finanzas.copy()
            df_finanzas_display["costo_importacion_real"] = df_finanzas_display["costo_importacion_real"].apply(lambda x: f"Bs. {x:,.2f}")
            df_finanzas_display["subvencion_asumida_bs"] = df_finanzas_display["subvencion_asumida_bs"].apply(lambda x: f"Bs. {x:,.2f}")

            st.dataframe(df_finanzas_display, hide_index=True)

            total_subvencion = df_finanzas["subvencion_asumida_bs"].sum()
            total_costo = df_finanzas["costo_importacion_real"].sum()
            st.markdown(f"**Total Subvencion Acumulada:** Bs. {total_subvencion:,.2f}")
            st.markdown(f"**Total Costo Importacion:** Bs. {total_costo:,.2f}")

        except Exception as e:
            try:
                engine.dispose()
            except Exception:
                pass
            try:
                conn = get_conn_santacruz()
                df_finanzas = pd.read_sql_query("SELECT * FROM despachos_finanzas ORDER BY id_despacho", conn)
                conn.close()

                df_finanzas_display = df_finanzas.copy()
                df_finanzas_display["costo_importacion_real"] = df_finanzas_display["costo_importacion_real"].apply(lambda x: f"Bs. {x:,.2f}")
                df_finanzas_display["subvencion_asumida_bs"] = df_finanzas_display["subvencion_asumida_bs"].apply(lambda x: f"Bs. {x:,.2f}")

                st.dataframe(df_finanzas_display, hide_index=True)

                total_subvencion = df_finanzas["subvencion_asumida_bs"].sum()
                total_costo = df_finanzas["costo_importacion_real"].sum()
                st.markdown(f"**Total Subvencion Acumulada:** Bs. {total_subvencion:,.2f}")
                st.markdown(f"**Total Costo Importacion:** Bs. {total_costo:,.2f}")
            except Exception as e2:
                st.error(f"Error al consultar datos financieros: {e2}")

    with tab_reconstruccion:
        st.markdown("### \U0001f310 Reconstruccion Distribuida Hibrida")
        st.markdown("Ejecuta la union de los 3 fragmentos operativos y la junta con la tabla financiera central.")

        if st.button("\u26a1 EJECUTAR RECONSTRUCCION DISTRIBUIDA", key="btn_reconstruir", use_container_width=True):
            progress_text = st.empty()
            progress_bar = st.progress(0)

            progress_text.markdown("\U0001f504 Extrayendo datos La Paz (PostgreSQL)...")
            progress_bar.progress(15)
            import time
            time.sleep(1)

            progress_text.markdown("\U0001f504 Extrayendo datos Cochabamba (MySQL)...")
            progress_bar.progress(35)
            time.sleep(1)

            progress_text.markdown("\U0001f504 Extrayendo datos Santa Cruz (PostgreSQL)...")
            progress_bar.progress(55)
            time.sleep(1)

            progress_text.markdown("\U0001f504 Ejecutando pd.concat() — Union horizontal \u222a...")
            progress_bar.progress(75)
            time.sleep(0.5)

            progress_text.markdown("\U0001f504 Ejecutando pd.merge() — Junta vertical \u22c8...")
            progress_bar.progress(90)
            time.sleep(0.5)

            resultado = ejecutar_reconstruccion()

            progress_bar.progress(100)
            progress_text.empty()

            if resultado["ok"]:
                st.session_state.df_reconstruido = resultado["df_final"]

                for nodo, disponible in resultado["nodos_disponibles"].items():
                    icon = "\u2705" if disponible else "\u274c"
                    st.markdown(f"{icon} **{nodo}**: {'Disponible' if disponible else 'No disponible'}")

                st.info(f"\u23f1 Reconstruccion completada en **{resultado['tiempo_segundos']} segundos**")

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
                    m1.metric("Total Litros Despachados", f"{total_litros:,}")
                    m2.metric("Total Costo Importacion", f"Bs. {total_costo:,.2f}")
                    m3.metric("Total Subvencion Asumida", f"Bs. {total_subvencion:,.2f}")
                    m4.metric("Despachos Consolidados", f"{total_despachos}")

                    df_barras, df_donut = obtener_datos_graficos(df_final)

                    if df_barras is not None:
                        st.markdown("#### \U0001f4ca Abastecimiento por Departamento (Litros)")
                        colores = {"La Paz": "#003366", "Cochabamba": "#198754", "Santa Cruz": "#CC0000"}
                        fig_barras = go.Figure()
                        for dept in df_barras["Departamento"].unique():
                            fila = df_barras[df_barras["Departamento"] == dept]
                            fig_barras.add_trace(go.Bar(
                                x=fila["Departamento"],
                                y=fila["Litros Despachados"],
                                name=dept,
                                marker_color=colores.get(dept, "#003366"),
                                text=fila["Litros Despachados"].apply(lambda x: f"{x:,}"),
                                textposition="outside",
                            ))
                        fig_barras.update_layout(
                            xaxis_title="Departamento",
                            yaxis_title="Litros Despachados",
                            showlegend=False,
                            height=400,
                            margin=dict(l=20, r=20, t=30, b=20),
                        )
                        st.plotly_chart(fig_barras, use_container_width=True)

                    if df_donut is not None:
                        st.markdown("#### \U0001f4b0 Distribucion de Subvencion Fiscal por Carburante")
                        fig_donut = go.Figure(data=[go.Pie(
                            labels=df_donut["Carburante"],
                            values=df_donut["Subvencion (Bs.)"],
                            hole=0.5,
                            marker_colors=["#003366", "#198754", "#CC0000"],
                            textinfo="label+percent",
                            texttemplate="%{label}<br>Bs. %{value:,.2f}<br>(%{percent})",
                            hovertemplate="%{label}: Bs. %{value:,.2f}<extra></extra>",
                        )])
                        fig_donut.update_layout(
                            height=400,
                            margin=dict(l=20, r=20, t=30, b=20),
                            showlegend=True,
                        )
                        st.plotly_chart(fig_donut, use_container_width=True)

            else:
                st.error(f"\u274c {resultado['error']}")

        elif st.session_state.get("df_reconstruido") is not None:
            df_final = st.session_state.df_reconstruido
            st.success("\u2705 Datos de la ultima reconstruccion disponibles")

            column_config = {}
            for col in df_final.columns:
                if col in ["litros_despachados", "id_despacho", "id_pedido", "id_plantas"]:
                    column_config[col] = st.column_config.NumberColumn(format="%d")
                elif col in ["costo_importacion_real", "subvencion_asumida_bs"]:
                    column_config[col] = st.column_config.NumberColumn(format="Bs. %,.2f")
                elif col == "fecha_despacho":
                    column_config[col] = st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm")

            st.dataframe(df_final, hide_index=True, column_config=column_config)