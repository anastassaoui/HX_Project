import streamlit as st
from ui.geometry import geometry_section
from ui.clearance import clearance_section
from ui.effectiveness import effectiveness_section
from ui.ml import fouling_prediction_section
from ui.summary import summary_section
from utils.session import init_session_state

st.set_page_config(page_title="Suite de Conception d'Échangeur de Chaleur", layout="wide")
st.title("🧪 Suite d'Ingénierie : Échangeur Tubulaire à Calandre")
init_session_state()

with st.sidebar:
    run_all = st.button("🚀 Calculer tout")
    from streamlit_option_menu import option_menu
    selection = option_menu(
        "Navigation",
        ["Géométrie", "Jeu Calandre", "Efficacité", "Prédiction ML", "Résumé"],
        icons=["rulers", "arrows-angle-contract", "graph-up", "robot", "card-list"],
        menu_icon="cast",
        default_index=0,
    )

if selection == "Géométrie":
    geometry_section(run_all)
elif selection == "Jeu Calandre":
    clearance_section(run_all)
elif selection == "Efficacité":
    effectiveness_section(run_all)
elif selection == "Prédiction ML":
    fouling_prediction_section()
elif selection == "Résumé":
    summary_section(run_all)
