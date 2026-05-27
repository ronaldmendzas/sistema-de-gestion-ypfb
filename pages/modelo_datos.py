import streamlit as st
import pandas as pd


def render():
    st.markdown("## Monitor del Modelo de Datos")
    st.markdown("Visualiza la arquitectura del sistema distribuido YPFB")

    tab_a, tab_b = st.tabs(["Modelo Base (ER)", "Esquema de Fragmentacion"])

    with tab_a:
        st.markdown("### Diagrama Entidad-Relacion Centralizado")
        st.markdown("Modelo original antes de la fragmentacion geografica.")

        entidades = {
            "PLANTAS": {"pk": ["id_plantas"], "attrs": ["nombre_planta", "departamento"], "color": "#003366"},
            "CARBURANTES": {"pk": ["id_carburante"], "attrs": ["nombre", "precio_surtidor_anh"], "color": "#003366"},
            "SURTIDORES": {"pk": ["id_surtidor"], "attrs": ["nombre_surtidor", "departamento"], "color": "#003366"},
            "STOCK_PLANTAS": {"pk": ["id_stock"], "attrs": ["id_plantas (FK)", "id_carburante (FK)", "stock_disponible_litros"], "color": "#CC6600"},
            "PEDIDOS_WEB": {"pk": ["id_pedido"], "attrs": ["id_surtidor (FK)", "id_carburante (FK)", "cantidad_litros_solicitados", "fecha_solicitud", "estado"], "color": "#CC6600"},
            "DESPACHOS": {"pk": ["id_despacho"], "attrs": ["id_pedido (FK)", "id_plantas (FK)", "litros_despachados", "fecha_despacho", "placa_cisterna", "costo_importacion_real", "subvencion_asumida_bs"], "color": "#198754"},
        }

        relaciones = [
            ("PLANTAS", "STOCK_PLANTAS", "1:N"),
            ("CARBURANTES", "STOCK_PLANTAS", "1:N"),
            ("CARBURANTES", "PEDIDOS_WEB", "1:N"),
            ("SURtidores", "PEDIDOS_WEB", "1:N"),
            ("PEDIDOS_WEB", "DESPACHOS", "1:1"),
            ("PLANTAS", "DESPACHOS", "1:N"),
        ]

        cols = st.columns(3)
        for i, (nombre, datos) in enumerate(entidades.items()):
            with cols[i % 3]:
                bg = datos["color"] + "10"
                border = datos["color"]
                pk_text = ", ".join(datos["pk"])
                attrs_text = "<br>".join(datos["attrs"])
                st.markdown(f"""
                <div style="border:2px solid {border};border-radius:10px;padding:14px;background:{bg};margin-bottom:10px;">
                    <strong style="color:{border};font-size:0.9rem;">{nombre}</strong><br>
                    <span style="color:#71717a;font-size:0.75rem;"><strong>PK:</strong> {pk_text}</span><br>
                    <span style="color:#52525b;font-size:0.75rem;">{attrs_text}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Relaciones:**")
        for parent, child, card in relaciones:
            st.markdown(f"- **{parent}** {card} **{child}**")

    with tab_b:
        st.markdown("### Esquema de Fragmentacion Distribuida")
        st.markdown("Como se dividieron las tablas entre los 3 nodos geograficos.")

        tabs_frag = st.tabs([
            "STOCK_PLANTAS (Horizontal)",
            "PEDIDOS_WEB (Horizontal)",
            "DESPACHOS (Hibrida)",
            "Reconstruccion Global",
        ])

        with tabs_frag[0]:
            st.markdown("#### Fragmentacion Horizontal por id_plantas")
            col_lp, col_cb, col_sc = st.columns(3)
            with col_lp:
                st.markdown("**PC1 - La Paz**")
                st.markdown("`\u03c3 id_plantas = 10`")
                st.dataframe(pd.DataFrame({"id_stock": [1001,1002,1003], "id_plantas": [10,10,10], "id_carburante": [1,2,3], "stock_litros": [500000,750000,120000]}), hide_index=True)
            with col_cb:
                st.markdown("**PC2 - Cochabamba**")
                st.markdown("`\u03c3 id_plantas = 20`")
                st.dataframe(pd.DataFrame({"id_stock": [2001,2002], "id_plantas": [20,20], "id_carburante": [1,2], "stock_litros": [420000,600000]}), hide_index=True)
            with col_sc:
                st.markdown("**PC3 - Santa Cruz**")
                st.markdown("`\u03c3 id_plantas = 30`")
                st.dataframe(pd.DataFrame({"id_stock": [3001,3002], "id_plantas": [30,30], "id_carburante": [1,2], "stock_litros": [900000,1200000]}), hide_index=True)
            st.info("STOCK_PLANTAS_Global = PC1 \u222a PC2 \u222a PC3")

        with tabs_frag[1]:
            st.markdown("#### Fragmentacion Horizontal por surtidor")
            col_lp, col_cb, col_sc = st.columns(3)
            with col_lp:
                st.markdown("**PC1 - La Paz** (Surtidores 101,102)")
                st.dataframe(pd.DataFrame({"id_pedido": [10001,10002], "id_surtidor": [101,102], "id_carburante": [1,2], "litros": [15000,20000], "estado": ["Despachado","Despachado"]}), hide_index=True)
            with col_cb:
                st.markdown("**PC2 - Cochabamba** (Surtidores 201,202)")
                st.dataframe(pd.DataFrame({"id_pedido": [20001,20002], "id_surtidor": [201,202], "id_carburante": [1,2], "litros": [12000,18000], "estado": ["Despachado","Despachado"]}), hide_index=True)
            with col_sc:
                st.markdown("**PC3 - Santa Cruz** (Surtidor 301)")
                st.dataframe(pd.DataFrame({"id_pedido": [30001], "id_surtidor": [301], "id_carburante": [1], "litros": [25000], "estado": ["Despachado"]}), hide_index=True)
            st.info("PEDIDOS_WEB_Global = PC1 \u222a PC2 \u222a PC3")

        with tabs_frag[2]:
            st.markdown("#### Fragmentacion Hibrida (Vertical + Horizontal)")
            st.markdown("**Paso A: Corte Vertical**")
            col_op, col_fin = st.columns(2)
            with col_op:
                st.markdown("**DESPACHOS_OPERATIVOS** (distribuido a 3 nodos)")
                st.code("id_despacho, id_pedido, id_plantas,\nlitros_despachados, fecha_despacho, placa_cisterna", language="sql")
            with col_fin:
                st.markdown("**DESPACHOS_FINANZAS** (solo en Santa Cruz)")
                st.code("id_despacho, costo_importacion_real,\nsubvencion_asumida_bs", language="sql")

            st.markdown("**Paso B: Corte Horizontal por id_plantas**")
            col_lp, col_cb, col_sc = st.columns(3)
            with col_lp:
                st.markdown("**PC1 - La Paz**")
                st.code("\u03c3 id_plantas=10\nIDs: 15XXX\nPostgreSQL 17")
            with col_cb:
                st.markdown("**PC2 - Cochabamba**")
                st.code("\u03c3 id_plantas=20\nIDs: 25XXX\nMySQL 8")
            with col_sc:
                st.markdown("**PC3 - Santa Cruz**")
                st.code("\u03c3 id_plantas=30\nIDs: 35XXX\nPostgreSQL 15+\n+ DESPACHOS_FINANZAS")

        with tabs_frag[3]:
            st.markdown("#### Pipeline de Reconstruccion Global")
            st.code("""# FASE 1: Extraccion
df_LP   = pd.read_sql('SELECT * FROM despachos_lp', conn_LP)
df_CBBA = pd.read_sql('SELECT * FROM despachos_cbba', conn_CBBA)
df_SC   = pd.read_sql('SELECT * FROM despachos_sc', conn_SC)

# FASE 2: Union horizontal - emula UNION ALL
df_operativos = pd.concat([df_LP, df_CBBA, df_SC], ignore_index=True)

# FASE 3: Junta vertical con tabla financiera
df_finanzas = pd.read_sql('SELECT * FROM despachos_finanzas', conn_SC)
df_final = pd.merge(df_operativos, df_finanzas, on='id_despacho', how='inner')""", language="python")

            st.success("DESPACHOS_Global = DESPACHOS_OPERATIVOS \u22c8 DESPACHOS_FINANZAS")