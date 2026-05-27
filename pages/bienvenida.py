import streamlit as st
from config import SEDES


def render():
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <h1 style="color:#003366; margin:0; font-weight:800; letter-spacing:2px;">
            <span style="color:#CC0000;">\U0001f3db\ufe0f</span> YPFB Bolivia
        </h1>
        <h2 style="color:#1a1a1a; margin:5px 0 0 0; font-weight:400; font-size:1.4rem;">
            Sistema Distribuido de Hidrocarburos
        </h2>
        <p style="color:#6c757d; margin:8px 0 0 0; font-size:0.95rem;">
            Selecciona tu sede operativa para ingresar al sistema
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    sedes_lista = list(SEDES.keys())
    datos = [
        ("La Paz", col1),
        ("Cochabamba", col2),
        ("Santa Cruz", col3),
    ]

    for nombre, col in datos:
        info = SEDES[nombre]
        with col:
            border_color = info["color"]
            st.markdown(f"""
            <div style="
                border: 3px solid {border_color};
                border-radius: 16px;
                padding: 28px 18px 18px 18px;
                text-align: center;
                background: #FFFFFF;
                margin-bottom: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                transition: transform 0.2s, box-shadow 0.2s;
            ">
                <div style="font-size:3.5rem; margin-bottom:6px;">{info['icono']}</div>
                <h3 style="color:{border_color}; margin:0 0 6px 0; font-size:1.1rem; font-weight:700;">
                    {nombre.upper()}
                </h3>
                <p style="color:#003366; font-weight:600; font-size:0.95rem; margin:0 0 4px 0;">
                    {info['planta_nombre']}
                </p>
                <span style="
                    display:inline-block;
                    background: {border_color}15;
                    color: {border_color};
                    border: 1px solid {border_color}40;
                    border-radius: 20px;
                    padding: 4px 14px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    margin: 6px 0;
                ">{info['badge']}</span>
                <p style="color:#6c757d; font-size:0.8rem; margin:8px 0 0 0;">
                    {info['descripcion']}
                </p>
            </div>
            """, unsafe_allow_html=True)

    for nombre, col in datos:
        info = SEDES[nombre]
        with col:
            btn_label = f"\U0001f69b Ingresar como Operador {nombre}" if nombre != "Santa Cruz" else "\U0001f3db\ufe0f Ingresar como Gerente Nacional"
            if st.button(btn_label, key=f"btn_{nombre}", use_container_width=True):
                st.session_state.sede_activa = nombre
                st.session_state.pagina = "Panel de Control"
                st.rerun()