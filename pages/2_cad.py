import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


st.set_page_config(page_title="CAD Generator", layout="wide")
st.title("🧱 CAD: Auto-generate BEP Shell & Tube Heat Exchanger")

# Set up Groq
client = Groq()

st.markdown("Click the button below to generate the FreeCAD script based on preset parameters.")

if st.button("🚀 Generate FreeCAD Script"):
    with st.spinner("Talking to Groq..."):
        prompt = open("cad_prompt.txt").read()  # Store that long prompt separately

        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_completion_tokens=4000,
            top_p=0.95,
            stream=True,
        )

        full_code = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                full_code += content

        st.code(full_code, language="python")

        st.download_button("💾 Download Script", full_code, file_name="heat_exchanger_model.py")

