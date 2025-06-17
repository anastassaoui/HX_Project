import streamlit as st
import pandas as pd
import joblib

def ml_result_card(fouling, ttc, status):
    st.markdown(f"""
    <style>
    .ml-card {{
        background: linear-gradient(120deg, #f0f2f6 60%, #e0e7ff 100%);
        border-radius: 16px;
        padding: 1.5em 1em 1em 1em;
        box-shadow: 0 2px 8px rgba(80,80,120,0.07);
        margin-bottom: 1em;
        margin-top: 2em;
        width: 100%;
        overflow-x: auto;
    }}
    .ml-metric-row {{
        display: flex;
        flex-direction: row;
        gap: 2em;
        flex-wrap: nowrap;
        overflow-x: auto;
    }}
    .ml-metric {{
        min-width: 180px;
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 0.5em;
    }}
    .ml-label {{
        color: #4b4b6b;
        font-weight: 700;
    }}
    .ml-value {{
        color: #ff4b4b;
        font-size: 1.2em;
        font-weight: 700;
    }}
    .ml-status {{
        font-size: 1.3em;
        font-weight: 700;
        margin-top: 0.5em;
    }}
    </style>
    <div class="ml-card">
    <h4 style="margin-bottom:1em;"> <b>Prédiction Encrassement</b></h4>
    <div class="ml-metric-row">
        <div class="ml-metric"><span class="ml-label">Niveau d'encrassement</span><br><span class="ml-value">{fouling:.3f}</span></div>
        <div class="ml-metric"><span class="ml-label">Heures avant nettoyage</span><br><span class="ml-value">{ttc:,.1f} h</span></div>
        <div class="ml-metric ml-status">{status}</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

def fouling_prediction_section() -> None:
    st.subheader("Prédiction d'Encrassement")
    
    try:
        m_foul = joblib.load("model_fouling.pkl")
        m_ttc = joblib.load("model_ttc.pkl")
        
        with st.form("fouling_form"):
            rtc = st.number_input(
                "Heures depuis dernier nettoyage", 0, 7*365*24, 100,
                help="Nombre d'heures de fonctionnement depuis le dernier nettoyage (0 à 7 ans)."
            )
            a1, a2 = st.columns(2)
            
            with a1:
                with st.expander("Mesures de performance", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        dTh = st.slider(
                            "ΔT côté chaud (°C)", 0.0, 40.0, 18.0, 0.1,
                            help="Différence de température côté chaud (0 à 40°C)."
                        )
                    with c2:
                        dTc = st.slider(
                            "ΔT côté froid (°C)", 0.0, 40.0, 16.0, 0.1,
                            help="Différence de température côté froid (0 à 40°C)."
                        )
                    dp = st.slider(
                        "ΔP calandre (kPa)", 0.0, 150.0, 20.0, 0.1,
                        help="Perte de charge côté calandre (0 à 150 kPa)."
                    )
            
            with a2:
                with st.expander(" Conditions d'opération", expanded=False):
                    t1, t2 = st.columns(2)
                    with t1:
                        Tin_hot = st.slider(
                            "T entrée chaud (°C)", 80, 180, 140,
                            help="Température d'entrée du fluide chaud (80 à 180°C)."
                        )
                    with t2:
                        Tin_cold = st.slider(
                            "T entrée froid (°C)", 5, 70, 30,
                            help="Température d'entrée du fluide froid (5 à 70°C)."
                        )

                    f1, f2 = st.columns(2)
                    with f1:
                        q_hot = st.slider(
                            "Débit chaud (kg/s)", 5.0, 30.0, 15.0,
                            help="Débit massique du fluide chaud (5 à 30 kg/s)."
                        )
                    with f2:
                        q_cold = st.slider(
                            "Débit froid (kg/s)", 5.0, 30.0, 15.0,
                            help="Débit massique du fluide froid (5 à 30 kg/s)."
                        )

                    v1, v2 = st.columns(2)
                    with v1:
                        mu_hot = st.number_input(
                            "Viscosité chaud (cP)", 0.1, 10.0, 0.4,
                            help="Viscosité dynamique du fluide chaud (0.1 à 10 cP)."
                        )
                    with v2:
                        mu_cold = st.number_input(
                            "Viscosité froid (cP)", 0.1, 10.0, 0.9,
                            help="Viscosité dynamique du fluide froid (0.1 à 10 cP)."
                        )

                    solids = st.slider(
                        "Solides en suspension (ppm)", 0, 300, 50,
                        help="Concentration de solides en suspension (0 à 300 ppm)."
                    )

            submit = st.form_submit_button("🔍 Prédire")

        if submit:
            # Input validation example: warn if cleaning interval is very high
            if rtc > 5*365*24:
                st.warning("Attention : plus de 5 ans depuis le dernier nettoyage, risque élevé d'encrassement.")
            features = pd.DataFrame([[
                rtc, dTh, dTc, dp,
                Tin_hot, Tin_cold,
                q_hot, q_cold,
                mu_hot, mu_cold,
                solids
            ]], columns=[
                "runtime_since_cleaning_hr",
                "deltaT_hot_C", "deltaT_cold_C", "deltaP_shell_kPa",
                "hot_inlet_temp_C", "cold_inlet_temp_C",
                "hot_flow_kg_s", "cold_flow_kg_s",
                "hot_visc_cP", "cold_visc_cP",
                "solids_ppm"
            ])

            fouling = m_foul.predict(features)[0]
            ttc = max(m_ttc.predict(features)[0], 0)
            
            st.session_state.fouling_prediction = fouling
            st.session_state.ttc_prediction = ttc
            
            status = ("🟢 <b>OK</b>" if fouling < 0.60 else
                      "🟠 <b>Attention</b>" if fouling < 0.85 else
                      "🔴 <b>Critique</b>")
            ml_result_card(fouling, ttc, status)
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des modèles: {str(e)}")
        st.info("Assurez-vous que les fichiers model_fouling.pkl et model_ttc.pkl sont présents.") 