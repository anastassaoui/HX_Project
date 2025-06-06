import streamlit as st
import pandas as pd
import numpy as np

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
    """Ensure all expected keys exist in session state."""
    keys = [
        "DB_Perry", "N_Perry", "DB_HEDH", "DB_Phadkeb", "DB_VDI",
        "DShell_min", "clearance_auto", "dB_hole", "L_max",
        "inputs_geometry", "inputs_pntu",
    ]
    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = None


# ---------------------------------------------------------------------------
# UI sections
# ---------------------------------------------------------------------------

def geometry_section(compute_all: bool) -> None:
    """Geometry calculations and results."""
    with st.expander("📐 Calculs de Géométrie"):
        col1, col2 = st.columns(2)
        with col1:
            Do = st.number_input("Diamètre extérieur du tube [m]", 0.005, 0.1, 0.025)
            pitch = st.number_input("Pas triangulaire [m]", 0.01, 0.1, 0.03125)
        with col2:
            angle = st.selectbox("Angle d'agencement [°]", [30, 45, 60, 90], index=0)
            Ntp = st.selectbox("Nombre de passes tubes", [1, 2], index=1)
        N = st.slider("Nombre de tubes", 1, 2000, 928)
        L_unsupported = st.number_input("Longueur non supportée [m]", 0.1, 10.0, 0.75)
        material = st.selectbox("Matériau du tube", ["CS", "aluminium"])

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
            st.session_state.inputs_geometry = {
                "Do": Do,
                "pitch": pitch,
                "angle": angle,
                "Ntp": Ntp,
                "N": N,
                "material": material,
                "L_unsupported": L_unsupported,
            }

        if st.session_state.DB_Perry:
            st.markdown("### 🧾 Résultats Géométriques Calculés")
            d1, d2, d3 = st.columns(3)

            with d1:
                st.subheader("📏 Méthode Perry")
                st.success(f"Faisceau Perry : `{st.session_state.DB_Perry:.5f} m`")
                st.info(f"Tubes Perry : `{int(st.session_state.N_Perry)}`")

            with d2:
                st.subheader("📐 Estimations Avancées")
                st.code(f"HEDH    = {st.session_state.DB_HEDH:.5f} m", language="python")
                st.code(f"Phadkeb = {st.session_state.DB_Phadkeb:.5f} m", language="python")
                st.code(f"VDI     = {st.session_state.DB_VDI:.5f} m", language="python")
                st.code(f"DShell_min = {st.session_state.DShell_min:.5f} m", language="python")

            with d3:
                st.subheader("🔧 Dérivés Pratiques")
                show_metric("Jeu calandre-faisceau (HEDH)", st.session_state.clearance_auto, "m")
                st.info(f"Ø trou chicane (TEMA) : `{st.session_state.dB_hole:.5f} m`")
                st.warning(f"L_max sans support : `{st.session_state.L_max:.2f} m`")


def clearance_section(compute_all: bool) -> None:
    """Standalone shell-clearance calculator."""
    with st.expander("📏 Jeu Calandre-Faisceau"):
        clearance_mode = st.radio("Basé sur", ["Diamètre faisceau", "Diamètre calandre"], horizontal=True)
        db = ds = None
        if clearance_mode == "Diamètre faisceau":
            default_db = st.session_state.DB_Perry or 1.2
            db = st.slider("Diamètre du faisceau [m]", 0.1, 3.0, default_db)
        else:
            ds = st.slider("Diamètre de la calandre [m]", 0.1, 3.0, 1.25)

        if compute_all:
            result = shell_clearance(DBundle=db) if db else shell_clearance(DShell=ds)
            st.session_state.clearance_result = result
        if st.session_state.get("clearance_result"):
            show_metric("Jeu recommandé", st.session_state.clearance_result, "m")


