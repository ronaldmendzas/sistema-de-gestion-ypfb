import streamlit as st
from config import SEDES


def render():
    st.markdown("""
    <div style="text-align:center;padding:24px 0 8px 0;">
        <h1 style="color:#003366;font-weight:800;font-size:2rem;margin:0;letter-spacing:1px;">YPFB Bolivia</h1>
        <p style="color:#71717a;font-size:1rem;margin:6px 0 0 0;">Sistema Distribuido de Hidrocarburos</p>
        <p style="color:#a1a1aa;font-size:0.85rem;margin:4px 0 0 0;">Heterogeneidad Controlada · Protocolo 2PC · Fragmentacion Hibrida</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3, gap="large")
    datos = [("La Paz", col1), ("Cochabamba", col2), ("Santa Cruz", col3)]

    for nombre, col in datos:
        info = SEDES[nombre]
        color = info["color"]
        with col:
            st.markdown(f"""
            <div style="border:2px solid {color};border-radius:12px;padding:24px 16px 16px 16px;text-align:center;background:#fff;transition:box-shadow 0.2s;">
                <h3 style="color:{color};margin:0 0 4px 0;font-size:1.05rem;font-weight:700;">{nombre.upper()}</h3>
                <p style="color:#27272a;font-weight:600;font-size:0.88rem;margin:0 0 6px 0;">{info['planta_nombre']}</p>
                <span style="display:inline-block;background:{color}10;color:{color};border:1px solid {color}30;border-radius:16px;padding:3px 12px;font-size:0.72rem;font-weight:600;">{info['badge']}</span>
                <p style="color:#71717a;font-size:0.78rem;margin:10px 0 0 0;">{info['descripcion']}</p>
            </div>
            """, unsafe_allow_html=True)

    for nombre, col in datos:
        with col:
            label = "Ingresar como Gerente Nacional" if nombre == "Santa Cruz" else f"Ingresar como Operador {nombre}"
            if st.button(label, key=f"btn_{nombre}", use_container_width=True):
                st.session_state.sede_activa = nombre
                st.session_state.pagina = "Panel de Control"
                st.rerun()