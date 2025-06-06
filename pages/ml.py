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

# Tailwind and FontAwesome for enhanced UI and helpful header
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        body, .stApp { background-color: #f9fafb; }
    </style>
    <div class="bg-gradient-to-r from-blue-600 to-teal-500 text-white p-4 rounded-lg mb-6 flex items-center justify-between">
        <div class="flex items-center">
            <i class="fas fa-thermometer-half text-2xl mr-2"></i>
            <h2 class="text-xl font-semibold">HX Fouling Dashboard</h2>
        </div>
        <a href="https://github.com" class="hover:text-gray-200"><i class="fab fa-github text-2xl"></i></a>
    </div>
    <div class="mt-4 mb-6 bg-blue-50 border-l-4 border-blue-500 p-4 flex items-center">
        <i class="fas fa-info-circle text-blue-500 text-2xl mr-3"></i>
        <p class="text-sm text-blue-800">
            Enter your operational data below to predict fouling buildup and cleaning schedule.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    """
    <div class="p-4">
        <h2 class="text-lg font-semibold mb-2"><i class="fas fa-question-circle mr-2"></i>Help</h2>
        <p class="text-sm text-gray-600">Fill in the form and click Predict to see fouling metrics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
    status_text = (
        "OK" if fouling < 0.60 else
        "Watch" if fouling < 0.85 else
        "Critical"
    )
    status_icon = (
        "fa-check-circle text-green-600" if fouling < 0.60 else
        "fa-exclamation-circle text-yellow-500" if fouling < 0.85 else
        "fa-skull-crossbones text-red-600"
    )

    st.markdown(
        f"""
        <div class="grid grid-cols-3 gap-4 mt-6">
            <div class="bg-white shadow rounded-lg p-4 text-center">
                <i class="fas fa-oil-can text-indigo-600 text-2xl mb-2"></i>
                <div class="text-xl font-bold">{fouling:.3f}</div>
                <div class="text-gray-500 text-sm">Fouling level</div>
            </div>
            <div class="bg-white shadow rounded-lg p-4 text-center">
                <i class="fas fa-clock text-indigo-600 text-2xl mb-2"></i>
                <div class="text-xl font-bold">{ttc:,.1f} h</div>
                <div class="text-gray-500 text-sm">Hours to cleaning</div>
            </div>
            <div class="bg-white shadow rounded-lg p-4 text-center">
                <i class="fas {status_icon} text-2xl mb-2"></i>
                <div class="text-xl font-bold">{status_text}</div>
                <div class="text-gray-500 text-sm">Status</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
