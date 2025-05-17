import streamlit as st
import pandas as pd
import joblib

m_foul = joblib.load("model_fouling.pkl")
m_ttc  = joblib.load("model_ttc.pkl")

FEATURES = [
    "runtime_since_cleaning_hr",
    "deltaT_hot_C", "deltaT_cold_C", "deltaP_shell_kPa",
    "hot_inlet_temp_C", "cold_inlet_temp_C",
    "hot_flow_kg_s", "cold_flow_kg_s",
    "hot_visc_cP", "cold_visc_cP",
    "solids_ppm",
]

st.set_page_config(page_title="HX Fouling Predictor", layout="wide")
st.title("Heat-Exchanger Fouling Prognostics")

with st.form("hx_form"):

    rtc = st.number_input("Hours since last cleaning", 0, 7*365*24, 100)
    a1, a2 = st.columns(2)
    with a1:
        # ── always-visible key KPI ───────────────────────────────────────────

        # ── expander: performance deltas & ΔP ────────────────────────────────
        with st.expander("📊 Performance readings", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                dTh = st.slider("ΔT hot (°C)", 0.0, 40.0, 18.0, 0.1)
            with c2:
                dTc = st.slider("ΔT cold (°C)", 0.0, 40.0, 16.0, 0.1)
            dp = st.slider("Shell ΔP (kPa)", 0.0, 150.0, 20.0, 0.1)
    with a2:
        # ── expander: operating conditions ───────────────────────────────────
        with st.expander("⚙️ Operating conditions", expanded=False):
            # temperatures & flows
            t1, t2 = st.columns(2)
            with t1: Tin_hot  = st.slider("Hot-inlet T (°C)", 80, 180, 140)
            with t2: Tin_cold = st.slider("Cold-inlet T (°C)", 5, 70, 30)

            f1, f2 = st.columns(2)
            with f1: q_hot  = st.slider("Hot flow (kg/s)",  5.0, 30.0, 15.0)
            with f2: q_cold = st.slider("Cold flow (kg/s)", 5.0, 30.0, 15.0)

            v1, v2 = st.columns(2)
            with v1: mu_hot  = st.number_input("Hot viscosity (cP)", 0.1, 10.0, 0.4)
            with v2: mu_cold = st.number_input("Cold viscosity (cP)", 0.1, 10.0, 0.9)

            solids = st.slider("Suspended solids (ppm)", 0, 300, 50)

    submitted = st.form_submit_button("🔍  Predict")

# ── inference ────────────────────────────────────────────────────────────
if submitted:
    df = pd.DataFrame([[
        rtc, dTh, dTc, dp,
        Tin_hot, Tin_cold,
        q_hot, q_cold,
        mu_hot, mu_cold,
        solids
    ]], columns=FEATURES)

    fouling = m_foul.predict(df)[0]
    ttc     = max(m_ttc.predict(df)[0], 0)
    p1,p2,p3 = st.columns(3)
    with p1:
        st.metric("Fouling level", f"{fouling:.3f}")
    with p2:
        st.metric("Hours to cleaning", f"{ttc:,.1f} h")
    with p3:
        status = ("🟢 **OK**"       if fouling < 0.60 else
              "🟠 **Watch**"    if fouling < 0.85 else
              "🔴 **Critical**")
        st.markdown(f"## {status}")