def tema_ui(tab, func, key_prefix: str, compute_all: bool) -> None:
    """Reusable UI for each TEMA correlation."""
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
                show_metric("Efficacité estimée", eff)
                effectiveness_chart(func, R1, Ntp=Ntp_local)
            else:
                eff = func(R1, NTU1, Ntp_local, optimal)
                show_metric("Efficacité estimée", eff)
                effectiveness_chart(func, R1, Ntp=Ntp_local, optimal=optimal)


def effectiveness_section(compute_all: bool) -> None:
    """All effectiveness methods and P-NTU solver."""
    with st.expander("🔥 Méthodes d'Efficacité Thermique"):
        tabs = st.tabs([
            "Basique", "TEMA E", "TEMA G", "TEMA H", "TEMA J",
            "Air Cooler", "Plaques", "Solveur P-NTU",
        ])

        with tabs[0]:
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
            if compute_all:
                eff = temperature_effectiveness_basic(R1, NTU1, subtype)
                show_metric("Efficacité estimée", eff)
                effectiveness_chart(temperature_effectiveness_basic, R1, subtype=subtype)

        tema_ui(tabs[1], temperature_effectiveness_TEMA_E, "tema_e", compute_all)
        tema_ui(tabs[2], temperature_effectiveness_TEMA_G, "tema_g", compute_all)
        tema_ui(tabs[3], temperature_effectiveness_TEMA_H, "tema_h", compute_all)
        tema_ui(tabs[4], temperature_effectiveness_TEMA_J, "tema_j", compute_all)

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
                show_metric("Efficacité estimée", eff)
                effectiveness_chart(
                    temperature_effectiveness_air_cooler,
                    R1,
                    rows=rows,
                    passes=passes,
                )

        with tabs[6]:
            R1 = st.number_input("R1", 0.01, 10.0, 0.5, key="plate_R1")
            NTU1 = st.number_input("NTU1", 0.01, 20.0, 1.0, key="plate_NTU")
            Np1 = st.number_input("Passes côté 1", 1, 4, 2, key="plate_Np1")
            Np2 = st.number_input("Passes côté 2", 1, 4, 2, key="plate_Np2")
            cf = st.checkbox("Contre-courant global", True, key="plate_cf")
            scf = st.checkbox("Contre-courant individuel", True, key="plate_scf")
            if compute_all:
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
            col1, col2 = st.columns(2)
            with col1:
                m1 = st.number_input("Débit massique 1 [kg/s]", 0.1, 50.0, 5.2)
                Cp1 = st.number_input("Cp1 [J/kg.K]", 1000.0, 5000.0, 1860.0)
                T1i = st.number_input("T1 entrée [°C]", 0.0, 300.0, 130.0)
            with col2:
                m2 = st.number_input("Débit massique 2 [kg/s]", 0.1, 50.0, 1.45)
                Cp2 = st.number_input("Cp2 [J/kg.K]", 1000.0, 5000.0, 1900.0)
                T2i = st.number_input("T2 entrée [°C]", 0.0, 300.0, 15.0)

            f1, f2, f3 = st.columns(3)
            with f1:
                UA = st.number_input("UA [W/K]", 10.0, 10000.0, 3000.0)
            with f2:
                subtype = st.selectbox("Configuration échangeur", ["E", "G", "H", "J", "crossflow"])
            with f3:
                Ntp = st.number_input("Passes tubes", 1, 2, 2)
            if compute_all:
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
            if compute_all:
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
    """Display a dataframe summarizing inputs and key results."""
    with st.expander("🧾 Résumé Complet des Paramètres et Résultats", expanded=False):
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
            st.info("Cliquez sur 'Calculer tous les résultats' pour générer le résumé complet.")


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Suite de Conception d'Échangeur de Chaleur", layout="wide")
st.title("🧪 Suite d'Ingénierie : Échangeur Tubulaire à Calandre")
st.markdown("---")

compute_all = st.button("🚀 Calculer tous les résultats")
init_session_state()

c1, c2, c3 = st.columns([3, 2, 3])
with c1:
    geometry_section(compute_all)
with c2:
    clearance_section(compute_all)
with c3:
    effectiveness_section(compute_all)

summary_section(compute_all)
