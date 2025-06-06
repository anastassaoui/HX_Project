import streamlit as st
import pandas as pd
from streamlit_navigation_bar import st_navbar
from ht.hx import (
    Ntubes,
    size_bundle_from_tubecount,
    shell_clearance,
    temperature_effectiveness_basic,
    temperature_effectiveness_TEMA_E,
    temperature_effectiveness_TEMA_G,
    temperature_effectiveness_TEMA_H,
    temperature_effectiveness_TEMA_J,
    temperature_effectiveness_air_cooler,
    temperature_effectiveness_plate,
    P_NTU_method,
    DBundle_for_Ntubes_HEDH,
    DBundle_for_Ntubes_Phadkeb,
    D_for_Ntubes_VDI,
    DBundle_min,
    D_baffle_holes,
    L_unsupported_max
)

st.set_page_config(page_title="Suite de Conception d'Échangeur de Chaleur", layout="wide")
page = st_navbar(["Home", "ML"], selected="Home")
if page == "ML":
    st.switch_page("pages/ml.py")

st.title("🧪 Suite d'Ingénierie : Échangeur Tubulaire à Calandre")
st.markdown("---")

compute_all = st.button("🚀 Calculer tous les résultats")

# Initialize session state
session_keys = [
    "DB_Perry", "N_Perry", "DB_HEDH", "DB_Phadkeb", "DB_VDI",
    "DShell_min", "clearance_auto", "dB_hole", "L_max"
]
for k in session_keys:
    if k not in st.session_state:
        st.session_state[k] = None

# Layout
c1, c2, c3 = st.columns([3, 2, 3])

# ------------------------ c1: GÉOMÉTRIE ------------------------
with c1:
    with st.expander("📐 Calculs de Géométrie"):
        col1, col2 = st.columns(2)
        with col1:
            Do = st.number_input("Diamètre extérieur du tube [m]", 0.005, 0.1, 0.025, key="Do")
            pitch = st.number_input("Pas triangulaire [m]", 0.01, 0.1, 0.03125, key="pitch")
        with col2:
            angle = st.selectbox("Angle d'agencement [°]", [30, 45, 60, 90], index=0, key="angle")
            Ntp = st.selectbox("Nombre de passes tubes", [1, 2], index=1, key="Ntp")
        N = st.slider("Nombre de tubes", 1, 2000, 928, key="N")
        L_unsupported = st.number_input("Longueur non supportée [m]", 0.1, 10.0, 0.75, key="L_unsupported")
        material = st.selectbox("Matériau du tube", ["CS", "aluminium"], key="material")

        # Calculs
        if compute_all:
            st.session_state.DB_Perry = size_bundle_from_tubecount(N, Do, pitch, Ntp, angle)
            st.session_state.N_Perry = Ntubes(st.session_state.DB_Perry, Do, pitch, Ntp, angle)
            st.session_state.DB_HEDH = DBundle_for_Ntubes_HEDH(N, Do, pitch, angle)
            st.session_state.DB_Phadkeb = DBundle_for_Ntubes_Phadkeb(N, Do, pitch, Ntp, angle)
            st.session_state.DB_VDI = D_for_Ntubes_VDI(N, Ntp, Do, pitch, angle)
            st.session_state.DShell_min = DBundle_min(Do)
            st.session_state.clearance_auto = shell_clearance(DBundle=st.session_state.DB_HEDH)
            st.session_state.dB_hole = D_baffle_holes(Do, L_unsupported)
            st.session_state.L_max = L_unsupported_max(Do, material)

        if st.session_state.DB_Perry:
            st.markdown("### 🧾 Résultats Géométriques Calculés")

            d1, d2, d3 = st.columns(3)

            # --- Colonne 1 : Perry ---
            with d1:
                st.subheader("📏 Méthode Perry")
                st.success(f"Faisceau Perry : `{st.session_state.DB_Perry:.5f} m`")
                st.info(f"Tubes Perry : `{int(st.session_state.N_Perry)}`")

            # --- Colonne 2 : Autres méthodes de faisceau ---
            with d2:
                st.subheader("📐 Estimations Avancées")
                st.code(f"HEDH    = {st.session_state.DB_HEDH:.5f} m", language="python")
                st.code(f"Phadkeb = {st.session_state.DB_Phadkeb:.5f} m", language="python")
                st.code(f"VDI     = {st.session_state.DB_VDI:.5f} m", language="python")
                st.code(f"DShell_min = {st.session_state.DShell_min:.5f} m", language="python")

            # --- Colonne 3 : Dérivés pratiques ---
            with d3:
                st.subheader("🔧 Dérivés Pratiques")
                st.info(f"Jeu calandre-faisceau (HEDH) : `{st.session_state.clearance_auto:.5f} m`")
                st.info(f"Ø trou chicane (TEMA) : `{st.session_state.dB_hole:.5f} m`")
                st.warning(f"L_max sans support : `{st.session_state.L_max:.2f} m`")





