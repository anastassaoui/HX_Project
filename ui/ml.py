import streamlit as st
import pandas as pd
import joblib

def fouling_prediction_section() -> None:
    st.subheader("🤖 Prédiction d'Encrassement")
    
    try:
        m_foul = joblib.load("model_fouling.pkl")
        m_ttc = joblib.load("model_ttc.pkl")
        
        with st.form("fouling_form"):
            rtc = st.number_input("Heures depuis dernier nettoyage", 0, 7*365*24, 100)
            a1, a2 = st.columns(2)
            
            with a1:
                with st.expander("📊 Mesures de performance", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        dTh = st.slider("ΔT côté chaud (°C)", 0.0, 40.0, 18.0, 0.1)
                    with c2:
                        dTc = st.slider("ΔT côté froid (°C)", 0.0, 40.0, 16.0, 0.1)
                    dp = st.slider("ΔP calandre (kPa)", 0.0, 150.0, 20.0, 0.1)
            
            with a2:
                with st.expander("⚙️ Conditions d'opération", expanded=False):
                    t1, t2 = st.columns(2)
                    with t1: Tin_hot = st.slider("T entrée chaud (°C)", 80, 180, 140)
                    with t2: Tin_cold = st.slider("T entrée froid (°C)", 5, 70, 30)

                    f1, f2 = st.columns(2)
                    with f1: q_hot = st.slider("Débit chaud (kg/s)", 5.0, 30.0, 15.0)
                    with f2: q_cold = st.slider("Débit froid (kg/s)", 5.0, 30.0, 15.0)

                    v1, v2 = st.columns(2)
                    with v1: mu_hot = st.number_input("Viscosité chaud (cP)", 0.1, 10.0, 0.4)
                    with v2: mu_cold = st.number_input("Viscosité froid (cP)", 0.1, 10.0, 0.9)

                    solids = st.slider("Solides en suspension (ppm)", 0, 300, 50)

            submit = st.form_submit_button("🔍 Prédire")

        if submit:
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
            
            p1, p2, p3 = st.columns(3)
            with p1:
                st.metric("Niveau d'encrassement", f"{fouling:.3f}")
            with p2:
                st.metric("Heures avant nettoyage", f"{ttc:,.1f} h")
            with p3:
                status = ("🟢 **OK**" if fouling < 0.60 else
                         "🟠 **Attention**" if fouling < 0.85 else
                         "🔴 **Critique**")
                st.markdown(f"## {status}")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des modèles: {str(e)}")
        st.info("Assurez-vous que les fichiers model_fouling.pkl et model_ttc.pkl sont présents.") 