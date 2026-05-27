import streamlit as st
import graphviz


def render():
    st.markdown("## \U0001f4ca Monitor del Modelo de Datos")
    st.markdown("Visualiza la arquitectura del sistema distribuido YPFB")

    tab_a, tab_b = st.tabs(["\U0001f4cb Modelo Base (ER)", "\U0001f5fa\ufe0f Esquema de Fragmentacion"])

    with tab_a:
        st.markdown("### Diagrama Entidad-Relacion Centralizado")
        st.markdown("Modelo original antes de la fragmentacion geografica")

        dot = graphviz.Digraph(comment="ER YPFB", format="png")
        dot.attr(rankdir="TB", bgcolor="#F8F9FA", fontname="Arial", dpi="150")
        dot.attr("node", shape="record", style="filled", fillcolor="#FFFFFF", fontname="Arial", fontsize="10")
        dot.attr("edge", fontname="Arial", fontsize="9")

        dot.node("plantas", "PLANTAS\n{id_plantas PK | nombre_planta | departamento}", fillcolor="#E3F2FD")
        dot.node("carburantes", "CARBURANTES\n{id_carburante PK | nombre | precio_surtidor_anh}", fillcolor="#E3F2FD")
        dot.node("surtidores", "SURTIDORES\n{id_surtidor PK | nombre_surtidor | departamento}", fillcolor="#E3F2FD")
        dot.node("stock", "STOCK_PLANTAS\n{id_stock PK | id_plantas FK | id_carburante FK | stock_disponible_litros}", fillcolor="#FFF3E0")
        dot.node("pedidos", "PEDIDOS_WEB\n{id_pedido PK | id_surtidor FK | id_carburante FK | cantidad_litros_solicitados | fecha_solicitud | estado}", fillcolor="#FFF3E0")
        dot.node("despachos", "DESPACHOS\n{id_despacho PK | id_pedido FK | id_plantas FK | litros_despachados | fecha_despacho | placa_cisterna | costo_importacion_real | subvencion_asumida_bs}", fillcolor="#E8F5E9")

        dot.edge("plantas", "stock", label="1:N", color="#003366")
        dot.edge("carburantes", "stock", label="1:N", color="#003366")
        dot.edge("carburantes", "pedidos", label="1:N", color="#003366")
        dot.edge("surtidores", "pedidos", label="1:N", color="#003366")
        dot.edge("pedidos", "despachos", label="1:1", color="#CC0000")
        dot.edge("plantas", "despachos", label="1:N", color="#003366")

        st.graphviz_chart(dot, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Tablas del Modelo Centralizado")
        datos_modelo = {
            "PLANTAS": ["id_plantas (PK)", "nombre_planta", "departamento"],
            "CARBURANTES": ["id_carburante (PK)", "nombre", "precio_surtidor_anh"],
            "SURTIDORES": ["id_surtidor (PK)", "nombre_surtidor", "departamento"],
            "STOCK_PLANTAS": ["id_stock (PK)", "id_plantas (FK)", "id_carburante (FK)", "stock_disponible_litros"],
            "PEDIDOS_WEB": ["id_pedido (PK)", "id_surtidor (FK)", "id_carburante (FK)", "cantidad_litros_solicitados", "fecha_solicitud", "estado"],
            "DESPACHOS": ["id_despacho (PK)", "id_pedido (FK)", "id_plantas (FK)", "litros_despachados", "fecha_despacho", "placa_cisterna", "costo_importacion_real", "subvencion_asumida_bs"],
        }
        for tabla, campos in datos_modelo.items():
            st.markdown(f"**{tabla}**: {', '.join(campos)}")

    with tab_b:
        st.markdown("### Esquema de Fragmentacion Distribuida")
        st.markdown("Como se dividieron las tablas entre los 3 nodos geograficos")

        frag_horizontal_stock, frag_horizontal_pedidos, frag_hibrida, frag_reconstruccion = st.tabs([
            "\U0001f4c8 Fragmentacion Horizontal - STOCK_PLANTAS",
            "\U0001f4c9 Fragmentacion Horizontal - PEDIDOS_WEB",
            "\U0001f504 Fragmentacion Hibrida - DESPACHOS",
            "\U0001f501 Reconstruccion Global",
        ])

        with frag_horizontal_stock:
            st.markdown("#### STOCK_PLANTAS - Fragmentacion Horizontal Primaria")
            st.markdown("La tabla se fragmenta por **id_plantas** asignando filas a cada nodo segun su planta.")

            col_lp, col_cb, col_sc = st.columns(3)

            with col_lp:
                st.markdown("""
                <div style="border:2px solid #003366; border-radius:10px; padding:12px; background:#E3F2FD;">
                <h4 style="color:#003366; margin:0;">\U0001f3d4\ufe0f PC1 - La Paz</h4>
                <p style="font-size:0.8rem; color:#333;">\u03c3 id_plantas = 10 (STOCK_PLANTAS)</p>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(
                    data={"id_stock": [1001, 1002, 1003], "id_plantas": [10, 10, 10], "id_carburante": [1, 2, 3], "stock_disponible_litros": [500000, 750000, 120000]},
                    hide_index=True,
                    use_container_width=True,
                )

            with col_cb:
                st.markdown("""
                <div style="border:2px solid #198754; border-radius:10px; padding:12px; background:#E8F5E9;">
                <h4 style="color:#198754; margin:0;">\U0001f33f PC2 - Cochabamba</h4>
                <p style="font-size:0.8rem; color:#333;">\u03c3 id_plantas = 20 (STOCK_PLANTAS)</p>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(
                    data={"id_stock": [2001, 2002], "id_plantas": [20, 20], "id_carburante": [1, 2], "stock_disponible_litros": [420000, 600000]},
                    hide_index=True,
                    use_container_width=True,
                )

            with col_sc:
                st.markdown("""
                <div style="border:2px solid #CC0000; border-radius:10px; padding:12px; background:#FFEBEE;">
                <h4 style="color:#CC0000; margin:0;">\U0001f3db\ufe0f PC3 - Santa Cruz</h4>
                <p style="font-size:0.8rem; color:#333;">\u03c3 id_plantas = 30 (STOCK_PLANTAS)</p>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(
                    data={"id_stock": [3001, 3002], "id_plantas": [30, 30], "id_carburante": [1, 2], "stock_disponible_litros": [900000, 1200000]},
                    hide_index=True,
                    use_container_width=True,
                )

            st.markdown("---")
            st.markdown("**Reconstruccion:** STOCK_PLANTAS_Global = PC1 \u222a PC2 \u222a PC3")

        with frag_horizontal_pedidos:
            st.markdown("#### PEDIDOS_WEB - Fragmentacion Horizontal Primaria")
            st.markdown("La tabla se fragmenta por surtidores asignados a cada departamento.")

            col_lp, col_cb, col_sc = st.columns(3)

            with col_lp:
                st.markdown("""
                <div style="border:2px solid #003366; border-radius:10px; padding:12px; background:#E3F2FD;">
                <h4 style="color:#003366; margin:0;">\U0001f3d4\ufe0f PC1 - La Paz</h4>
                <p style="font-size:0.8rem; color:#333;">Surtidores 101, 102 | IDs 10XXX</p>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(
                    data={"id_pedido": [10001, 10002], "id_surtidor": [101, 102], "id_carburante": [1, 2], "cantidad_litros_solicitados": [15000, 20000], "fecha_solicitud": ["2026-05-25 08:30:00", "2026-05-25 09:15:00"], "estado": ["Despachado", "Despachado"]},
                    hide_index=True,
                    use_container_width=True,
                )

            with col_cb:
                st.markdown("""
                <div style="border:2px solid #198754; border-radius:10px; padding:12px; background:#E8F5E9;">
                <h4 style="color:#198754; margin:0;">\U0001f33f PC2 - Cochabamba</h4>
                <p style="font-size:0.8rem; color:#333;">Surtidores 201, 202 | IDs 20XXX</p>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(
                    data={"id_pedido": [20001, 20002], "id_surtidor": [201, 202], "id_carburante": [1, 2], "cantidad_litros_solicitados": [12000, 18000], "fecha_solicitud": ["2026-05-25 07:45:00", "2026-05-25 09:30:00"], "estado": ["Despachado", "Despachado"]},
                    hide_index=True,
                    use_container_width=True,
                )

            with col_sc:
                st.markdown("""
                <div style="border:2px solid #CC0000; border-radius:10px; padding:12px; background:#FFEBEE;">
                <h4 style="color:#CC0000; margin:0;">\U0001f3db\ufe0f PC3 - Santa Cruz</h4>
                <p style="font-size:0.8rem; color:#333;">Surtidor 301 | IDs 30XXX</p>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(
                    data={"id_pedido": [30001], "id_surtidor": [301], "id_carburante": [1], "cantidad_litros_solicitados": [25000], "fecha_solicitud": ["2026-05-25 06:00:00"], "estado": ["Despachado"]},
                    hide_index=True,
                    use_container_width=True,
                )

            st.markdown("---")
            st.markdown("**Reconstruccion:** PEDIDOS_WEB_Global = PC1 \u222a PC2 \u222a PC3")

        with frag_hibrida:
            st.markdown("#### DESPACHOS - Fragmentacion Hibrida (Vertical + Horizontal)")
            st.markdown("Se separan columnas confidenciales (vertical) y se distribuyen filas por planta (horizontal).")

            st.markdown("##### PASO A: Corte Vertical (Separacion de Columnas)")
            col_op, col_fin = st.columns(2)

            with col_op:
                st.markdown("""
                <div style="border:2px solid #003366; border-radius:10px; padding:12px; background:#E3F2FD;">
                <h4 style="color:#003366; margin:0;">DESPACHOS_OPERATIVOS</h4>
                <p style="font-size:0.8rem; color:#333;">Columnas operativas distribuidas a los 3 nodos</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("- id_despacho (PK)\n- id_pedido (FK)\n- id_plantas (FK)\n- litros_despachados\n- fecha_despacho\n- placa_cisterna")

            with col_fin:
                st.markdown("""
                <div style="border:2px solid #198754; border-radius:10px; padding:12px; background:#E8F5E9;">
                <h4 style="color:#198754; margin:0;">DESPACHOS_FINANZAS</h4>
                <p style="font-size:0.8rem; color:#333;">Columnas financieras exclusivas de Santa Cruz</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("- id_despacho (PK)\n- costo_importacion_real\n- subvencion_asumida_bs")

            st.markdown("##### PASO B: Corte Horizontal (Distribucion por Filas)")
            col_lp, col_cb, col_sc = st.columns(3)

            with col_lp:
                st.markdown("""
                <div style="border:2px solid #003366; border-radius:10px; padding:10px; background:#E3F2FD; text-align:center;">
                <strong style="color:#003366;">PC1 - La Paz</strong><br>
                <span style="font-size:0.75rem;">\u03c3 id_plantas = 10<br>IDs 15XXX<br>PostgreSQL 17</span>
                </div>
                """, unsafe_allow_html=True)

            with col_cb:
                st.markdown("""
                <div style="border:2px solid #198754; border-radius:10px; padding:10px; background:#E8F5E9; text-align:center;">
                <strong style="color:#198754;">PC2 - Cochabamba</strong><br>
                <span style="font-size:0.75rem;">\u03c3 id_plantas = 20<br>IDs 25XXX<br>MySQL 8</span>
                </div>
                """, unsafe_allow_html=True)

            with col_sc:
                st.markdown("""
                <div style="border:2px solid #CC0000; border-radius:10px; padding:10px; background:#FFEBEE; text-align:center;">
                <strong style="color:#CC0000;">PC3 - Santa Cruz</strong><br>
                <span style="font-size:0.75rem;">\u03c3 id_plantas = 30<br>IDs 35XXX<br>PostgreSQL 15+<br>+ DESPACHOS_FINANZAS</span>
                </div>
                """, unsafe_allow_html=True)

        with frag_reconstruccion:
            st.markdown("#### Pipeline de Reconstruccion Global Hibrida")
            st.markdown("El proceso reconstruye la tabla DESPACHOS completa en 3 fases usando Pandas.")

            st.markdown("**FASE 1: Extraccion de Fragmentos**")
            st.code("""
df_LP   = pd.read_sql('SELECT * FROM despachos_lp', conn_LP)
df_CBBA = pd.read_sql('SELECT * FROM despachos_cbba', conn_CBBA)
df_SC   = pd.read_sql('SELECT * FROM despachos_sc', conn_SC)
            """, language="python")

            st.markdown("**FASE 2: Union Horizontal (\u222a) - Emula UNION ALL**")
            st.code("""
df_operativos = pd.concat([df_LP, df_CBBA, df_SC], ignore_index=True)
            """, language="python")

            st.markdown("**FASE 3: Junta Vertical (\u22c8) con tabla financiera de Santa Cruz**")
            st.code("""
df_finanzas = pd.read_sql('SELECT * FROM despachos_finanzas', conn_SC)
df_final = pd.merge(df_operativos, df_finanzas, on='id_despacho', how='inner')
            """, language="python")

            st.markdown("---")
            st.markdown("**Resultado Final: DESPACHOS reconstruido al 100%**")
            st.markdown("""
            <div style="border:2px solid #198754; border-radius:10px; padding:15px; background:#E8F5E9;">
            <p style="margin:0; font-size:0.9rem; color:#1a1a1a;">
            <strong>DESPACHOS_Global</strong> = DESPACHOS_OPERATIVOS_Global \u22c8<sub>id_despacho</sub> DESPACHOS_FINANZAS<br><br>
            Columnas operativas (azul) + Columnas financieras (verde) = Tabla completa
            </p>
            </div>
            """, unsafe_allow_html=True)