import streamlit as st
from pages.bienvenida import render as render_bienvenida
from pages.modelo_datos import render as render_modelo
from pages.panel_control import render as render_panel

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --azul: #003366;
    --rojo: #CC0000;
    --fondo: #F8F9FA;
    --texto: #1a1a1a;
    --verde: #198754;
    --amarillo: #FFC107;
    --gris-borde: #dee2e6;
}

.stApp {
    background-color: var(--fondo);
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #003366 0%, #001a33 100%) !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stRadio [role="radiobutton"] label {
    color: #FFFFFF !important;
    font-weight: 500;
}

[data-testid="stSidebar"] .stRadio [role="radiobutton"] label:hover {
    color: #FFC107 !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    display: none;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif;
}

.stButton>button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

[data-testid="stMetricValue"] {
    font-weight: 700;
}

.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 10px 20px;
    font-weight: 600;
}

div.stSuccess > div {
    background-color: #d4edda;
    border-left: 4px solid var(--verde);
}

div.stError > div {
    background-color: #f8d7da;
    border-left: 4px solid var(--rojo);
}

div.stWarning > div {
    background-color: #fff3cd;
    border-left: 4px solid var(--amarillo);
}

div.stInfo > div {
    background-color: #d1ecf1;
    border-left: 4px solid var(--azul);
}

.element-container:has(.stMetric) {
    background: white;
    border-radius: 12px;
    padding: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
</style>
"""

st.set_page_config(
    page_title="YPFB Sistema Distribuido",
    page_icon="\U0001f6e2",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)

if "sede_activa" not in st.session_state:
    st.session_state.sede_activa = None
if "log_2pc" not in st.session_state:
    st.session_state.log_2pc = []
if "df_reconstruido" not in st.session_state:
    st.session_state.df_reconstruido = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:15px 0;">
        <h2 style="color:#FFFFFF; margin:0; font-size:1.6rem; letter-spacing:1px;">\U0001f6e2 YPFB Bolivia</h2>
        <p style="color:#FFFFFFAA; margin:5px 0 0 0; font-size:0.75rem;">
            Sistema Distribuido de Hidrocarburos
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.sede_activa:
        info_sede = {
            "La Paz": {"icono": "\U0001f3d4\ufe0f", "color": "#003366"},
            "Cochabamba": {"icono": "\U0001f33f", "color": "#198754"},
            "Santa Cruz": {"icono": "\U0001f3db\ufe0f", "color": "#CC0000"},
        }.get(st.session_state.sede_activa, {"icono": "\u26a0\ufe0f", "color": "#FFC107"})

        st.markdown(f"""
        <div style="
            background: {info_sede['color']}30;
            border: 2px solid {info_sede['color']};
            border-radius: 10px;
            padding: 10px 14px;
            text-align: center;
            margin-bottom: 10px;
        ">
            <span style="font-size:1.3rem;">{info_sede['icono']}</span><br>
            <strong style="color:{info_sede['color']};">{st.session_state.sede_activa}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: #FFFFFF15;
            border: 2px dashed #FFFFFF50;
            border-radius: 10px;
            padding: 10px 14px;
            text-align: center;
            margin-bottom: 10px;
        ">
            <span style="color:#FFFFFFAA; font-size:0.85rem;">Sin sede seleccionada</span>
        </div>
        """, unsafe_allow_html=True)

    opciones = ["Inicio", "Modelo de Datos", "Panel de Control"]
    indice_actual = opciones.index(st.session_state.pagina) if st.session_state.pagina in opciones else 0
    pagina = st.radio("Navegacion", opciones, index=indice_actual)
    st.session_state.pagina = pagina

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:10px 0;">
        <p style="color:#FFFFFF80; font-size:0.7rem; margin:0;">
            v1.0 \u00b7 INF-262 UMSA 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

if pagina == "Inicio":
    render_bienvenida()
elif pagina == "Modelo de Datos":
    render_modelo()
elif pagina == "Panel de Control":
    render_panel()