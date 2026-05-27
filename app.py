import streamlit as st
from pages.bienvenida import render as render_bienvenida
from pages.modelo_datos import render as render_modelo
from pages.panel_control import render as render_panel

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --azul: #003366;
    --azul-light: #0a4d8c;
    --rojo: #CC0000;
    --fondo: #F0F2F5;
    --verde: #198754;
    --amarillo: #FFC107;
    --gris-borde: #dee2e6;
}

.stApp { font-family: 'Inter', sans-serif !important; background: var(--fondo); }

[data-testid="stSidebar"] {
    background: #0a0a0b !important;
    border-right: 1px solid #1a1a1e !important;
}
[data-testid="stSidebar"] * { color: #e4e4e7 !important; }
[data-testid="stSidebar"] .stRadio [role="radiobutton"] label {
    color: #a1a1aa !important; font-weight: 500; font-size: 0.9rem; padding: 8px 14px; border-radius: 8px;
}
[data-testid="stSidebar"] .stRadio [role="radiobutton"] label:hover {
    color: #fff !important; background: rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] .stRadio [role="radiobutton"][aria-checked="true"] label {
    color: #fff !important; background: var(--azul); border-radius: 8px;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] hr { border-color: #27272a !important; }

h1,h2,h3,h4,h5,h6 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.01em; color: #18181b; }

.stButton > button {
    border-radius: 8px !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important;
    transition: all 0.15s ease !important; border: none !important;
}
.stButton > button:hover { opacity: 0.9; }
.stButton > button[kind="primary"] {
    background: var(--azul) !important; color: #fff !important;
}

.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important; padding: 8px 16px !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"][data-baseweb="tab"] {
    color: var(--azul) !important; border-bottom: 2px solid var(--azul) !important;
}

.stDataFrame { border-radius: 8px !important; overflow: hidden !important; }

[data-testid="stMetricValue"] { font-weight: 800 !important; font-size: 1.6rem !important; color: var(--azul); }
[data-testid="stMetricLabel"] { font-weight: 600 !important; color: #71717a !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.5px; }

.stExpander { border: 1px solid #e4e4e7 !important; border-radius: 8px !important; }
</style>
"""

st.set_page_config(page_title="YPFB Sistema Distribuido", page_icon="\U0001f6e2", layout="wide", initial_sidebar_state="expanded")
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
    st.markdown('<div style="text-align:center;padding:16px 0 8px 0;"><span style="color:#fff;font-size:1.3rem;font-weight:800;letter-spacing:2px;">YPFB</span><br><span style="color:#71717a;font-size:0.65rem;text-transform:uppercase;letter-spacing:1px;">Sistema Distribuido</span></div>', unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.sede_activa:
        sedes_cfg = {
            "La Paz": {"color": "#003366"},
            "Cochabamba": {"color": "#198754"},
            "Santa Cruz": {"color": "#CC0000"},
        }
        cfg = sedes_cfg.get(st.session_state.sede_activa, {"color": "#FFC107"})
        st.markdown(f'<div style="background:#18181b;border:1px solid {cfg["color"]};border-radius:8px;padding:10px;text-align:center;margin-bottom:8px;"><strong style="color:{cfg["color"]};">{st.session_state.sede_activa}</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#18181b;border:1px dashed #3f3f46;border-radius:8px;padding:10px;text-align:center;margin-bottom:8px;color:#71717a;font-size:0.8rem;">Sin sede</div>', unsafe_allow_html=True)

    opciones = ["Inicio", "Modelo de Datos", "Panel de Control"]
    indice_actual = opciones.index(st.session_state.pagina) if st.session_state.pagina in opciones else 0
    pagina = st.radio("Navegacion", opciones, index=indice_actual)
    st.session_state.pagina = pagina
    st.markdown("---")
    st.caption("v1.0 · INF-262 · UMSA 2026")

if pagina == "Inicio":
    render_bienvenida()
elif pagina == "Modelo de Datos":
    render_modelo()
elif pagina == "Panel de Control":
    render_panel()