import streamlit as st
import numpy as np
import pandas as pd

def show_metric(label: str, value: float, unit: str = "") -> None:
    formatted = f"{value:.5f} {unit}" if unit else f"{value:.5f}"
    st.markdown(
        f"""
        <div style="border: 1px solid #333; padding: 10px; background: #f0f0f0; text-align: center; border-radius: 5px;">
            <h3>{label}</h3>
            <p>{formatted}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def effectiveness_chart(func, R1: float, **kwargs) -> None:
    NTU_range = np.linspace(0.1, 10.0, 50)
    effs = [func(R1, NTU, **kwargs) for NTU in NTU_range]
    df = pd.DataFrame({"NTU": NTU_range, "Effectiveness": effs}).set_index("NTU")
    st.line_chart(df) 