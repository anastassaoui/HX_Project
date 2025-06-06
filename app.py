import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

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
    L_unsupported_max,
)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def show_metric(label: str, value: float, unit: str = "") -> None:
    """Display a numeric value as a Streamlit metric."""
    formatted = f"{value:.5f} {unit}" if unit else f"{value:.5f}"
    st.metric(label, formatted)


def effectiveness_chart(func, R1: float, **kwargs) -> None:
    """Plot effectiveness vs. NTU using the provided correlation."""
    NTU_range = np.linspace(0.1, 10.0, 50)
    effs = [func(R1, NTU, **kwargs) for NTU in NTU_range]
    df = pd.DataFrame({"NTU": NTU_range, "Effectiveness": effs}).set_index("NTU")
    st.line_chart(df)


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

def init_session_state() -> None:
    keys = [
        "DB_Perry", "N_Perry", "DB_HEDH", "DB_Phadkeb", "DB_VDI",
        "DShell_min", "clearance_auto", "dB_hole", "L_max",
        "inputs_geometry", "inputs_pntu", "clearance_result",
    ]
    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = None


# ---------------------------------------------------------------------------
# UI sections
# ---------------------------------------------------------------------------

def geometry_section(compute_all: bool) -> None:
    st.header("📐 Calculs de Géométrie")
    left, right = st.columns([2, 1])
    with left:
        with st.form("geom_form"):
            r1c1, r1c2 = st.columns(2)
            Do = r1c1.number_input("Ø extérieur [m]", 0.005, 0.1, 0.025)
            pitch = r1c2.number_input("Pas triangulaire [m]", 0.01, 0.1, 0.03125)

            r2c1, r2c2 = st.columns(2)
            angle = r2c1.selectbox("Angle d'agencement [°]", [30, 45, 60, 90], index=0)
            Ntp = r2c2.selectbox("Passes tubes", [1, 2], index=1)

            N = st.slider("Nombre de tubes", 1, 2000, 928)
            L_unsupported = st.number_input("Longueur non supportée [m]", 0.1, 10.0, 0.75)
            material = st.selectbox("Matériau du tube", ["CS", "aluminium"])

            submit = st.form_submit_button("Calculer géométrie")

        run = submit or compute_all
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
    with right:
        if st.session_state.DB_Perry:
            st.subheader("Résultats")
            show_metric("Faisceau Perry", st.session_state.DB_Perry, "m")
            show_metric("Tubes Perry", st.session_state.N_Perry)
            st.code(f"HEDH    = {st.session_state.DB_HEDH:.5f} m")
            st.code(f"Phadkeb = {st.session_state.DB_Phadkeb:.5f} m")
            st.code(f"VDI     = {st.session_state.DB_VDI:.5f} m")
            st.code(f"DShell_min = {st.session_state.DShell_min:.5f} m")
            show_metric("Jeu calandre-faisceau (HEDH)", st.session_state.clearance_auto, "m")
            show_metric("Ø trou chicane (TEMA)", st.session_state.dB_hole, "m")
            show_metric("L_max sans support", st.session_state.L_max, "m")


def clearance_section(compute_all: bool) -> None:
    st.header("📏 Jeu Calandre-Faisceau")
    left, right = st.columns(2)
    with left:
        with st.form("clearance_form"):
            clearance_mode = st.radio("Basé sur", ["Diamètre faisceau", "Diamètre calandre"], horizontal=True)
            db = ds = None
            if clearance_mode == "Diamètre faisceau":
                default_db = st.session_state.DB_Perry or 1.2
                db = st.slider("Diamètre du faisceau [m]", 0.1, 3.0, default_db)
            else:
                ds = st.slider("Diamètre de la calandre [m]", 0.1, 3.0, 1.25)
            submit = st.form_submit_button("Calculer jeu")
        run = submit or compute_all
        if run:
            result = shell_clearance(DBundle=db) if db else shell_clearance(DShell=ds)
            st.session_state.clearance_result = result
    with right:
        if st.session_state.clearance_result:
            show_metric("Jeu recommandé", st.session_state.clearance_result, "m")


