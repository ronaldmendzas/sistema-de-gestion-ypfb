import streamlit as st
import pandas as pd

def render():
    st.markdown("## Monitor del Modelo de Datos")
    st.caption("Arquitectura del sistema distribuido YPFB — Fragmentacion geografica heterogenea")

    tab_er, tab_frag = st.tabs(["Modelo Base (ER)", "Esquema de Fragmentacion"])

    with tab_er:
        st.markdown("### Entidades del Modelo Centralizado")
        st.caption("Antes de la fragmentacion, todas las tablas residian en un unico servidor.")

        entidades = [
            ("PLANTAS", ["id_plantas (PK)", "nombre_planta", "departamento"], "#003366"),
            ("CARBURANTES", ["id_carburante (PK)", "nombre", "precio_surtidor_anh"], "#003366"),
            ("SURTIDORES", ["id_surtidor (PK)", "nombre_surtidor", "departamento"], "#003366"),
            ("STOCK_PLANTAS", ["id_stock (PK)", "id_plantas (FK)", "id_carburante (FK)", "stock_disponible_litros"], "#8b5e00"),
            ("PEDIDOS_WEB", ["id_pedido (PK)", "id_surtidor (FK)", "id_carburante (FK)", "cantidad_litros_solicitados", "fecha_solicitud", "estado"], "#8b5e00"),
            ("DESPACHOS", ["id_despacho (PK)", "id_pedido (FK)", "id_plantas (FK)", "litros_despachados", "fecha_despacho", "placa_cisterna", "costo_importacion_real", "subvencion_asumida_bs"], "#166534"),
        ]

        c1, c2, c3 = st.columns(3)
        for i, (nombre, columnas, color) in enumerate(entidades):
            col = [c1, c2, c3][i % 3]
            with col:
                attrs = "<br>".join([f"<code style='font-size:0.75rem;color:#27272a;'>{c}</code>" for c in columnas])
                st.markdown(f"""
                <div style="border-left:4px solid {color};border-radius:6px;padding:10px 14px;background:white;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                    <div style="font-weight:700;color:{color};font-size:0.85rem;margin-bottom:4px;">{nombre}</div>
                    <div style="line-height:1.6;">{attrs}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Relaciones")
        rel_data = pd.DataFrame({
            "Entidad Padre": ["PLANTAS", "CARBURANTES", "CARBURANTES", "SURTIDORES", "PEDIDOS_WEB", "PLANTAS"],
            "Cardinalidad": ["1:N", "1:N", "1:N", "1:N", "1:1", "1:N"],
            "Entidad Hijo": ["STOCK_PLANTAS", "STOCK_PLANTAS", "PEDIDOS_WEB", "PEDIDOS_WEB", "DESPACHOS", "DESPACHOS"]
        })
        st.dataframe(rel_data, hide_index=True, use_container_width=True)

        st.info("Nota: La tabla DESPACHOS contiene columnas operativas y financieras. Esta dualidad es la base de la fragmentacion hibrida.")

    with tab_frag:
        st.markdown("### Esquema de Fragmentacion Distribuida")
        st.caption("Las tablas se dividen entre 3 nodos geograficos con diferentes motores de BD.")

        tab_s, tab_p, tab_d, tab_r = st.tabs(["STOCK_PLANTAS (Horizontal)", "PEDIDOS_WEB (Horizontal)", "DESPACHOS (Hibrida)", "Reconstruccion Global"])

        with tab_s:
            st.markdown("#### Fragmentacion Horizontal Primaria — STOCK_PLANTAS")
            st.caption("Cada nodo almacena solo los registros de su planta. Reconstruccion: UNION.")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**PC1 — La Paz**")
                st.caption("PostgreSQL 17 · id_plantas = 10")
                st.dataframe(pd.DataFrame({"id_stock": [1001, 1002, 1003], "id_plantas": [10, 10, 10], "id_carburante": [1, 2, 3], "stock_litros": [500000, 750000, 120000]}), hide_index=True)
            with c2:
                st.markdown("**PC2 — Cochabamba**")
                st.caption("MySQL 8 · id_plantas = 20")
                st.dataframe(pd.DataFrame({"id_stock": [2001, 2002], "id_plantas": [20, 20], "id_carburante": [1, 2], "stock_litros": [420000, 600000]}), hide_index=True)
            with c3:
                st.markdown("**PC3 — Santa Cruz**")
                st.caption("PostgreSQL 15+ · id_plantas = 30")
                st.dataframe(pd.DataFrame({"id_stock": [3001, 3002], "id_plantas": [30, 30], "id_carburante": [1, 2], "stock_litros": [900000, 1200000]}), hide_index=True)

            st.code("STOCK_PLANTAS_Global = PC1 ∪ PC2 ∪ PC3", language=None)

        with tab_p:
            st.markdown("#### Fragmentacion Horizontal Primaria — PEDIDOS_WEB")
            st.caption("Cada nodo almacena los pedidos de sus surtidores locales.")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**PC1 — La Paz**")
                st.caption("Surtidores 101, 102")
                st.dataframe(pd.DataFrame({"id_pedido": [10001, 10002], "id_surtidor": [101, 102], "id_carburante": [1, 2], "litros": [15000, 20000], "estado": ["Despachado", "Despachado"]}), hide_index=True)
            with c2:
                st.markdown("**PC2 — Cochabamba**")
                st.caption("Surtidores 201, 202")
                st.dataframe(pd.DataFrame({"id_pedido": [20001, 20002], "id_surtidor": [201, 202], "id_carburante": [1, 2], "litros": [12000, 18000], "estado": ["Despachado", "Despachado"]}), hide_index=True)
            with c3:
                st.markdown("**PC3 — Santa Cruz**")
                st.caption("Surtidor 301")
                st.dataframe(pd.DataFrame({"id_pedido": [30001], "id_surtidor": [301], "id_carburante": [1], "litros": [25000], "estado": ["Despachado"]}), hide_index=True)

            st.code("PEDIDOS_WEB_Global = PC1 ∪ PC2 ∪ PC3", language=None)

        with tab_d:
            st.markdown("#### Fragmentacion Hibrida — DESPACHOS")
            st.caption("Corte vertical (columnas confidenciales) + Corte horizontal (distribucion por planta).")

            st.markdown("**Paso A: Corte Vertical**")
            c_op, c_fin = st.columns(2)
            with c_op:
                st.markdown("**DESPACHOS_OPERATIVOS**")
                st.caption("Distribuido a los 3 nodos")
                st.code("id_despacho, id_pedido, id_plantas,\nlitros_despachados, fecha_despacho,\nplaca_cisterna", language="sql")
            with c_fin:
                st.markdown("**DESPACHOS_FINANZAS**")
                st.caption("Solo en Santa Cruz (PC3)")
                st.code("id_despacho,\ncosto_importacion_real,\nsubvencion_asumida_bs", language="sql")

            st.markdown("---")
            st.markdown("**Paso B: Corte Horizontal** — Distribucion por id_plantas")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**PC1 — La Paz**")
                st.code("id_plantas = 10\nIDs: 15XXX\nPostgreSQL 17", language=None)
                st.dataframe(pd.DataFrame({"id_despacho": [15001, 15002], "id_pedido": [10001, 10002], "id_plantas": [10, 10], "litros": [15000, 20000], "placa": ["2345-PKD", "4712-LXZ"]}), hide_index=True)
            with c2:
                st.markdown("**PC2 — Cochabamba**")
                st.code("id_plantas = 20\nIDs: 25XXX\nMySQL 8", language=None)
                st.dataframe(pd.DataFrame({"id_despacho": [25001, 25002], "id_pedido": [20001, 20002], "id_plantas": [20, 20], "litros": [12000, 18000], "placa": ["3988-BFF", "1544-KLA"]}), hide_index=True)
            with c3:
                st.markdown("**PC3 — Santa Cruz**")
                st.code("id_plantas = 30\nIDs: 35XXX\nPostgreSQL 15+", language=None)
                st.dataframe(pd.DataFrame({"id_despacho": [35001], "id_pedido": [30001], "id_plantas": [30], "litros": [25000], "placa": ["9822-XPT"]}), hide_index=True)
                st.markdown("**+ DESPACHOS_FINANZAS (completa)**")
                st.dataframe(pd.DataFrame({"id_despacho": [15001, 15002, 25001, 25002, 35001], "costo_real_Bs": [127500, 170000, 102000, 153000, 212500], "subvencion_Bs": [71400, 95200, 57120, 86040, 119000]}), hide_index=True)

        with tab_r:
            st.markdown("#### Pipeline de Reconstruccion Global Hibrida")
            st.caption("Python + Pandas reconstruye la tabla DESPACHOS completa desde los 3 nodos heterogeneos.")

            st.markdown("**FASE 1: Extraccion** — Cada nodo ejecuta su consulta SQL local.")
            st.code("""df_LP   = pd.read_sql('SELECT * FROM despachos_lp', conn_LP)
df_CBBA = pd.read_sql('SELECT * FROM despachos_cbba', conn_CBBA)
df_SC   = pd.read_sql('SELECT * FROM despachos_sc', conn_SC)""", language="python")

            st.markdown("**FASE 2: Union Horizontal (∪)** — Emula UNION ALL del algebra relacional.")
            st.code("df_operativos = pd.concat([df_LP, df_CBBA, df_SC], ignore_index=True)", language="python")

            st.markdown("**FASE 3: Junta Vertical (⋈)** — JOIN con la tabla financiera exclusiva de Santa Cruz.")
            st.code("""df_finanzas = pd.read_sql('SELECT * FROM despachos_finanzas', conn_SC)
df_final = pd.merge(df_operativos, df_finanzas, on='id_despacho', how='inner')""", language="python")

            st.markdown("---")
            st.success("DESPACHOS_Global = DESPACHOS_OPERATIVOS_Global ⋈ DESPACHOS_FINANZAS")