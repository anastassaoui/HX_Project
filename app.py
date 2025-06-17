import streamlit as st
from ui.geometry import geometry_section
from ui.clearance import clearance_section
from ui.effectiveness import effectiveness_section
from ui.ml import fouling_prediction_section
from ui.summary import summary_section
from utils.session import init_session_state
import base64

st.set_page_config(page_title="Suite de Conception d'Échangeur de Chaleur", layout="wide")

# --- CUSTOM GRADIENT BACKGROUND ---
gradient_css = '''
<style>
body, .stApp {
    background: linear-gradient(135deg, #f0f2f6 0%, #e0e7ff 50%, #ffe0e7 100%) !important;
}
</style>
'''
st.markdown(gradient_css, unsafe_allow_html=True)

# --- HEADER ---
st.title(" Suite d'Ingénierie : Échangeur Tubulaire à Calandre")

init_session_state()

with st.sidebar:
    # Logo at the top of the sidebar
    try:
        st.image("logo.png", width=200)
    except Exception:
        st.markdown("<div style='height:80px;display:flex;align-items:center;justify-content:center;background:#eee;border-radius:8px;'>LOGO</div>", unsafe_allow_html=True)
    from streamlit_option_menu import option_menu
    selection = option_menu(
        "Navigation",
        ["Accueil", "Géométrie", "Jeu Calandre", "Efficacité", "Prédiction ML", "Résumé"],
        icons=["house", "rulers", "arrows-angle-contract", "graph-up", "robot", "card-list"],
        menu_icon="cast",
        default_index=0,
    )
    # Button under the navigation options
    run_all = st.button("🚀 Calculer tout")

if selection == "Accueil":
    st.markdown("""
    <style>
    .hero {
        background: linear-gradient(90deg, #e0e7ff 0%, #ffe0e7 100%);
        border-radius: 1.5rem;
        padding: 2.5rem 2rem 2rem 2rem;
        margin: 2rem auto 2rem auto;
        max-width: 1100px;
        box-shadow: 0 4px 24px 0 rgba(80,80,120,0.08);
        text-align: center;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .hero-sub {
        font-size: 1.2rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    .features-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #fff;
        border-radius: 1rem;
        box-shadow: 0 2px 8px 0 rgba(80,80,120,0.07);
        padding: 1.5rem 1.2rem;
        min-width: 220px;
        max-width: 260px;
        flex: 1 1 220px;
        text-align: center;
        transition: box-shadow 0.2s;
    }
    .feature-card:hover {
        box-shadow: 0 6px 24px 0 rgba(80,80,120,0.13);
    }
    .feature-icon {
        width: 48px;
        height: 48px;
        margin-bottom: 0.7rem;
    }
    .feature-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 0.3rem;
    }
    .feature-desc {
        font-size: 0.98rem;
        color: #64748b;
    }
    @media (max-width: 1200px) {
        .hero { max-width: 98vw; }
    }
    @media (max-width: 800px) {
        .features-row { flex-direction: column; align-items: center; }
        .hero { padding: 1.5rem 0.5rem; }
    }
    </style>
    <div class="hero">
        <img src='https://cdn-icons-png.flaticon.com/512/2917/2917995.png' width='80' style='margin-bottom:1em;' />
        <div class="hero-title">Bienvenue dans la Suite de Conception d'Échangeur de Chaleur</div>
        <div class="hero-sub">Concevez, analysez et optimisez vos échangeurs tubulaires à calandre avec des outils modernes, du machine learning, et des rapports professionnels.</div>
        <div class="features-row">
            <div class="feature-card">
                <svg class="feature-icon" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l4 2"/></svg>
                <div class="feature-title">Calculs de Géométrie</div>
                <div class="feature-desc">Dimensionnez vos échangeurs avec précision grâce à des modules avancés.</div>
            </div>
            <div class="feature-card">
                <svg class="feature-icon" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h8"/></svg>
                <div class="feature-title">Efficacité Thermique</div>
                <div class="feature-desc">Analysez les performances thermiques et optimisez l'efficacité énergétique.</div>
            </div>
            <div class="feature-card">
                <svg class="feature-icon" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path stroke-linecap="round" stroke-linejoin="round" d="M8 9h8M8 15h8"/></svg>
                <div class="feature-title">Prédiction ML</div>
                <div class="feature-desc">Prédisez l'encrassement et le temps de nettoyage avec l'IA intégrée.</div>
            </div>
            <div class="feature-card">
                <svg class="feature-icon" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                <div class="feature-title">Rapports PDF</div>
                <div class="feature-desc">Générez des rapports professionnels et partagez vos résultats facilement.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
elif selection == "Géométrie":
    geometry_section(run_all)
elif selection == "Jeu Calandre":
    clearance_section(run_all)
elif selection == "Efficacité":
    effectiveness_section(run_all)
elif selection == "Prédiction ML":
    fouling_prediction_section()
elif selection == "Résumé":
    summary_section(run_all)

# --- FOOTER ---
footer = '''
<style>
.footer {position: fixed; left: 0; bottom: 0; width: 100%; background: #f0f2f6; color: #888; text-align: center; padding: 8px 0; font-size: 0.9em; z-index: 100; border-top: 1px solid #e0e0e0;}
</style>
<div class="footer">Version 1.0.0 | © 2025 HX_Project | Made with Streamlit</div>
'''
st.markdown(footer, unsafe_allow_html=True)
