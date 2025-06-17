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

def effectiveness_result_card(label, value):
    st.markdown(f"""
    <style>
    .eff-card {{
        background: linear-gradient(120deg, #f0f2f6 60%, #e0e7ff 100%);
        border-radius: 16px;
        padding: 1.5em 1em 1em 1em;
        box-shadow: 0 2px 8px rgba(80,80,120,0.07);
        margin-bottom: 1em;
        margin-top: 2em;
        width: 100%;
        overflow-x: auto;
    }}
    .eff-metric-row {{
        display: flex;
        flex-direction: row;
        gap: 2em;
        flex-wrap: nowrap;
        overflow-x: auto;
    }}
    .eff-metric {{
        min-width: 180px;
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 0.5em;
    }}
    .eff-label {{
        color: #4b4b6b;
        font-weight: 700;
    }}
    .eff-value {{
        color: #ff4b4b;
        font-size: 1.2em;
        font-weight: 700;
    }}
    </style>
    <div class="eff-card">
    <h4 style="margin-bottom:1em;">⚡ <b>Résultat Efficacité</b></h4>
    <div class="eff-metric-row">
        <div class="eff-metric"><span class="eff-label">{label}</span><br><span class="eff-value">{value:.3f}</span></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

def tema_ui(tab, func, key_prefix: str, run_all: bool) -> None:
    with tab:
        with st.form(f"{key_prefix}_form"):
            c1, c2, c3 = st.columns(3)
            R1 = c1.number_input(
                "R1", 0.01, 10.0, 0.5, key=f"{key_prefix}_R1",
                help="Rapport de capacité thermique (Cmin/Cmax). Doit être > 0."
            )
            NTU1 = c2.number_input(
                "NTU1", 0.01, 20.0, 1.0, key=f"{key_prefix}_NTU",
                help="Nombre d'unités de transfert (NTU). Doit être > 0."
            )
            Ntp_local = c3.number_input(
                "Passes tubes", 1, 4, 1, key=f"{key_prefix}_Ntp",
                help="Nombre de passes côté tubes (1 à 4)."
            )
            optimal = None
            if func.__name__ != "temperature_effectiveness_TEMA_J":
                optimal = st.checkbox("Contre-courant", True, key=f"{key_prefix}_opt", help="Active le mode contre-courant si disponible.")
            submit = st.form_submit_button("Calculer")
        run = submit or run_all
        if run:
            if func.__name__ == "temperature_effectiveness_TEMA_J":
                eff = func(R1, NTU1, Ntp_local)
                effectiveness_result_card("Efficacité estimée", eff)
                effectiveness_chart(func, R1, Ntp=Ntp_local)
            else:
                eff = func(R1, NTU1, Ntp_local, optimal)
                effectiveness_result_card("Efficacité estimée", eff)
                effectiveness_chart(func, R1, Ntp=Ntp_local, optimal=optimal)

def effectiveness_section(run_all: bool) -> None:
    st.subheader("Méthodes d'Efficacité Thermique")
    tabs = st.tabs([
        "Basique", "TEMA E", "TEMA G", "TEMA H", "TEMA J",
        "Air Cooler", "Plaques", "Solveur P-NTU",
    ])

    with tabs[0]:
        with st.form("basic_form"):
            r1 = st.number_input(
                "R1", 0.01, 10.0, 0.5,
                help="Rapport de capacité thermique (Cmin/Cmax). Doit être > 0."
            )
            ntu = st.number_input(
                "NTU", 0.01, 20.0, 1.0,
                help="Nombre d'unités de transfert (NTU). Doit être > 0."
            )
            subtype = st.selectbox(
                "Configuration",
                [
                    "counterflow", "parallel", "crossflow",
                    "crossflow, mixed 1", "crossflow, mixed 2", "crossflow, mixed 1&2",
                ],
                help="Sélectionnez la configuration de l'échangeur."
            )
            submit = st.form_submit_button("Calculer")
        run = submit or run_all
        if run:
            eff = temperature_effectiveness_basic(r1, ntu, subtype)
            effectiveness_result_card("Efficacité estimée", eff)
            effectiveness_chart(temperature_effectiveness_basic, r1, subtype=subtype)

    tema_ui(tabs[1], temperature_effectiveness_TEMA_E, "tema_e", run_all)
    tema_ui(tabs[2], temperature_effectiveness_TEMA_G, "tema_g", run_all)
    tema_ui(tabs[3], temperature_effectiveness_TEMA_H, "tema_h", run_all)
    tema_ui(tabs[4], temperature_effectiveness_TEMA_J, "tema_j", run_all)

    with tabs[5]:
        with st.form("air_form"):
            col1, col2 = st.columns(2)
            R1 = col1.number_input(
                "R1", 0.01, 10.0, 0.5,
                help="Rapport de capacité thermique (Cmin/Cmax). Doit être > 0."
            )
            NTU1 = col2.number_input(
                "NTU1", 0.01, 20.0, 2.0,
                help="Nombre d'unités de transfert (NTU). Doit être > 0."
            )
            rows = col1.number_input(
                "Rangées", 1, 20, 4,
                help="Nombre de rangées de tubes dans l'air cooler."
            )
            passes = col2.number_input(
                "Passes", 1, 5, 2,
                help="Nombre de passes côté air."
            )
            submit = st.form_submit_button("Calculer")
        run = submit or run_all
        if run:
            eff = temperature_effectiveness_air_cooler(R1, NTU1, rows, passes)
            effectiveness_result_card("Efficacité estimée", eff)
            effectiveness_chart(
                temperature_effectiveness_air_cooler,
                R1,
                rows=rows,
                passes=passes,
            )

    with tabs[6]:
        with st.form("plate_form"):
            R1 = st.number_input(
                "R1", 0.01, 10.0, 0.5,
                help="Rapport de capacité thermique (Cmin/Cmax). Doit être > 0."
            )
            NTU1 = st.number_input(
                "NTU1", 0.01, 20.0, 1.0,
                help="Nombre d'unités de transfert (NTU). Doit être > 0."
            )
            Np1 = st.number_input(
                "Passes côté 1", 1, 4, 2,
                help="Nombre de passes côté 1 (1 à 4)."
            )
            Np2 = st.number_input(
                "Passes côté 2", 1, 4, 2,
                help="Nombre de passes côté 2 (1 à 4)."
            )
            cf = st.checkbox("Contre-courant global", True, help="Active le mode contre-courant global.")
            scf = st.checkbox("Contre-courant individuel", True, help="Active le mode contre-courant individuel.")
            submit = st.form_submit_button("Calculer")
        run = submit or run_all
        if run:
            eff = temperature_effectiveness_plate(R1, NTU1, Np1, Np2, cf, scf)
            effectiveness_result_card("Efficacité estimée", eff)
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
            m1 = r1c1.number_input(
                "Débit m1 [kg/s]", 0.1, 50.0, 5.2,
                help="Débit massique du fluide 1 (kg/s)."
            )
            m2 = r1c2.number_input(
                "Débit m2 [kg/s]", 0.1, 50.0, 1.45,
                help="Débit massique du fluide 2 (kg/s)."
            )

            r2c1, r2c2 = st.columns(2)
            Cp1 = r2c1.number_input(
                "Cp1 [J/kg.K]", 1000.0, 5000.0, 1860.0,
                help="Capacité thermique massique du fluide 1 (J/kg.K)."
            )
            Cp2 = r2c2.number_input(
                "Cp2 [J/kg.K]", 1000.0, 5000.0, 1900.0,
                help="Capacité thermique massique du fluide 2 (J/kg.K)."
            )

            r3c1, r3c2 = st.columns(2)
            T1i = r3c1.number_input(
                "T1 entrée [°C]", 0.0, 300.0, 130.0,
                help="Température d'entrée du fluide 1 (°C)."
            )
            T2i = r3c2.number_input(
                "T2 entrée [°C]", 0.0, 300.0, 15.0,
                help="Température d'entrée du fluide 2 (°C)."
            )

            f1, f2, f3 = st.columns(3)
            UA = f1.number_input(
                "UA [W/K]", 10.0, 10000.0, 3000.0,
                help="Produit du coefficient global d'échange et de la surface (UA)."
            )
            subtype = f2.selectbox(
                "Configuration HX", ["E", "G", "H", "J", "crossflow"],
                help="Type/configuration de l'échangeur."
            )
            Ntp = f3.number_input(
                "Passes tubes", 1, 2, 2,
                help="Nombre de passes côté tubes (1 ou 2)."
            )
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