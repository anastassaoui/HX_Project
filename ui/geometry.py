import streamlit as st
from utils.helpers import show_metric
from ht.hx import size_bundle_from_tubecount, Ntubes, DBundle_for_Ntubes_HEDH, DBundle_for_Ntubes_Phadkeb, D_for_Ntubes_VDI, DBundle_min, shell_clearance, D_baffle_holes, L_unsupported_max

def geometry_section(run_all: bool) -> None:
    st.subheader("📐 Calculs de Géométrie")
    col_input, col_result = st.columns([2, 1])
    with col_input:
        with st.form("geom_form"):
            r1c1, r1c2, r1c3 = st.columns(3)
            Do = r1c1.number_input("Ø extérieur [m]", 0.005, 0.1, 0.025)
            pitch = r1c2.number_input("Pas triangulaire [m]", 0.01, 0.1, 0.03125)
            angle = r1c3.selectbox("Angle [°]", [30, 45, 60, 90], index=0)

            r2c1, r2c2, r2c3 = st.columns(3)
            Ntp = r2c1.selectbox("Passes tubes", [1, 2], index=1)
            N = r2c2.slider("Nombre de tubes", 1, 2000, 928)
            L_unsupported = r2c3.number_input("Longueur non supportée [m]", 0.1, 10.0, 0.75)

            material = st.selectbox("Matériau du tube", ["CS", "aluminium"])
            submit = st.form_submit_button("Calculer géométrie")

        run = submit or run_all
        if run:
            st.session_state.DB_Perry = size_bundle_from_tubecount(N, Do, pitch, Ntp, angle)
            st.session_state.N_Perry = Ntubes(st.session_state.DB_Perry, Do, pitch, Ntp, angle)
            st.session_state.DB_HEDH = DBundle_for_Ntubes_HEDH(N, Do, pitch, angle)
            st.session_state.DB_Phadkeb = DBundle_for_Ntubes_Phadkeb(N, Do, pitch, Ntp, angle)
            st.session_state.DB_VDI = D_for_Ntubes_VDI(N, Ntp, Do, pitch, angle)
            st.session_state.DShell_min = DBundle_min(Do)
            st.session_state.clearance_auto = shell_clearance(DBundle=st.session_state.DB_HEDH)
            st.session_state.dB_hole = D_baffle_holes(Do, L_unsupported)
            st.session_state.L_max = L_unsupported_max(Do, material)
            st.session_state.inputs_geometry = {
                "Do": Do,
                "pitch": pitch,
                "angle": angle,
                "Ntp": Ntp,
                "N": N,
                "material": material,
                "L_unsupported": L_unsupported,
            }
    with col_result:
        if st.session_state.DB_Perry:
            st.markdown("### Résultats")
            show_metric("Faisceau Perry", st.session_state.DB_Perry, "m")
            show_metric("Tubes Perry", st.session_state.N_Perry)
            show_metric("HEDH", st.session_state.DB_HEDH, "m")
            show_metric("Phadkeb", st.session_state.DB_Phadkeb, "m")
            show_metric("VDI", st.session_state.DB_VDI, "m")
            show_metric("DShell_min", st.session_state.DShell_min, "m")
            show_metric("Clearance auto", st.session_state.clearance_auto, "m")
            show_metric("Ø trou chicane", st.session_state.dB_hole, "m")
            show_metric("L_max sans support", st.session_state.L_max, "m") 