import streamlit as st
import pandas as pd
import numpy as np
from utils.helpers import show_metric, effectiveness_chart
from ht.hx import (
    temperature_effectiveness_basic,
    temperature_effectiveness_TEMA_E,
    temperature_effectiveness_TEMA_G,
    temperature_effectiveness_TEMA_H,
    temperature_effectiveness_TEMA_J,
    temperature_effectiveness_air_cooler,
    temperature_effectiveness_plate,
    P_NTU_method,
)

def tema_ui(tab, func, key_prefix: str, run_all: bool) -> None:
    with tab:
        with st.form(f"{key_prefix}_form"):
            c1, c2, c3 = st.columns(3)
            R1 = c1.number_input("R1", 0.01, 10.0, 0.5, key=f"{key_prefix}_R1")
            NTU1 = c2.number_input("NTU1", 0.01, 20.0, 1.0, key=f"{key_prefix}_NTU")
            Ntp_local = c3.number_input("Passes tubes", 1, 4, 1, key=f"{key_prefix}_Ntp")
            optimal = None
            if func.__name__ != "temperature_effectiveness_TEMA_J":
                optimal = st.checkbox("Contre-courant", True, key=f"{key_prefix}_opt")
            submit = st.form_submit_button("Calculer")
        run = submit or run_all
        if run:
            if func.__name__ == "temperature_effectiveness_TEMA_J":
                eff = func(R1, NTU1, Ntp_local)
                show_metric("Efficacité estimée", eff)
                effectiveness_chart(func, R1, Ntp=Ntp_local)
            else:
                eff = func(R1, NTU1, Ntp_local, optimal)
                show_metric("Efficacité estimée", eff)
                effectiveness_chart(func, R1, Ntp=Ntp_local, optimal=optimal)

def effectiveness_section(run_all: bool) -> None:
    st.subheader("🔥 Méthodes d'Efficacité Thermique")
    tabs = st.tabs([
        "Basique", "TEMA E", "TEMA G", "TEMA H", "TEMA J",
        "Air Cooler", "Plaques", "Solveur P-NTU",
    ])

    with tabs[0]:
        with st.form("basic_form"):
            r1 = st.number_input("R1", 0.01, 10.0, 0.5)
            ntu = st.number_input("NTU", 0.01, 20.0, 1.0)
            subtype = st.selectbox(
                "Configuration",
                [
                    "counterflow", "parallel", "crossflow",
                    "crossflow, mixed 1", "crossflow, mixed 2", "crossflow, mixed 1&2",
                ],
            )
            submit = st.form_submit_button("Calculer")
        run = submit or run_all
        if run:
            eff = temperature_effectiveness_basic(r1, ntu, subtype)
            show_metric("Efficacité estimée", eff)
            effectiveness_chart(temperature_effectiveness_basic, r1, subtype=subtype)

    tema_ui(tabs[1], temperature_effectiveness_TEMA_E, "tema_e", run_all)
    tema_ui(tabs[2], temperature_effectiveness_TEMA_G, "tema_g", run_all)
    tema_ui(tabs[3], temperature_effectiveness_TEMA_H, "tema_h", run_all)
    tema_ui(tabs[4], temperature_effectiveness_TEMA_J, "tema_j", run_all)

    with tabs[5]:
        with st.form("air_form"):
            col1, col2 = st.columns(2)
            R1 = col1.number_input("R1", 0.01, 10.0, 0.5)
            NTU1 = col2.number_input("NTU1", 0.01, 20.0, 2.0)
            rows = col1.number_input("Rangées", 1, 20, 4)
            passes = col2.number_input("Passes", 1, 5, 2)
            submit = st.form_submit_button("Calculer")
        run = submit or run_all
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
            R1 = st.number_input("R1", 0.01, 10.0, 0.5)
            NTU1 = st.number_input("NTU1", 0.01, 20.0, 1.0)
            Np1 = st.number_input("Passes côté 1", 1, 4, 2)
            Np2 = st.number_input("Passes côté 2", 1, 4, 2)
            cf = st.checkbox("Contre-courant global", True)
            scf = st.checkbox("Contre-courant individuel", True)
            submit = st.form_submit_button("Calculer")
        run = submit or run_all
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
        run = submit or run_all
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