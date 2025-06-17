import streamlit as st
from utils.helpers import show_metric
from ht.hx import shell_clearance

def clearance_section(run_all: bool) -> None:
    st.subheader("Jeu Calandre-Faisceau")
    # Only input columns at the top
    input_col = st.columns([1])[0]
    with input_col:
        with st.form("clearance_form"):
            mode = st.radio(
                "Basé sur",
                ["Diamètre faisceau", "Diamètre calandre"],
                horizontal=True,
                help="Choisissez si vous souhaitez calculer le jeu à partir du diamètre du faisceau ou de la calandre."
            )
            db = ds = None
            error = None
            if mode == "Diamètre faisceau":
                db_default = st.session_state.DB_Perry or 1.2
                db = st.slider(
                    "Diamètre du faisceau [m]",
                    0.1, 3.0, db_default,
                    help="Diamètre extérieur du faisceau de tubes. Utilisez la valeur calculée ou saisissez manuellement."
                )
                if db <= 0.1 or db >= 3.0:
                    error = "Le diamètre du faisceau doit être compris entre 0.1 m et 3.0 m."
            else:
                ds = st.slider(
                    "Diamètre de la calandre [m]",
                    0.1, 3.0, 1.25,
                    help="Diamètre intérieur de la calandre. Utilisez la valeur recommandée ou saisissez manuellement."
                )
                if ds <= 0.1 or ds >= 3.0:
                    error = "Le diamètre de la calandre doit être compris entre 0.1 m et 3.0 m."
            submit = st.form_submit_button("Calculer jeu")
    run = submit or run_all
    if run:
        if error:
            st.error(error)
        else:
            result = shell_clearance(DBundle=db) if db else shell_clearance(DShell=ds)
            st.session_state.clearance_result = result
    # Results card now below the input form, full width and horizontal
    if st.session_state.get("clearance_result"):
        st.markdown("""
        <style>
        .clearance-card {{
            background: linear-gradient(120deg, #f0f2f6 60%, #e0e7ff 100%);
            border-radius: 16px;
            padding: 1.5em 1em 1em 1em;
            box-shadow: 0 2px 8px rgba(80,80,120,0.07);
            margin-bottom: 1em;
            margin-top: 2em;
            width: 100%;
            overflow-x: auto;
        }}
        .clearance-metric-row {{
            display: flex;
            flex-direction: row;
            gap: 2em;
            flex-wrap: nowrap;
            overflow-x: auto;
        }}
        .clearance-metric {{
            min-width: 180px;
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 0.5em;
        }}
        .clearance-label {{
            color: #4b4b6b;
            font-weight: 700;
        }}
        .clearance-value {{
            color: #ff4b4b;
            font-size: 1.2em;
            font-weight: 700;
        }}
        </style>
        <div class="clearance-card">
        <h4 style="margin-bottom:1em;">🔎 <b>Résultat Jeu Calandre-Faisceau</b></h4>
        <div class="clearance-metric-row">
            <div class="clearance-metric"><span class="clearance-label">Jeu recommandé</span><br><span class="clearance-value">{:.3f} m</span></div>
        </div>
        </div>
        """.format(
            st.session_state.clearance_result
        ), unsafe_allow_html=True) 