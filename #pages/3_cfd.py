#import os, math
#from io import BytesIO
#from tempfile import NamedTemporaryFile
#
#import streamlit as st
#import numpy as np
#import plotly.graph_objects as go
#import matplotlib.pyplot as plt
#from PIL import Image
#from dotenv import load_dotenv
#from groq import Groq
#from fipy import Grid1D, CellVariable, DiffusionTerm, Grid2D, FaceVariable
#from fipy.viewers.matplotlibViewer import MatplotlibViewer as Viewer
#
## keep the inch conversion
#inch = 0.0254  # m
#
## set up Groq once
#load_dotenv()
#client = Groq(api_key=os.getenv("GROQ_API_KEY"))
#
#st.title("🔥  Échangeur Tubulaire — Calcul & Visualisation CFD")
#
#def plot_fipy_var(variable, title="FiPy 2D Contour", cmap="inferno"):
#    arr = variable.value
#    shape = variable.mesh.shape
#    fig, ax = plt.subplots(figsize=(6, 6))
#    im = ax.imshow(arr.reshape(shape), origin="lower", cmap=cmap)
#    ax.set_title(title)
#    plt.colorbar(im, ax=ax)
#    buf = BytesIO()
#    fig.tight_layout()
#    fig.savefig(buf, format="png", bbox_inches="tight")
#    plt.close(fig)
#    buf.seek(0)
#    return Image.open(buf)
#
## ───────────────────────── SINGLE FORM ───────────────────────── #
#with st.form(key="form_hxx"):
#    tabs = st.tabs([
#        "Géométrie",
#        "Fluide chaud",
#        "Fluide froid",
#        "Paroi & encrassement",
#        "Maillage",
#        "AI"
#    ])
#
#    # — GEOMETRIE —
#    with tabs[0]:
#        c1, c2 = st.columns(2)
#        with c1:
#            N_tube    = st.number_input("Nombre de tubes", 56)
#            L_tube_in = st.number_input("Longueur tubes [pouce]", 112.20, format="%.2f")
#            pitch_in  = st.number_input("Pas triangulaire [pouce]", 0.9375, format="%.4f")
#        with c2:
#            Do_in = st.number_input("Ø ext. tube [pouce]", 0.75, format="%.3f")
#            Di_in = st.number_input("Ø int. tube [pouce]", 0.584, format="%.3f")
#            Ds_in = st.number_input("Ø int. calandre [pouce]", 10.136, format="%.3f")
#
#    # — FLUIDE CHAUD —
#    with tabs[1]:
#        c1, c2 = st.columns(2)
#        with c1:
#            m_hot    = st.number_input("Débit chaud [lb/h]", 11023.1, format="%.1f")
#            Tin_hot  = st.number_input("T° entrée chaud [°F]", 206.33, format="%.2f")
#            Tout_hot = st.number_input("T° sortie chaud [°F]", 117.04, format="%.2f")
#        with c2:
#            cp_hot   = st.number_input("cᵖ chaud [BTU/(lb·°F)]", 0.624, format="%.4f")
#            mu_hot   = st.number_input("μ chaud [cP]", 4.83, format="%.3f")
#            k_hot    = st.number_input("k chaud [BTU/(ft·h·°F)]", 0.1495, format="%.4f")
#            rho_hot  = st.number_input("ρ chaud [lb/ft³]", 67.20, format="%.2f")
#
#    # — FLUIDE FROID —
#    with tabs[2]:
#        c1, c2 = st.columns(2)
#        with c1:
#            m_cold   = st.number_input("Débit froid [lb/h]", 26455.5, format="%.1f")
#            Tin_cold = st.number_input("T° entrée froid [°F]", -9.67, format="%.2f")
#        with c2:
#            cp_cold  = st.number_input("cᵖ froid [BTU/(lb·°F)]", 0.261, format="%.4f")
#            mu_cold  = st.number_input("μ froid [cP]", 0.276, format="%.3f")
#            k_cold   = st.number_input("k froid [BTU/(ft·h·°F)]", 0.0465, format="%.4f")
#            rho_cold = st.number_input("ρ froid [lb/ft³]", 86.4, format="%.2f")
#
#    # — PAROI & ENCRASSEMENT —
#    with tabs[3]:
#        k_wall = st.number_input("k métal tube [W/m·K]", 16.5, format="%.2f")
#        c1, c2 = st.columns(2)
#        with c1:
#            Rf_hot = st.number_input("Encrassement calandre [ft²·h·°F/BTU]", 0.0006, format="%.5f")
#        with c2:
#            Rf_cold = st.number_input("Encrassement tubes [ft²·h·°F/BTU]", 0.0006, format="%.5f")
#
#    # — MAILLAGE (1D + 2D) —
#    with tabs[4]:
#        c1, c2, c3, c4 = st.columns(4)
#        with c1:
#            nx   = st.slider("Cellules radiales (1D)", 10, 300, 60)
#        with c2:
#            nang = st.slider("Cellules angulaires (1D)", 4, 360, 90)
#        with c3:
#            nx2d = st.slider("Maillage X (2D)", 50, 400, 200)
#        with c4:
#            ny2d = st.slider("Maillage Y (2D)", 50, 400, 200)
#
#    # single submit button
#    run = st.form_submit_button("🚀 Calculer")
#
#    # AI tab
#    with tabs[5]:
#        if run:
#            with st.spinner("Talking to Groq..."):
#                prompt = open("cad_prompt.txt").read()
#                response = client.chat.completions.create(
#                    model="deepseek-r1-distill-llama-70b",
#                    messages=[{"role": "user", "content": prompt}],
#                    temperature=0.3,
#                    max_completion_tokens=4000,
#                    top_p=0.95,
#                    stream=True,
#                )
#
#                full_code = ""
#                for chunk in response:
#                    delta = chunk.choices[0].delta
#                    if getattr(delta, "content", None):
#                        full_code += delta.content
#
#                st.code(full_code, language="python")
#
#
## ───────────────────────── CALCULS & RESULTATS ───────────────────────── #
#if run:
#
#    # Géométrie & conversions
#    L_tube = L_tube_in * inch
#    Do, Di, Ds, pitch = [v * inch for v in (Do_in, Di_in, Ds_in, pitch_in)]
#    f2c    = lambda F: (F-32)*5/9
#    BTU2W  = lambda Q: Q*1055.06/3600
#    cp_SI  = lambda cp: cp*4186.8/778
#    k_SI   = lambda k: k*1.7307
#    mu_SI  = lambda mu: mu*0.001
#    rho_SI = lambda r: r*16.0185
#    μ_hot, μ_cold       = mu_SI(mu_hot), mu_SI(mu_cold)
#    ρ_hot, ρ_cold       = rho_SI(rho_hot), rho_SI(rho_cold)
#    k_hot_SI, k_cold_SI = k_SI(k_hot),    k_SI(k_cold)
#    cp_hot_SI, cp_cold_SI = cp_SI(cp_hot), cp_SI(cp_cold)
#
#    # Calculs filmique 1D
#    m_cold_kg_s = m_cold*0.4536/3600
#    v_cold      = m_cold_kg_s/(ρ_cold*np.pi*(Di/2)**2*N_tube)
#    Re_c        = ρ_cold*v_cold*Di/μ_cold
#    Pr_c        = cp_cold_SI*μ_cold/k_cold_SI
#    Nu_c        = 0.023*Re_c**0.8*Pr_c**0.4
#    h_i         = Nu_c*k_cold_SI/Di
#
#    m_hot_kg_s = m_hot*0.4536/3600
#    A_shell    = np.pi*(Ds/2)**2
#    v_shell    = m_hot_kg_s/(ρ_hot*A_shell)
#    De         = 4*(pitch**2 - np.pi*Do**2/4)/(np.pi*Do)
#    Re_s       = ρ_hot*v_shell*De/μ_hot
#    Pr_s       = cp_hot_SI*μ_hot/k_hot_SI
#    j_h        = 0.36*Re_s**-0.55
#    Nu_s       = j_h*Re_s*Pr_s**(1/3)
#    h_o        = Nu_s*k_hot_SI/De
#
#    R_conv_o = 1/h_o
#    R_conv_i = (Do/Di)/h_i
#    R_wall   = np.log(Do/Di)/(2*np.pi*k_wall*L_tube)
#    R_foul   = (Rf_hot+Rf_cold)/(0.3048**2)
#    Uo       = 1/(R_conv_o+R_conv_i+R_wall+R_foul)
#
#    Q_BTUh     = m_hot*cp_hot*(Tin_hot-Tout_hot)
#    T_cold_out = Tin_cold + Q_BTUh/(m_cold*cp_cold)
#
#
#
#
#
#
#
#
#
#
#    # ─────────────────── AFFICHAGE RÉSULTATS ─────────────────── #
#    # (this is inside your `if run:` block, after all conversions & calculs)
#
#    # Affichage des métriques (hors onglets)
#    c1, c2, c3 = st.columns(3)
#    c1.metric("U₀", f"{Uo:.1f} W/m²·K")
#    c2.metric("Q (BTU/h)", f"{Q_BTUh:,.0f}")
#    c3.metric("T° sortie froid", f"{T_cold_out:.2f} °F")
#    # Pré‑calcul pour radial (température + flux)
#    mesh1d = Grid1D(nx=nx, dx=(Do-Di)/2/nx)
#    T_r    = CellVariable(mesh=mesh1d, value=f2c(T_cold_out))
#    T_r.constrain(f2c(Tin_hot),    mesh1d.facesLeft)
#    T_r.constrain(f2c(T_cold_out), mesh1d.facesRight)
#    DiffusionTerm(coeff=k_wall).solve(var=T_r)
#
#    # radial coordinates (en m)
#    r_n = np.array(mesh1d.cellCenters[0] + Di/2)
#
#    # convert back to °F
#    T_n = np.array(T_r.value)*9/5 + 32
#
#    # flux radial
#    dTdr = np.gradient(T_n, r_n)
#    q_r  = -k_wall * dTdr
#
#    # ─────────────────── AFFICHAGE PROFILS 1D AVEC ONGLET SUPPLÉMENTAIRES ─────────────────── #
#    # maintenant 7 onglets au lieu de 3
#    tabs_profiles = st.tabs([
#        "Axial",
#        "Radial T(r)",
#        "Radial qʺ(r)",
#        "d²T/dz²"
#    ])
#    
#    # Préparation des données axiales
#    z         = np.linspace(0, L_tube, 30)
#    T_hot_z   = Tin_hot  - (Tin_hot  - Tout_hot)*(z/L_tube)
#    T_cold_z  = Tin_cold + (T_cold_out - Tin_cold)*(z/L_tube)
#    
#    # Gradient et seconde dérivée
#    dTdz_hot  = np.gradient(T_hot_z, z)
#    dTdz_cold = np.gradient(T_cold_z, z)
#    d2Tdz2_hot  = np.gradient(dTdz_hot, z)
#    d2Tdz2_cold = np.gradient(dTdz_cold, z)
#    
#    # Chaleur cumulée
#    Q_cumulée_hot  = m_hot*cp_hot*(Tin_hot  - T_hot_z)
#    Q_cumulée_cold = m_cold*cp_cold*(T_cold_out - T_cold_z)  # negative of cold if you like
#    
#    # Nusselt axial (utilisation des Nu globaux calculés plus haut)
#    Nu_hot_line  = np.full_like(z, Nu_s)
#    Nu_cold_line = np.full_like(z, Nu_c)
#
#    
#    
#    # Onglet 0 : profils axiaux
#    with tabs_profiles[0]:
#        # 1) Precompute static arrays
#        z       = np.linspace(0, L_tube, 30)
#        # these are your inlet→outlet linear profiles
#        T_hot_z = Tin_hot  - (Tin_hot  - Tout_hot)*(z/L_tube)
#        T_cold_z= Tin_cold + (T_cold_out - Tin_cold)*(z/L_tube)
#
#        # 2) Determine y‑axis bounds so color doesn’t jump around
#        allT = np.concatenate([T_hot_z, T_cold_z])
#        y_min, y_max = allT.min(), allT.max()
#
#        # 3) Build animation frames
#        n_frames = 60
#        alphas   = np.linspace(0, 1, n_frames)
#        frames   = []
#        for i, a in enumerate(alphas):
#            # interpolate each profile
#            Th = Tin_hot   - (Tin_hot   - Tout_hot)*(z/L_tube)*a
#            Tc = Tin_cold  + (T_cold_out - Tin_cold)*(z/L_tube)*a
#            frames.append(go.Frame(
#                data=[
#                    go.Scatter(x=z, y=Th, name="Chaude", mode="lines"),
#                    go.Scatter(x=z, y=Tc, name="Froide", mode="lines")
#                ],
#                name=str(i)
#            ))
#
#        # 4) Create the animated figure
#        fig_anim = go.Figure(
#            data=frames[0].data,
#            frames=frames
#        )
#
#        # 5) Add Play/Pause buttons and a slider
#        slider_steps = [
#            {
#                "args": [[f.name], 
#                         {"frame": {"duration": 100, "redraw": True},
#                          "mode": "immediate"}],
#                "label": f.name,
#                "method": "animate"
#            }
#            for f in frames
#        ]
#
#        fig_anim.update_layout(
#            title="Animation Profils Axiaux – T(z)",
#            xaxis_title="Longueur [m]",
#            yaxis_title="T [°F]",
#            yaxis=dict(range=[y_min, y_max]),
#            template="plotly_dark",
#            updatemenus=[{
#                "type": "buttons",
#                "showactive": False,
#                "x": 0.0, "y": 1.15,
#                "buttons": [
#                    {"label": "▶ Play",
#                     "method": "animate",
#                     "args": [None, {"frame": {"duration": 10, "redraw": True},
#                                     "fromcurrent": True}]},
#                    {"label": "■ Pause",
#                     "method": "animate",
#                     "args": [[None], {"frame": {"duration": 0, "redraw": False},
#                                       "mode": "immediate"}]}
#                ]
#            }],
#            sliders=[{
#                "active": 0,
#                "pad": {"t": 50},
#                "steps": slider_steps
#            }]
#        )
#    
#        # 6) Render the animated chart
#        st.plotly_chart(fig_anim, use_container_width=True)
#    
#    # Onglet 1 : température radiale
#    with tabs_profiles[1]:
#        fig_temp_r = go.Figure(go.Scatter(x=r_n, y=T_n, mode="lines"))
#        fig_temp_r.update_layout(
#            title="Profil radial de température",
#            xaxis_title="Rayon [m]",
#            yaxis_title="T [°F]",
#            template="plotly_dark"
#        )
#        st.plotly_chart(fig_temp_r, use_container_width=True)
#    
#    # Onglet 2 : flux radial
#    with tabs_profiles[2]:
#        fig_flux_r = go.Figure(go.Scatter(x=r_n, y=q_r, mode="lines"))
#        fig_flux_r.update_layout(
#            title="Flux radial qʺ(r)",
#            xaxis_title="Rayon [m]",
#            yaxis_title="Flux [W/m²]",
#            template="plotly_dark"
#        )
#        st.plotly_chart(fig_flux_r, use_container_width=True)
#    
#    # Onglet 4 : seconde dérivée d²T/dz²
#    with tabs_profiles[3]:
#        fig_dd = go.Figure()
#        fig_dd.add_trace(go.Scatter(x=z, y=d2Tdz2_hot,  name="d²T_hot/dz²"))
#        fig_dd.add_trace(go.Scatter(x=z, y=d2Tdz2_cold, name="d²T_cold/dz²"))
#        fig_dd.update_layout(
#            title="Seconde dérivée d²T/dz²",
#            xaxis_title="Longueur [m]",
#            yaxis_title="d²T/dz² [°F/m²]",
#            template="plotly_dark"
#        )
#        st.plotly_chart(fig_dd, use_container_width=True)
#
#
#    
#    
#
#
#    # Visualisations polaires
#    Zg   = np.tile(T_n[:, None], (1, nang))
#    Zq   = np.tile(np.abs(q_r)[:, None], (1, nang))
#    tabs = st.tabs(["T","Isothermes","|qʺ|","Surface 3D"])
#    with tabs[0]:
#        st.plotly_chart(go.Figure(go.Heatmap(z=Zg)), use_container_width=True)
#    with tabs[1]:
#        # Lock color scale
#        zmin, zmax = Tin_cold, Tin_hot
#
#        # Initial flat → final radial field
#        initial_Z = np.full_like(Zg, Tin_hot)
#        final_Z   = Zg
#
#        # Build interpolation frames
#        n_frames = 120
#        alphas   = np.linspace(0, 1, n_frames)
#        frames   = []
#        for i, a in enumerate(alphas):
#            Zf = initial_Z*(1-a) + final_Z*a
#            frames.append(go.Frame(
#                data=[go.Contour(
#                    z=Zf,
#                    colorscale="Viridis",
#                    zmin=zmin,
#                    zmax=zmax,
#                    contours=dict(showlabels=True),
#                    colorbar=dict(title="T [°F]")
#                )],
#                name=str(i)
#            ))
#
#        # Figure with first frame
#        fig = go.Figure(
#            data=frames[0].data,
#            frames=frames
#        )
#
#        # Slider steps
#        slider_steps = [{
#            "args": [[f.name], {"frame": {"duration": 80, "redraw": True}, "mode": "immediate"}],
#            "label": f.name,
#            "method": "animate"
#        } for f in frames]
#
#        # Layout with axis titles
#        fig.update_layout(
#            title="Animation Contour – Évolution radiale",
#            template="plotly_dark",
#            xaxis=dict(
#                title="Angle θ (cell index)",
#                showgrid=False
#            ),
#            yaxis=dict(
#                title="Rayon r (cell index)",
#                showgrid=False
#            ),
#            updatemenus=[{
#                "type": "buttons",
#                "x": 1.0, "y": 1.0,
#                "xanchor": "left", "yanchor": "top",
#                "buttons": [
#                    {"label": "▶ Play", "method": "animate",
#                     "args": [None, {"frame": {"duration": 80, "redraw": True}, "fromcurrent": True}]},
#                    {"label": "■ Pause", "method": "animate",
#                     "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
#                ]
#            }],
#            sliders=[{
#                "active": 0,
#                "pad": {"t": 40, "b": 10},
#                "len": 0.9,
#                "x": 0.05, "y": 1,
#                "xanchor": "left", "yanchor": "bottom",
#                "steps": slider_steps
#            }]
#        )
#
#        st.plotly_chart(fig, use_container_width=True)
#
#    with tabs[2]:
#        st.plotly_chart(go.Figure(go.Heatmap(z=Zq)), use_container_width=True)
#    with tabs[3]:
#        st.plotly_chart(go.Figure(go.Surface(z=Zg)), use_container_width=True)
#
#
#
#    # Simulation 2D – Cross‑section (toutes les vues en onglets)
#    dx2    = Ds / nx2d
#    dy2    = Ds / ny2d
#    mesh2d = Grid2D(nx=nx2d, ny=ny2d, dx=dx2, dy=dy2)
#    x2, y2 = mesh2d.cellCenters
#    ro, ri = Ds/2, Di/2
#    r2     = np.sqrt((x2-ro)**2 + (y2-ro)**2)
#    T2d    = CellVariable(name="T2D", mesh=mesh2d, value=f2c(T_cold_out))
#    tol    = min(dx2, dy2)/2
#    T2d.constrain(f2c(Tin_hot),    where=(r2 >= ro - tol))
#    T2d.constrain(f2c(T_cold_out), where=(r2 <= ri + tol))
#    DiffusionTerm(coeff=k_wall).solve(var=T2d)
#
#    # reshape pour affichage
#    T2d_C = T2d.value.reshape((ny2d, nx2d))       # en °C
#    Z2d   = T2d_C * 9/5 + 32                      # en °F
#    X2d   = x2.reshape((ny2d, nx2d))
#    Y2d   = y2.reshape((ny2d, nx2d))
#
#    RE_field = np.where(r2 <= ri, Re_c, Re_s).reshape((ny2d, nx2d))
#    PR_field = np.where(r2 <= ri, Pr_c, Pr_s).reshape((ny2d, nx2d))
#
#    # compute global min/max for a smooth colorbar
#    re_min, re_max = float(np.nanmin(RE_field)), float(np.nanmax(RE_field))
#    pr_min, pr_max = float(np.nanmin(PR_field)), float(np.nanmax(PR_field))
#
#    tab2d = st.tabs([
#        "Heatmap", "Isothermes", "Flux vect.", "Surf 3D", "Scatter 3D,"
#    ])
#
#    # 1) Heatmap
#    with tab2d[0]:
#        fig_hm = go.Figure(go.Heatmap(z=Z2d, colorscale="Viridis"))
#        fig_hm.update_layout(title="Heatmap 2D", template="plotly_dark", height=900)
#        st.plotly_chart(fig_hm, use_container_width=True)
#
#    # 2) Isothermes
#    with tab2d[1]:
#        fig_iso = go.Figure(go.Contour(
#            z=Z2d,
#            colorscale="Viridis",
#            contours=dict(showlabels=True, coloring="lines"),
#            colorbar=dict(title="T [°F]")
#        ))
#        fig_iso.update_layout(title="Isothermes 2D", template="plotly_dark", height=900,
#                              xaxis=dict(visible=False), yaxis=dict(visible=False))
#        st.plotly_chart(fig_iso, use_container_width=True)
#
#    # 3) Champ de flux thermique
#    with tab2d[2]:
#        dTdy, dTdx = np.gradient(T2d_C, dy2, dx2)
#        qx2 = -k_wall * dTdx
#        qy2 = -k_wall * dTdy
#        fig_q = go.Figure()
#        skip = max(1, min(ny2d, nx2d)//20)
#        for i in range(0, ny2d, skip):
#            for j in range(0, nx2d, skip):
#                fig_q.add_trace(go.Scatter(
#                    x=[X2d[i,j], X2d[i,j] + qx2[i,j]*0.001],
#                    y=[Y2d[i,j], Y2d[i,j] + qy2[i,j]*0.001],
#                    mode="lines", line=dict(color="cyan", width=1),
#                    showlegend=False
#                ))
#        fig_q.update_layout(title="Flux thermique 2D", template="plotly_dark", height=900,
#                            xaxis=dict(visible=False), yaxis=dict(visible=False))
#        st.plotly_chart(fig_q, use_container_width=True)
#
#    # 4) Surface 3D
#    with tab2d[3]:
#        fig_surf = go.Figure(go.Surface(
#            z=Z2d, x=X2d, y=Y2d, colorscale="Viridis",
#            colorbar=dict(title="T [°F]")
#        ))
#        fig_surf.update_layout(title="Surface 3D – Température", template="plotly_dark", height=800,
#                               scene=dict(xaxis=dict(visible=False),
#                                          yaxis=dict(visible=False),
#                                          zaxis=dict(title="T [°F]")))
#        st.plotly_chart(fig_surf, use_container_width=True)
#
#    # 5) Scatter 3D
#    with tab2d[4]:
#        fig_sc3d = go.Figure(go.Scatter3d(
#            x=X2d.flatten(), y=Y2d.flatten(), z=Z2d.flatten(),
#            mode="markers", marker=dict(
#                size=2, color=Z2d.flatten(), colorscale="Viridis",
#                colorbar=dict(title="T [°F]")
#            )
#        ))
#        fig_sc3d.update_layout(title="Scatter 3D – Température", template="plotly_dark", height=800,
#                               scene=dict(xaxis=dict(visible=False),
#                                          yaxis=dict(visible=False),
#                                          zaxis=dict(title="T [°F]")))
#        st.plotly_chart(fig_sc3d, use_container_width=True)
#
#
#    
#
#else:
#   st.info("Définissez vos paramètres puis cliquez sur « Lancer le calcul ».")
#