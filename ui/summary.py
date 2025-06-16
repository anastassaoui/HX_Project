import streamlit as st
import pandas as pd
from utils.pdf_report import generate_pdf_report

def summary_section(run_all: bool) -> None:
    st.subheader("🧾 Résumé Complet")
    if run_all and st.session_state.inputs_geometry and st.session_state.inputs_pntu:
        g = st.session_state.inputs_geometry
        p = st.session_state.inputs_pntu
        data = {
            "Paramètre": [
                "Do [m]", "pitch [m]", "angle [°]", "Ntp", "N", "Matériau", "L_unsupported [m]",
                "DB_Perry [m]", "N_Perry", "DB_HEDH [m]", "DB_Phadkeb [m]", "DB_VDI [m]",
                "DShell_min [m]", "Clearance auto [m]", "dB_hole [m]", "L_max [m]",
                "Débit m1 [kg/s]", "Cp1 [J/kg.K]", "T1 entrée [°C]",
                "Débit m2 [kg/s]", "Cp2 [J/kg.K]", "T2 entrée [°C]",
                "UA [W/K]", "Subtype HX", "Ntp (P-NTU)",
            ],
            "Valeur": [
                g["Do"], g["pitch"], g["angle"], g["Ntp"], g["N"], g["material"], g["L_unsupported"],
                st.session_state.DB_Perry, st.session_state.N_Perry, st.session_state.DB_HEDH,
                st.session_state.DB_Phadkeb, st.session_state.DB_VDI, st.session_state.DShell_min,
                st.session_state.clearance_auto, st.session_state.dB_hole, st.session_state.L_max,
                p["m1"], p["Cp1"], p["T1i"], p["m2"], p["Cp2"], p["T2i"], p["UA"], p["subtype"], p["Ntp"],
            ],
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.markdown("""
        <br/>
        <b>Générez un rapport PDF de ce résumé :</b>
        """, unsafe_allow_html=True)
        pdf_buffer = generate_pdf_report()
        st.download_button(
            label="📄 Télécharger le PDF du Résumé",
            data=pdf_buffer,
            file_name="resume_echangeur.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Cliquez sur 'Calculer tout' pour générer le résumé complet.") 