# ------------------------ c2: JEU CALANDRE ------------------------
with c2:
    with st.expander("📏 Jeu Calandre-Faisceau"):
        clearance_mode = st.radio("Basé sur", ["Diamètre faisceau", "Diamètre calandre"], horizontal=True, key="clr_mode")
        db = ds = None
        if clearance_mode == "Diamètre faisceau":
            db = st.slider("Diamètre du faisceau [m]", 0.1, 3.0, st.session_state.DB_Perry or 1.2, key="clr_db")
        else:
            ds = st.slider("Diamètre de la calandre [m]", 0.1, 3.0, 1.25, key="clr_ds")

        if compute_all:
            result = shell_clearance(DBundle=db) if db else shell_clearance(DShell=ds)
            st.session_state.clearance_result = result
        if st.session_state.get("clearance_result"):
            st.success(f"Jeu recommandé : {st.session_state.clearance_result:.5f} m")


# ------------------------ c3: EFFICACITÉ ------------------------
with c3:
    with st.expander("🔥 Méthodes d'Efficacité Thermique"):
        tabs = st.tabs(["Basique", "TEMA E", "TEMA G", "TEMA H", "TEMA J", "Air Cooler", "Plaques", "Solveur P-NTU"])

        def tema_ui(tab, func, key_prefix):
            with tab:
                c1, c2, c3 = st.columns(3)
                with c1:
                    R1 = st.number_input("R1", 0.01, 10.0, 0.5, key=f"{key_prefix}_R1")
                with c2:
                    NTU1 = st.number_input("NTU1", 0.01, 20.0, 1.0, key=f"{key_prefix}_NTU")
                with c3:
                    Ntp_local = st.number_input("Passes tubes", 1, 4, 1, key=f"{key_prefix}_Ntp")
                    optimal = st.checkbox("Contre-courant", True, key=f"{key_prefix}_opt")
                if compute_all:
                    if func.__name__ == "temperature_effectiveness_TEMA_J":
                        eff = func(R1, NTU1, Ntp_local)
                    else:
                        eff = func(R1, NTU1, Ntp_local, optimal)
                    st.success(f"Efficacité : {eff:.5f}")

        # Basique
        with tabs[0]:
            R1 = st.number_input("R1", 0.01, 10.0, 0.5, key="basic_R1")
            NTU1 = st.number_input("NTU1", 0.01, 20.0, 1.0, key="basic_NTU")
            subtype = st.selectbox("Configuration", [
                'counterflow', 'parallel', 'crossflow',
                'crossflow, mixed 1', 'crossflow, mixed 2', 'crossflow, mixed 1&2'
            ], key="basic_subtype")
            if compute_all:
                eff = temperature_effectiveness_basic(R1, NTU1, subtype)
                st.success(f"Efficacité : {eff:.5f}")

        tema_ui(tabs[1], temperature_effectiveness_TEMA_E, "tema_e")
        tema_ui(tabs[2], temperature_effectiveness_TEMA_G, "tema_g")
        tema_ui(tabs[3], temperature_effectiveness_TEMA_H, "tema_h")
        tema_ui(tabs[4], temperature_effectiveness_TEMA_J, "tema_j")

        # Air Cooler
        with tabs[5]:
            col1, col2 = st.columns(2)
            with col1:
                R1 = st.number_input("R1", 0.01, 10.0, 0.5, key="air_R1")
                NTU1 = st.number_input("NTU1", 0.01, 20.0, 2.0, key="air_NTU")
            with col2:
                rows = st.number_input("Rangées", 1, 20, 4, key="air_rows")
                passes = st.number_input("Passes", 1, 5, 2, key="air_passes")
            if compute_all:
                eff = temperature_effectiveness_air_cooler(R1, NTU1, rows, passes)
                st.success(f"Efficacité : {eff:.5f}")

        # Plaques
        with tabs[6]:
            R1 = st.number_input("R1", 0.01, 10.0, 0.5, key="plate_R1")
            NTU1 = st.number_input("NTU1", 0.01, 20.0, 1.0, key="plate_NTU")
            Np1 = st.number_input("Passes côté 1", 1, 4, 2, key="plate_Np1")
            Np2 = st.number_input("Passes côté 2", 1, 4, 2, key="plate_Np2")
            cf = st.checkbox("Contre-courant global", True, key="plate_cf")
            scf = st.checkbox("Contre-courant individuel", True, key="plate_scf")
            if compute_all:
                eff = temperature_effectiveness_plate(R1, NTU1, Np1, Np2, cf, scf)
                st.success(f"Efficacité : {eff:.5f}")

        # P-NTU
        with tabs[7]:
            col1, col2 = st.columns(2)
            with col1:
                m1 = st.number_input("Débit massique 1 [kg/s]", 0.1, 50.0, 5.2, key="pntu_m1")
                Cp1 = st.number_input("Cp1 [J/kg.K]", 1000.0, 5000.0, 1860.0, key="pntu_Cp1")
                T1i = st.number_input("T1 entrée [°C]", 0.0, 300.0, 130.0, key="pntu_T1i")
            with col2:
                m2 = st.number_input("Débit massique 2 [kg/s]", 0.1, 50.0, 1.45, key="pntu_m2")
                Cp2 = st.number_input("Cp2 [J/kg.K]", 1000.0, 5000.0, 1900.0, key="pntu_Cp2")
                T2i = st.number_input("T2 entrée [°C]", 0.0, 300.0, 15.0, key="pntu_T2i")

            f1,f2,f3 = st.columns(3)
            with f1:
                UA = st.number_input("UA [W/K]", 10.0, 10000.0, 3000.0, key="pntu_UA")
            with f2:
                subtype = st.selectbox("Configuration échangeur", ['E', 'G', 'H', 'J', 'crossflow'], key="pntu_subtype")
            with f3:
                Ntp = st.number_input("Passes tubes", 1, 2, 2, key="pntu_Ntp")  # G only supports 1 or 2
            if compute_all:
                try:
                    result = P_NTU_method(m1, m2, Cp1, Cp2, T1i=T1i, T2i=T2i, UA=UA, subtype=subtype, Ntp=Ntp)
                    st.json(result)
                except Exception as e:
                    st.error(str(e))

