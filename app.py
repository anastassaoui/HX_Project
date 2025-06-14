import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import joblib
import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv
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


from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Load environment variables
load_dotenv()

# Authentication functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

def login_user(username, password):
    # In production, this should be replaced with a secure database
    # For now, we'll use environment variables
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH', make_hashes('admin'))
    
    if username == admin_username and check_hashes(password, admin_password_hash):
        return True
    return False

def init_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def init_session_state() -> None:
    """Initialize all session state variables with default values."""
    # Geometry section variables
    if "DB_Perry" not in st.session_state:
        st.session_state.DB_Perry = None
    if "N_Perry" not in st.session_state:
        st.session_state.N_Perry = None
    if "DB_HEDH" not in st.session_state:
        st.session_state.DB_HEDH = None
    if "DB_Phadkeb" not in st.session_state:
        st.session_state.DB_Phadkeb = None
    if "DB_VDI" not in st.session_state:
        st.session_state.DB_VDI = None
    if "DShell_min" not in st.session_state:
        st.session_state.DShell_min = None
    if "clearance_auto" not in st.session_state:
        st.session_state.clearance_auto = None
    if "dB_hole" not in st.session_state:
        st.session_state.dB_hole = None
    if "L_max" not in st.session_state:
        st.session_state.L_max = None
    
    # Input variables
    if "inputs_geometry" not in st.session_state:
        st.session_state.inputs_geometry = None
    if "inputs_pntu" not in st.session_state:
        st.session_state.inputs_pntu = None
    
    # Clearance section variables
    if "clearance_result" not in st.session_state:
        st.session_state.clearance_result = None
    
    # ML prediction variables
    if "fouling_prediction" not in st.session_state:
        st.session_state.fouling_prediction = None
    if "ttc_prediction" not in st.session_state:
        st.session_state.ttc_prediction = None

def login():
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("## 🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password")
        st.markdown('</div>', unsafe_allow_html=True)

# Initialize authentication
init_auth()

# Main app
if not st.session_state.authenticated:
    login()
