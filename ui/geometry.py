import streamlit as st
from utils.helpers import show_metric
from ht.hx import size_bundle_from_tubecount, Ntubes, DBundle_for_Ntubes_HEDH, DBundle_for_Ntubes_Phadkeb, D_for_Ntubes_VDI, DBundle_min, shell_clearance, D_baffle_holes, L_unsupported_max

def geometry_section(run_all: bool) -> None:
    st.subheader(" Calculs de Géométrie")
    # Only input columns at the top
    col_input = st.columns([1])[0]
    with col_input:
        with st.form("geom_form"):
            r1c1, r1c2, r1c3 = st.columns(3)
            Do = r1c1.number_input(
                "Ø extérieur [m]",
                0.005, 0.1, 0.025,
                help="Diamètre extérieur du tube (généralement entre 5 mm et 100 mm)."
            )
            pitch = r1c2.number_input(
                "Pas triangulaire [m]",
                0.01, 0.1, 0.03125,
                help="Distance entre les centres de deux tubes adjacents. Typiquement 1.25 × Ø extérieur."
            )
            angle = r1c3.selectbox(
                "Angle [°]",
                [30, 45, 60, 90],
                index=0,
                help="Angle du motif de disposition des tubes (30°/45°/60° pour triangle, 90° pour carré)."
            )

            r2c1, r2c2, r2c3 = st.columns(3)
            Ntp = r2c1.selectbox(
                "Passes tubes",
                [1, 2],
                index=1,
                help="Nombre de passes côté tubes (1 ou 2)."
            )
            N = r2c2.slider(
                "Nombre de tubes",
                1, 2000, 928,
                help="Nombre total de tubes dans le faisceau."
            )
            L_unsupported = r2c3.number_input(
                "Longueur non supportée [m]",
                0.1, 10.0, 0.75,
                help="Longueur de tube entre supports (baffles). Trop long augmente le risque de vibration."
            )

            material = st.selectbox(
                "Matériau du tube",
                ["CS", "aluminium"],
                help="Matériau utilisé pour les tubes."
            )
            submit = st.form_submit_button("Calculer géométrie")

    run = submit or run_all
    error = None
    # --- Input validation ---
    if run:
        if pitch <= Do:
            error = "Le pas triangulaire doit être supérieur au diamètre extérieur du tube."
        if L_unsupported < 0.1 or L_unsupported > 10.0:
            error = "La longueur non supportée doit être comprise entre 0.1 m et 10 m."
        if N < 1:
            error = "Le nombre de tubes doit être au moins 1."
        if error:
            st.error(error)
        else:
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
    # Results card now below the input form, full width and horizontal
    if st.session_state.get("DB_Perry"):
        st.markdown("""
        <style>
        .geom-card {{
            background: linear-gradient(120deg, #f0f2f6 60%, #e0e7ff 100%);
            border-radius: 16px;
            padding: 1.5em 1em 1em 1em;
            box-shadow: 0 2px 8px rgba(80,80,120,0.07);
            margin-bottom: 1em;
            margin-top: 2em;
            width: 100%;
            overflow-x: auto;
        }}
        .geom-metric-row {{
            display: flex;
            flex-direction: row;
            gap: 2em;
            flex-wrap: nowrap;
            overflow-x: auto;
        }}
        .geom-metric {{
            min-width: 140px;
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 0.5em;
        }}
        .geom-label {{
            color: #4b4b6b;
            font-weight: 700;
        }}
        .geom-value {{
            color: #ff4b4b;
            font-size: 1.2em;
            font-weight: 700;
        }}
        </style>
        <div class="geom-card">
        <h4 style="margin-bottom:1em;">✨ <b>Résultats Géométrie</b></h4>
        <div class="geom-metric-row">
            <div class="geom-metric"><span class="geom-label">Faisceau Perry</span><br><span class="geom-value">{:.3f} m</span></div>
            <div class="geom-metric"><span class="geom-label">Tubes Perry</span><br><span class="geom-value">{}</span></div>
            <div class="geom-metric"><span class="geom-label">HEDH</span><br><span class="geom-value">{:.3f} m</span></div>
            <div class="geom-metric"><span class="geom-label">Phadkeb</span><br><span class="geom-value">{:.3f} m</span></div>
            <div class="geom-metric"><span class="geom-label">VDI</span><br><span class="geom-value">{:.3f} m</span></div>
            <div class="geom-metric"><span class="geom-label">DShell min</span><br><span class="geom-value">{:.3f} m</span></div>
            <div class="geom-metric"><span class="geom-label">Clearance auto</span><br><span class="geom-value">{:.3f} m</span></div>
            <div class="geom-metric"><span class="geom-label">Ø trou chicane</span><br><span class="geom-value">{:.3f} m</span></div>
            <div class="geom-metric"><span class="geom-label">L_max sans support</span><br><span class="geom-value">{:.3f} m</span></div>
        </div>
        </div>
        """.format(
            st.session_state.DB_Perry,
            st.session_state.N_Perry,
            st.session_state.DB_HEDH,
            st.session_state.DB_Phadkeb,
            st.session_state.DB_VDI,
            st.session_state.DShell_min,
            st.session_state.clearance_auto,
            st.session_state.dB_hole,
            st.session_state.L_max
        ), unsafe_allow_html=True) 