def tema_ui(tab, func, key_prefix: str, compute_all: bool) -> None:
    with tab:
        with st.form(f"{key_prefix}_form"):
            c1, c2, c3 = st.columns(3)
            R1 = c1.number_input("R1", 0.01, 10.0, 0.5, key=f"{key_prefix}_R1")
            NTU1 = c2.number_input("NTU1", 0.01, 20.0, 1.0, key=f"{key_prefix}_NTU")
            Ntp_local = c3.number_input("Passes tubes", 1, 4, 1, key=f"{key_prefix}_Ntp")
            optimal = st.checkbox("Contre-courant", True, key=f"{key_prefix}_opt") if func.__name__ != "temperature_effectiveness_TEMA_J" else None
            submit = st.form_submit_button("Calculer")
        run = submit or compute_all
        if run:
            if func.__name__ == "temperature_effectiveness_TEMA_J":
                eff = func(R1, NTU1, Ntp_local)
                show_metric("Efficacité estimée", eff)
                effectiveness_chart(func, R1, Ntp=Ntp_local)
            else:
                eff = func(R1, NTU1, Ntp_local, optimal)
                show_metric("Efficacité estimée", eff)
                effectiveness_chart(func, R1, Ntp=Ntp_local, optimal=optimal)


def effectiveness_section(compute_all: bool) -> None:
    st.header("🔥 Méthodes d'Efficacité Thermique")
    tabs = st.tabs([
        "Basique", "TEMA E", "TEMA G", "TEMA H", "TEMA J",
        "Air Cooler", "Plaques", "Solveur P-NTU",
    ])

    with tabs[0]:
        with st.form("basic_form"):
            R1 = st.number_input("R1", 0.01, 10.0, 0.5, key="basic_R1")
            NTU1 = st.number_input("NTU1", 0.01, 20.0, 1.0, key="basic_NTU")
            subtype = st.selectbox(
                "Configuration",
                [
                    "counterflow", "parallel", "crossflow",
                    "crossflow, mixed 1", "crossflow, mixed 2", "crossflow, mixed 1&2",
                ],
                key="basic_subtype",
            )
            submit = st.form_submit_button("Calculer")
        run = submit or compute_all
        if run:
            eff = temperature_effectiveness_basic(R1, NTU1, subtype)
            show_metric("Efficacité estimée", eff)
            effectiveness_chart(temperature_effectiveness_basic, R1, subtype=subtype)

    tema_ui(tabs[1], temperature_effectiveness_TEMA_E, "tema_e", compute_all)
    tema_ui(tabs[2], temperature_effectiveness_TEMA_G, "tema_g", compute_all)
    tema_ui(tabs[3], temperature_effectiveness_TEMA_H, "tema_h", compute_all)
    tema_ui(tabs[4], temperature_effectiveness_TEMA_J, "tema_j", compute_all)

    with tabs[5]:
        with st.form("air_form"):
            col1, col2 = st.columns(2)
            R1 = col1.number_input("R1", 0.01, 10.0, 0.5, key="air_R1")
            NTU1 = col2.number_input("NTU1", 0.01, 20.0, 2.0, key="air_NTU")
            rows = col1.number_input("Rangées", 1, 20, 4, key="air_rows")
            passes = col2.number_input("Passes", 1, 5, 2, key="air_passes")
            submit = st.form_submit_button("Calculer")
        run = submit or compute_all
        if run:
            eff = temperature_effectiveness_air_cooler(R1, NTU1, rows, passes)
            show_metric("Efficacité estimée", eff)
            effectiveness_chart(
                temperature_effectiveness_air_cooler,
                R1,
                rows=rows,
                passes=passes,
            )

    with tabs[6]:
        with st.form("plate_form"):
            R1 = st.number_input("R1", 0.01, 10.0, 0.5, key="plate_R1")
            NTU1 = st.number_input("NTU1", 0.01, 20.0, 1.0, key="plate_NTU")
            Np1 = st.number_input("Passes côté 1", 1, 4, 2, key="plate_Np1")
            Np2 = st.number_input("Passes côté 2", 1, 4, 2, key="plate_Np2")
            cf = st.checkbox("Contre-courant global", True, key="plate_cf")
            scf = st.checkbox("Contre-courant individuel", True, key="plate_scf")
            submit = st.form_submit_button("Calculer")
        run = submit or compute_all
        if run:
            eff = temperature_effectiveness_plate(R1, NTU1, Np1, Np2, cf, scf)
            show_metric("Efficacité estimée", eff)
            effectiveness_chart(
                temperature_effectiveness_plate,
                R1,
                Np1=Np1,
                Np2=Np2,
                counterflow=cf,
                passes_counterflow=scf,
            )

    with tabs[7]:
        with st.form("pntu_form"):
            r1c1, r1c2 = st.columns(2)
            m1 = r1c1.number_input("Débit m1 [kg/s]", 0.1, 50.0, 5.2)
            m2 = r1c2.number_input("Débit m2 [kg/s]", 0.1, 50.0, 1.45)

            r2c1, r2c2 = st.columns(2)
            Cp1 = r2c1.number_input("Cp1 [J/kg.K]", 1000.0, 5000.0, 1860.0)
            Cp2 = r2c2.number_input("Cp2 [J/kg.K]", 1000.0, 5000.0, 1900.0)

            r3c1, r3c2 = st.columns(2)
            T1i = r3c1.number_input("T1 entrée [°C]", 0.0, 300.0, 130.0)
            T2i = r3c2.number_input("T2 entrée [°C]", 0.0, 300.0, 15.0)

            f1, f2, f3 = st.columns(3)
            UA = f1.number_input("UA [W/K]", 10.0, 10000.0, 3000.0)
            subtype = f2.selectbox("Configuration HX", ["E", "G", "H", "J", "crossflow"])
            Ntp = f3.number_input("Passes tubes", 1, 2, 2)
            submit = st.form_submit_button("Calculer")
        run = submit or compute_all
        if run:
            try:
                result = P_NTU_method(
                    m1,
                    m2,
                    Cp1,
                    Cp2,
                    T1i=T1i,
                    T2i=T2i,
                    UA=UA,
                    subtype=subtype,
                    Ntp=Ntp,
                )
                st.json(result)
            except Exception as e:
                st.error(str(e))
            st.session_state.inputs_pntu = {
                "m1": m1,
                "Cp1": Cp1,
                "T1i": T1i,
                "m2": m2,
                "Cp2": Cp2,
                "T2i": T2i,
                "UA": UA,
                "subtype": subtype,
                "Ntp": Ntp,
            }


def summary_section(compute_all: bool) -> None:
    st.header("🧾 Résumé Complet")
    if compute_all and st.session_state.inputs_geometry and st.session_state.inputs_pntu:
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
    else:
        st.info("Cliquez sur 'Calculer tout' pour générer le résumé complet.")


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Suite de Conception d'Échangeur de Chaleur", layout="wide")
st.title("🧪 Suite d'Ingénierie : Échangeur Tubulaire à Calandre")
init_session_state()

with st.sidebar:
    st.header("Navigation")
    compute_all = st.button("🚀 Calculer tout")
    selection = option_menu(
        menu_title="",
        options=["Géométrie", "Jeu Calandre", "Efficacité", "Résumé"],
        icons=["rulers", "arrows-angle-contract", "graph-up", "table"],
        menu_icon="cast",
        default_index=0,
    )

if selection == "Géométrie":
    geometry_section(compute_all)
elif selection == "Jeu Calandre":
    clearance_section(compute_all)
elif selection == "Efficacité":
    effectiveness_section(compute_all)
elif selection == "Résumé":
    summary_section(compute_all)
