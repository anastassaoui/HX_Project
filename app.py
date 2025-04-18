import streamlit as st

st.set_page_config(page_title="Heat Exchanger Dashboard", page_icon="🔥", layout="wide")

# Load custom CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.markdown("# 👋 Welcome to the Heat Exchanger Interface")
st.markdown("Navigate through the sidebar to explore solver, CAD, and CFD modules.")

st.info(" the sidebar to switch between modules.")
