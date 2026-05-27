import streamlit as st
from config import SEDES

COLORS = {"La Paz": "#003366", "Cochabamba": "#166534", "Santa Cruz": "#991b1b"}

def render():
    st.markdown("""
    <div style="text-align:center;padding:32px 0 12px 0;">
        <div style="font-size:2.2rem;font-weight:900;color:#003366;letter-spacing:2px;">YPFB Bolivia</div>
        <div style="font-size:1rem;color:#52525b;margin-top:6px;">Sistema Distribuido de Hidrocarburos</div>
        <div style="font-size:0.8rem;color:#71717a;margin-top:4px;">Heterogeneidad Controlada · Protocolo 2PC · Fragmentacion Hibrida</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3, gap="large")
    datos = [("La Paz", col1), ("Cochabamba", col2), ("Santa Cruz", col3)]

    for nombre, col in datos:
        info = SEDES[nombre]
        color = COLORS[nombre]
        with col:
            st.markdown(f"""
            <div style="border:2px solid {color};border-radius:12px;padding:28px 20px;text-align:center;background:#fff;">
                <div style="font-size:1.1rem;font-weight:800;color:{color};margin-bottom:4px;">{nombre.upper()}</div>
                <div style="font-size:0.9rem;font-weight:600;color:#18181b;margin-bottom:8px;">{info['planta_nombre']}</div>
                <div style="display:inline-block;background:{color}12;color:{color};border:1px solid {color}30;border-radius:12px;padding:3px 10px;font-size:0.7rem;font-weight:600;">{info['badge']}</div>
                <div style="font-size:0.78rem;color:#52525b;margin-top:10px;">{info['descripcion']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    for nombre, col in datos:
        with col:
            label = "Ingresar como Gerente Nacional" if nombre == "Santa Cruz" else f"Ingresar como Operador {nombre}"
            if st.button(label, key=f"btn_{nombre}", use_container_width=True, type="primary"):
                st.session_state.sede_activa = nombre
                st.session_state.pagina = "Panel de Control"
                st.rerun()