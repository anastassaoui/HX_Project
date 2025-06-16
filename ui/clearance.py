import streamlit as st
from utils.helpers import show_metric
from ht.hx import shell_clearance

def clearance_section(run_all: bool) -> None:
    st.subheader("📏 Jeu Calandre-Faisceau")
    input_col, out_col = st.columns(2)
    with input_col:
        with st.form("clearance_form"):
            mode = st.radio("Basé sur", ["Diamètre faisceau", "Diamètre calandre"], horizontal=True)
            db = ds = None
            if mode == "Diamètre faisceau":
                db_default = st.session_state.DB_Perry or 1.2
                db = st.slider("Diamètre du faisceau [m]", 0.1, 3.0, db_default)
            else:
                ds = st.slider("Diamètre de la calandre [m]", 0.1, 3.0, 1.25)
            submit = st.form_submit_button("Calculer jeu")
        run = submit or run_all
        if run:
            result = shell_clearance(DBundle=db) if db else shell_clearance(DShell=ds)
            st.session_state.clearance_result = result
    with out_col:
        if st.session_state.clearance_result:
            show_metric("Jeu recommandé", st.session_state.clearance_result, "m") 