with c2:
        # ---------------------- Résumé des Données ----------------------
    with st.expander("🧾 Résumé Complet des Paramètres et Résultats", expanded=False):
        if compute_all:
            data = {
                "Paramètre": [
                    "Do [m]", "pitch [m]", "angle [°]", "Ntp", "N", "Matériau", "L_unsupported [m]",
                    "DB_Perry [m]", "N_Perry", "DB_HEDH [m]", "DB_Phadkeb [m]", "DB_VDI [m]",
                    "DShell_min [m]", "Clearance auto [m]", "dB_hole [m]", "L_max [m]",
                    "Débit m1 [kg/s]", "Cp1 [J/kg.K]", "T1 entrée [°C]",
                    "Débit m2 [kg/s]", "Cp2 [J/kg.K]", "T2 entrée [°C]",
                    "UA [W/K]", "Subtype HX", "Ntp (P-NTU)"
                ],
                "Valeur": [
                    Do, pitch, angle, Ntp, N, material, L_unsupported,
                    st.session_state.DB_Perry, st.session_state.N_Perry, st.session_state.DB_HEDH,
                    st.session_state.DB_Phadkeb, st.session_state.DB_VDI, st.session_state.DShell_min,
                    st.session_state.clearance_auto, st.session_state.dB_hole, st.session_state.L_max,
                    m1, Cp1, T1i, m2, Cp2, T2i, UA, subtype, Ntp
                ]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Cliquez sur 'Calculer tous les résultats' pour générer le résumé complet.")
