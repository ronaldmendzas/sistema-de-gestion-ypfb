import streamlit as st
from config import SEDES

COLORS = {"La Paz": "#003366", "Cochabamba": "#166534", "Santa Cruz": "#991b1b"}
LIGHT_BG = {"La Paz": "#dbeafe", "Cochabamba": "#dcfce7", "Santa Cruz": "#fee2e2"}

def render():
    st.markdown("""
    <div style="text-align:center;padding:28px 0 8px 0;">
        <div style="font-size:2rem;font-weight:900;color:#003366;letter-spacing:2px;">YPFB Bolivia</div>
        <div style="font-size:1rem;color:#27272a;margin-top:4px;">Sistema Distribuido de Hidrocarburos</div>
        <div style="font-size:0.8rem;color:#71717a;margin-top:2px;">Heterogeneidad Controlada · Protocolo 2PC · Fragmentacion Hibrida</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3, gap="large")
    datos = [("La Paz", col1), ("Cochabamba", col2), ("Santa Cruz", col3)]

    for nombre, col in datos:
        info = SEDES[nombre]
        bg = LIGHT_BG[nombre]
        border = COLORS[nombre]
        with col:
            st.markdown(f"""
            <div style="border:2px solid {border};border-radius:12px;padding:24px 16px 16px;text-align:center;background:{bg};">
                <div style="font-size:1.05rem;font-weight:800;color:{border};margin-bottom:4px;">{nombre.upper()}</div>
                <div style="font-size:0.88rem;font-weight:600;color:#18181b;margin-bottom:8px;">{info['planta_nombre']}</div>
                <div style="display:inline-block;background:#fff;border:1px solid {border}50;border-radius:12px;padding:3px 10px;font-size:0.72rem;font-weight:600;color:{border};">{info['badge']}</div>
                <div style="font-size:0.78rem;color:#52525b;margin-top:10px;">{info['descripcion']}</div>
            </div>
            """, unsafe_allow_html=True)

    for nombre, col in datos:
        with col:
            label = "Ingresar como Gerente Nacional" if nombre == "Santa Cruz" else f"Ingresar como Operador {nombre}"
            if st.button(label, key=f"btn_{nombre}", use_container_width=True, type="primary"):
                st.session_state.sede_activa = nombre
                st.session_state.pagina = "Panel de Control"
                st.rerun()