else:
    # Initialize session state variables
    init_session_state()
    
    # Your existing app code starts here
    st.set_page_config(page_title="Suite de Conception d'Échangeur de Chaleur", layout="wide")
    st.title("🧪 Suite d'Ingénierie : Échangeur Tubulaire à Calandre")
    
    # Add logout button in sidebar
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
        
        run_all = st.button("🚀 Calculer tout")
        selection = option_menu(
            "Navigation",
            ["Géométrie", "Jeu Calandre", "Efficacité", "Prédiction ML", "Résumé"],
            icons=["rulers", "arrows-angle-contract", "graph-up", "robot", "card-list"],
            menu_icon="cast",
            default_index=0,
        )

    # ---------------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------------

    def show_metric(label: str, value: float, unit: str = "") -> None:
        """Display a numeric value using Streamlit metric."""
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
        """Plot effectiveness versus NTU for a given correlation."""
        NTU_range = np.linspace(0.1, 10.0, 50)
        effs = [func(R1, NTU, **kwargs) for NTU in NTU_range]
        df = pd.DataFrame({"NTU": NTU_range, "Effectiveness": effs}).set_index("NTU")
        st.line_chart(df)


    # ---------------------------------------------------------------------------
    # UI sections
    # ---------------------------------------------------------------------------

    def geometry_section(run_all: bool) -> None:
        st.subheader("📐 Calculs de Géométrie")
        col_input, col_result = st.columns([2, 1])
        with col_input:
            with st.form("geom_form"):
                r1c1, r1c2, r1c3 = st.columns(3)
                Do = r1c1.number_input("Ø extérieur [m]", 0.005, 0.1, 0.025)
                pitch = r1c2.number_input("Pas triangulaire [m]", 0.01, 0.1, 0.03125)
                angle = r1c3.selectbox("Angle [°]", [30, 45, 60, 90], index=0)

                r2c1, r2c2, r2c3 = st.columns(3)
                Ntp = r2c1.selectbox("Passes tubes", [1, 2], index=1)
                N = r2c2.slider("Nombre de tubes", 1, 2000, 928)
                L_unsupported = r2c3.number_input("Longueur non supportée [m]", 0.1, 10.0, 0.75)

                material = st.selectbox("Matériau du tube", ["CS", "aluminium"])
                submit = st.form_submit_button("Calculer géométrie")

            run = submit or run_all
            if run:
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
        with col_result:
            if st.session_state.DB_Perry is not None:
                st.markdown("### Résultats")
                show_metric("Faisceau Perry", st.session_state.DB_Perry, "m")
                show_metric("Tubes Perry", st.session_state.N_Perry)
                show_metric("HEDH", st.session_state.DB_HEDH, "m")
                show_metric("Phadkeb", st.session_state.DB_Phadkeb, "m")
                show_metric("VDI", st.session_state.DB_VDI, "m")
                show_metric("DShell_min", st.session_state.DShell_min, "m")
                show_metric("Clearance auto", st.session_state.clearance_auto, "m")
                show_metric("Ø trou chicane", st.session_state.dB_hole, "m")
                show_metric("L_max sans support", st.session_state.L_max, "m")


    def clearance_section(run_all: bool) -> None:
        st.subheader("📏 Jeu Calandre-Faisceau")
        input_col, out_col = st.columns(2)
        with input_col:
            with st.form("clearance_form"):
                mode = st.radio("Basé sur", ["Diamètre faisceau", "Diamètre calandre"], horizontal=True)
                db = ds = None
                if mode == "Diamètre faisceau":
                    db_default = st.session_state.DB_Perry if st.session_state.DB_Perry is not None else 1.2
                    db = st.slider("Diamètre du faisceau [m]", 0.1, 3.0, db_default)
                else:
                    ds = st.slider("Diamètre de la calandre [m]", 0.1, 3.0, 1.25)
                submit = st.form_submit_button("Calculer jeu")
            run = submit or run_all
            if run:
                result = shell_clearance(DBundle=db) if db else shell_clearance(DShell=ds)
                st.session_state.clearance_result = result
        with out_col:
            if st.session_state.clearance_result is not None:
                show_metric("Jeu recommandé", st.session_state.clearance_result, "m")


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


    def generate_pdf_report():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        section_style = styles['Heading2']
        normal_style = styles['Normal']

        # Title
        elements.append(Paragraph("Résumé de l'Échangeur de Chaleur", title_style))
        elements.append(Spacer(1, 12))

        # Geometry Section
        g = st.session_state.get("inputs_geometry")
        if g:
            elements.append(Paragraph("Section Géométrie", section_style))
            geo_data = [["Paramètre", "Valeur"]]
            for k, v in g.items():
                geo_data.append([str(k), str(v)])
            geo_data += [
                ["DB_Perry", str(st.session_state.get('DB_Perry'))],
                ["N_Perry", str(st.session_state.get('N_Perry'))],
                ["DB_HEDH", str(st.session_state.get('DB_HEDH'))],
                ["DB_Phadkeb", str(st.session_state.get('DB_Phadkeb'))],
                ["DB_VDI", str(st.session_state.get('DB_VDI'))],
                ["DShell_min", str(st.session_state.get('DShell_min'))],
                ["Clearance auto", str(st.session_state.get('clearance_auto'))],
                ["Ø trou chicane", str(st.session_state.get('dB_hole'))],
                ["L_max sans support", str(st.session_state.get('L_max'))],
            ]
            geo_table = Table(geo_data, hAlign='LEFT')
            geo_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            elements.append(geo_table)
            elements.append(Spacer(1, 12))

        # Clearance Section
        if st.session_state.get("clearance_result") is not None:
            elements.append(Paragraph("Section Jeu Calandre-Faisceau", section_style))
            clearance_data = [["Paramètre", "Valeur"], ["Jeu recommandé", str(st.session_state.get('clearance_result'))]]
            clearance_table = Table(clearance_data, hAlign='LEFT')
            clearance_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            elements.append(clearance_table)
            elements.append(Spacer(1, 12))

        # Effectiveness Section
        p = st.session_state.get("inputs_pntu")
        if p:
            elements.append(Paragraph("Section Efficacité", section_style))
            eff_data = [["Paramètre", "Valeur"]]
            for k, v in p.items():
                eff_data.append([str(k), str(v)])
            eff_table = Table(eff_data, hAlign='LEFT')
            eff_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            elements.append(eff_table)
            elements.append(Spacer(1, 12))

        # ML Prediction Section
        if st.session_state.get("fouling_prediction") is not None or st.session_state.get("ttc_prediction") is not None:
            elements.append(Paragraph("Section Prédiction ML", section_style))
            ml_data = [["Paramètre", "Valeur"]]
            if st.session_state.get("fouling_prediction") is not None:
                ml_data.append(["Niveau d'encrassement", str(st.session_state.get('fouling_prediction'))])
            if st.session_state.get("ttc_prediction") is not None:
                ml_data.append(["Heures avant nettoyage", str(st.session_state.get('ttc_prediction'))])
            ml_table = Table(ml_data, hAlign='LEFT')
            ml_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            elements.append(ml_table)
            elements.append(Spacer(1, 12))

        doc.build(elements)
        buffer.seek(0)
        return buffer


    def summary_section(run_all: bool) -> None:
        st.subheader("🧾 Résumé Complet")
        if run_all and st.session_state.inputs_geometry is not None and st.session_state.inputs_pntu is not None:
            g = st.session_state.inputs_geometry
            p = st.session_state.inputs_pntu
            
            # Convert all values to strings to avoid serialization issues
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
                    str(g["Do"]), str(g["pitch"]), str(g["angle"]), str(g["Ntp"]), 
                    str(g["N"]), str(g["material"]), str(g["L_unsupported"]),
                    str(st.session_state.DB_Perry), str(st.session_state.N_Perry), 
                    str(st.session_state.DB_HEDH), str(st.session_state.DB_Phadkeb), 
                    str(st.session_state.DB_VDI), str(st.session_state.DShell_min),
                    str(st.session_state.clearance_auto), str(st.session_state.dB_hole), 
                    str(st.session_state.L_max), str(p["m1"]), str(p["Cp1"]), 
                    str(p["T1i"]), str(p["m2"]), str(p["Cp2"]), str(p["T2i"]), 
                    str(p["UA"]), str(p["subtype"]), str(p["Ntp"]),
                ],
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.markdown("""
            <br/>
            <b>Générez un rapport PDF de ce résumé :</b>
            """, unsafe_allow_html=True)
            pdf_buffer = generate_pdf_report()
            st.download_button(
                label="📄 Télécharger le PDF du Résumé",
                data=pdf_buffer,
                file_name="resume_echangeur.pdf",
                mime="application/pdf"
            )
        else:
            st.info("Cliquez sur 'Calculer tout' pour générer le résumé complet.")


    # ---------------------------------------------------------------------------
    # ML Prediction Section
    # ---------------------------------------------------------------------------

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


    # ---------------------------------------------------------------------------
    # Application entry point
    # ---------------------------------------------------------------------------

    if selection == "Géométrie":
        geometry_section(run_all)
    elif selection == "Jeu Calandre":
        clearance_section(run_all)
    elif selection == "Efficacité":
        effectiveness_section(run_all)
    elif selection == "Prédiction ML":
        fouling_prediction_section()
    elif selection == "Résumé":
        summary_section(run_all)
