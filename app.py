import streamlit as st
from pages.bienvenida import render as render_bienvenida
from pages.modelo_datos import render as render_modelo
from pages.panel_control import render as render_panel

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --azul: #003366;
    --verde: #166534;
    --rojo: #991b1b;
    --gris-oscuro: #18181b;
    --gris-medio: #52525b;
    --gris-claro: #a1a1aa;
    --fondo: #f8f9fa;
}

.stApp { background: var(--fondo); font-family: 'Inter', sans-serif !important; }

[data-testid="stSidebar"] { background: #09090b !important; border-right: 1px solid #27272a !important; }
[data-testid="stSidebar"] * { color: #e4e4e7 !important; }
[data-testid="stSidebar"] .stRadio [role="radiobutton"] label { color: #a1a1aa !important; font-weight: 500; padding: 8px 14px; border-radius: 8px; }
[data-testid="stSidebar"] .stRadio [role="radiobutton"] label:hover { color: #fff !important; background: rgba(255,255,255,0.06); }
[data-testid="stSidebar"] .stRadio [role="radiobutton"][aria-checked="true"] label { color: #fff !important; background: var(--azul); border-radius: 8px; }
[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] hr { border-color: #27272a !important; }
[data-testid="stSidebar"] .stCaption { color: #71717a !important; }

h1,h2,h3,h4,h5,h6 { color: var(--gris-oscuro) !important; font-family: 'Inter', sans-serif !important; }
p, .stMarkdown { color: var(--gris-oscuro); }
.stCaption, .stMarkdown caption { color: var(--gris-medio) !important; }

.stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
.stButton > button[kind="primary"] { background: var(--azul) !important; color: #fff !important; }
.stButton > button[kind="primary"]:hover { background: #0a4d8c !important; }

.stTabs [aria-selected="true"][data-baseweb="tab"] { color: var(--azul) !important; border-bottom: 2px solid var(--azul) !important; }

[data-testid="stMetricValue"] { color: var(--azul) !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: var(--gris-medio) !important; font-weight: 600 !important; }

.stDataFrame { border-radius: 8px !important; overflow: hidden !important; }
.stExpander { border: 1px solid #e4e4e7 !important; border-radius: 8px !important; }
</style>
"""

st.set_page_config(page_title="YPFB Sistema Distribuido", page_icon="YPFB", layout="wide", initial_sidebar_state="expanded")
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
    <div style="text-align:center;padding:20px 0 12px 0;">
        <div style="font-size:1.4rem;font-weight:800;color:#fff;letter-spacing:3px;">YPFB</div>
        <div style="font-size:0.65rem;color:#71717a;text-transform:uppercase;letter-spacing:1.5px;margin-top:2px;">Sistema Distribuido de Hidrocarburos</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.sede_activa:
        sedes_cfg = {"La Paz": "#4a90d9", "Cochabamba": "#34d399", "Santa Cruz": "#f87171"}
        c = sedes_cfg.get(st.session_state.sede_activa, "#71717a")
        st.markdown(f"""<div style="background:#18181b;border:2px solid {c};border-radius:8px;padding:10px;text-align:center;">
        <span style="color:{c};font-weight:700;font-size:0.95rem;">{st.session_state.sede_activa}</span></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#18181b;border:1px dashed #3f3f46;border-radius:8px;padding:10px;text-align:center;color:#52525b;font-size:0.8rem;">Sin sede seleccionada</div>', unsafe_allow_html=True)

    opciones = ["Inicio", "Modelo de Datos", "Panel de Control"]
    idx = opciones.index(st.session_state.pagina) if st.session_state.pagina in opciones else 0
    pagina = st.radio("Navegacion", opciones, index=idx)
    st.session_state.pagina = pagina
    st.markdown("---")
    st.caption("v1.0 · INF-262 · UMSA 2026")

if pagina == "Inicio":
    render_bienvenida()
elif pagina == "Modelo de Datos":
    render_modelo()
elif pagina == "Panel de Control":
    render_panel()