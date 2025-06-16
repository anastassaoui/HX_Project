def init_session_state() -> None:
    import streamlit as st
    keys = [
        "DB_Perry", "N_Perry", "DB_HEDH", "DB_Phadkeb", "DB_VDI",
        "DShell_min", "clearance_auto", "dB_hole", "L_max",
        "inputs_geometry", "inputs_pntu", "clearance_result",
        "fouling_prediction", "ttc_prediction"
    ]
    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = None 