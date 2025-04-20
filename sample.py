import os
import math
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from fipy import Grid1D, Grid2D, CellVariable, DiffusionTerm

# ───────────────────────── APP CONFIG ───────────────────────── #
os.environ["FIPY_COMM"] = "serial"
st.set_page_config(page_title="Échangeur tubulaire – CFD", layout="wide")
st.title("🔥  Échangeur Tubulaire — Calcul & Visualisation CFD")

inch = 0.0254  # m

# ───────────────────────── INPUT FORM ───────────────────────── #
with st.form(key="form_hxx"):
    tabs = st.tabs(["Géométrie", "Fluide chaud", "Fluide froid", "Paroi & encrassement", "Maillage"])
    # Géométrie
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            N_tube    = st.number_input("Nombre de tubes", 56)
            L_tube_in = st.number_input("Longueur tubes [pouce]", 112.20, format="%.2f")
            pitch_in  = st.number_input("Pas triangulaire [pouce]", 0.9375, format="%.4f")
        with c2:
            Do_in = st.number_input("Ø ext. tube [pouce]", 0.75, format="%.3f")
            Di_in = st.number_input("Ø int. tube [pouce]", 0.584, format="%.3f")
            Ds_in = st.number_input("Ø int. calandre [pouce]", 10.136, format="%.3f")
    # Fluide chaud
    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            m_hot    = st.number_input("Débit chaud [lb/h]", 11023.1, format="%.1f")
            Tin_hot  = st.number_input("T° entrée chaud [°F]", 206.33, format="%.2f")
            Tout_hot = st.number_input("T° sortie chaud [°F]", 117.04, format="%.2f")
        with c2:
            cp_hot   = st.number_input("cᵖ chaud [BTU/(lb·°F)]", 0.624, format="%.4f")
            mu_hot   = st.number_input("μ chaud [cP]", 4.83, format="%.3f")
            k_hot    = st.number_input("k chaud [BTU/(ft·h·°F)]", 0.1495, format="%.4f")
            rho_hot  = st.number_input("ρ chaud [lb/ft³]", 67.20, format="%.2f")
    # Fluide froid
    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            m_cold   = st.number_input("Débit froid [lb/h]", 26455.5, format="%.1f")
            Tin_cold = st.number_input("T° entrée froid [°F]", -9.67, format="%.2f")
        with c2:
            cp_cold  = st.number_input("cᵖ froid [BTU/(lb·°F)]", 0.261, format="%.4f")
            mu_cold  = st.number_input("μ froid [cP]", 0.276, format="%.3f")
            k_cold   = st.number_input("k froid [BTU/(ft·h·°F)]", 0.0465, format="%.4f")
            rho_cold = st.number_input("ρ froid [lb/ft³]", 86.4, format="%.2f")
    # Paroi & encrassement
    with tabs[3]:
        k_wall = st.number_input("k métal tube [W/m·K]", 16.5, format="%.2f")
        c1, c2 = st.columns(2)
        with c1:
            Rf_hot = st.number_input("Encrassement calandre [ft²·h·°F/BTU]", 0.0006, format="%.5f")
        with c2:
            Rf_cold = st.number_input("Encrassement tubes [ft²·h·°F/BTU]", 0.0006, format="%.5f")
    # Maillage
    with tabs[4]:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            nx   = st.slider("Cellules radiales (1D)", 10, 300, 60)
        with c2:
            nang = st.slider("Cellules angulaires (1D)", 4, 360, 90)
        with c3:
            nx2d = st.slider("Maillage X (2D)", 50, 400, 200)
        with c4:
            ny2d = st.slider("Maillage Y (2D)", 50, 400, 200)
    run = st.form_submit_button("🚀 Calculer")

# ───────────────────────── CALCULS & VISUALISATIONS ───────────────────────── #
if run:
    # Conversions & définitions
    L_tube = L_tube_in * inch
    Do, Di, Ds, pitch = [v * inch for v in (Do_in, Di_in, Ds_in, pitch_in)]
    f2c    = lambda F: (F-32)*5/9
    cp_SI  = lambda cp: cp*4186.8/778
    k_SI   = lambda k: k*1.7307
    mu_SI  = lambda mu: mu*0.001
    rho_SI = lambda r: r*16.0185

    μ_hot, μ_cold       = mu_SI(mu_hot), mu_SI(mu_cold)
    ρ_hot, ρ_cold       = rho_SI(rho_hot), rho_SI(rho_cold)
    k_hot_SI, k_cold_SI = k_SI(k_hot),    k_SI(k_cold)
    cp_hot_SI, cp_cold_SI = cp_SI(cp_hot), cp_SI(cp_cold)

    # Film coefficients (1D)
    m_cold_kg_s = m_cold*0.4536/3600
    v_cold      = m_cold_kg_s/(ρ_cold*np.pi*(Di/2)**2*N_tube)
    Re_c        = ρ_cold*v_cold*Di/μ_cold
    Pr_c        = cp_cold_SI*μ_cold/k_cold_SI
    Nu_c        = 0.023*Re_c**0.8*Pr_c**0.4
    h_i         = Nu_c*k_cold_SI/Di

    m_hot_kg_s = m_hot*0.4536/3600
    A_shell    = np.pi*(Ds/2)**2
    v_shell    = m_hot_kg_s/(ρ_hot*A_shell)
    De         = 4*(pitch**2 - np.pi*Do**2/4)/(np.pi*Do)
    Re_s       = ρ_hot*v_shell*De/μ_hot
    Pr_s       = cp_hot_SI*μ_hot/k_hot_SI
    j_h        = 0.36*Re_s**-0.55
    Nu_s       = j_h*Re_s*Pr_s**(1/3)
    h_o        = Nu_s*k_hot_SI/De

    R_conv_o = 1/h_o
    R_conv_i = (Do/Di)/h_i
    R_wall   = np.log(Do/Di)/(2*np.pi*k_wall*L_tube)
    R_foul   = (Rf_hot+Rf_cold)/(0.3048**2)
    Uo       = 1/(R_conv_o+R_conv_i+R_wall+R_foul)

    Q_BTUh     = m_hot*cp_hot*(Tin_hot-Tout_hot)
    T_cold_out = Tin_cold + Q_BTUh/(m_cold*cp_cold)

    # Affichage métriques
    c1, c2, c3 = st.columns(3)
    c1.metric("U₀", f"{Uo:.1f} W/m²·K")
    c2.metric("Q (BTU/h)", f"{Q_BTUh:,.0f}")
    c3.metric("T° sortie froid", f"{T_cold_out:.2f} °F")

    # ── Profils 1D ── #
    tabs_profiles = st.tabs([
        "Axial",
        "Radial T(r)",
        "Radial qʺ(r)",
    ])
    # Axial T(z)
    with tabs_profiles[0]:
        z        = np.linspace(0, L_tube, 30)
        T_hot_z  = Tin_hot  - (Tin_hot  - Tout_hot)*(z/L_tube)
        T_cold_z = Tin_cold + (T_cold_out - Tin_cold)*(z/L_tube)
        fig_ax = go.Figure()
        fig_ax.add_trace(go.Scatter(x=z, y=T_hot_z, name="Chaude"))
        fig_ax.add_trace(go.Scatter(x=z, y=T_cold_z, name="Froide"))
        fig_ax.update_layout(
            title="Profils axiaux",
            xaxis_title="Longueur [m]",
            yaxis_title="T [°F]",
            template="plotly_dark"
        )
        st.plotly_chart(fig_ax, use_container_width=True)

    # Pré‑calc radial
    mesh1d = Grid1D(nx=nx, dx=(Do-Di)/2/nx)
    T_r    = CellVariable(mesh=mesh1d, value=f2c(T_cold_out))
    T_r.constrain(f2c(Tin_hot),    mesh1d.facesLeft)
    T_r.constrain(f2c(T_cold_out), mesh1d.facesRight)
    DiffusionTerm(coeff=k_wall).solve(var=T_r)
    r_n = np.array(mesh1d.cellCenters[0] + Di/2)
    T_n = np.array(T_r.value)*9/5 + 32
    dTdr = np.gradient(T_n, r_n)
    q_r  = -k_wall * dTdr

    # Radial T(r)
    with tabs_profiles[1]:
        fig_temp_r = go.Figure(go.Scatter(x=r_n, y=T_n, mode="lines"))
        fig_temp_r.update_layout(
            title="Profil radial de température",
            xaxis_title="Rayon [m]",
            yaxis_title="T [°F]",
            template="plotly_dark"
        )
        st.plotly_chart(fig_temp_r, use_container_width=True)

    # Radial qʺ(r)
    with tabs_profiles[2]:
        fig_flux_r = go.Figure(go.Scatter(x=r_n, y=q_r, mode="lines"))
        fig_flux_r.update_layout(
            title="Flux radial qʺ(r)",
            xaxis_title="Rayon [m]",
            yaxis_title="Flux [W/m²]",
            template="plotly_dark"
        )
        st.plotly_chart(fig_flux_r, use_container_width=True)

    # ── Visualisations polaires & 2D ── #
    Zg = np.tile(T_n[:, None], (1, nang))
    Zq = np.tile(np.abs(q_r)[:, None], (1, nang))
    tabs2 = st.tabs(["T", "Isothermes", "Vecteurs", "|qʺ|", "Surface 3D"])
    with tabs2[0]:
        st.plotly_chart(go.Figure(go.Heatmap(z=Zg)), use_container_width=True)
    with tabs2[1]:
        st.plotly_chart(go.Figure(go.Contour(z=Zg)), use_container_width=True)
    with tabs2[2]:
        fig_vec = go.Figure()
        step = max(1, nx//25)
        for i in range(0, len(r_n), step):
            fig_vec.add_trace(go.Scatter(
                x=[0, r_n[i] + q_r[i]*0.004],
                y=[0, 0],
                mode="lines"
            ))
        fig_vec.update_layout(title="Vecteurs qʺ", template="plotly_dark")
        st.plotly_chart(fig_vec, use_container_width=True)
    with tabs2[3]:
        st.plotly_chart(go.Figure(go.Heatmap(z=Zq)), use_container_width=True)
    with tabs2[4]:
        st.plotly_chart(go.Figure(go.Surface(z=Zg)), use_container_width=True)

    # ── Simulation 2D – Cross‑section ── #
    dx2  = Ds / nx2d
    dy2  = Ds / ny2d
    mesh2d = Grid2D(nx=nx2d, ny=ny2d, dx=dx2, dy=dy2)
    x2, y2 = mesh2d.cellCenters
    ro, ri = Ds/2, Di/2
    r2     = np.sqrt((x2-ro)**2 + (y2-ro)**2)
    T2d    = CellVariable(name="T2D", mesh=mesh2d, value=f2c(T_cold_out))
    tol    = min(dx2, dy2)/2
    T2d.constrain(f2c(Tin_hot),    where=(r2 >= ro - tol))
    T2d.constrain(f2c(T_cold_out), where=(r2 <= ri + tol))
    DiffusionTerm(coeff=k_wall).solve(var=T2d)
    T2d_C = T2d.value.reshape((ny2d, nx2d))       # °C
    Z2d   = T2d_C * 9/5 + 32                      # °F
    X2d   = x2.reshape((ny2d, nx2d))
    Y2d   = y2.reshape((ny2d, nx2d))

    # 2D tabs
    tab2d = st.tabs(["Heatmap", "Isothermes", "Flux vect.", "Surf 3D", "Scatter 3D"])
    with tab2d[0]:
        fig_hm = go.Figure(go.Heatmap(z=Z2d, colorscale="Viridis"))
        fig_hm.update_layout(title="Heatmap 2D", template="plotly_dark", height=900)
        st.plotly_chart(fig_hm, use_container_width=True)
    with tab2d[1]:
        fig_iso = go.Figure(go.Contour(
            z=Z2d, colorscale="Viridis",
            contours=dict(showlabels=True, coloring="lines"),
            colorbar=dict(title="T [°F]")
        ))
        fig_iso.update_layout(title="Isothermes 2D", template="plotly_dark", height=900,
                              xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig_iso, use_container_width=True)
    with tab2d[2]:
        dTdy, dTdx = np.gradient(T2d_C, dy2, dx2)
        qx2 = -k_wall * dTdx
        qy2 = -k_wall * dTdy
        fig_q = go.Figure()
        skip = max(1, min(ny2d, nx2d)//20)
        for i in range(0, ny2d, skip):
            for j in range(0, nx2d, skip):
                fig_q.add_trace(go.Scatter(
                    x=[X2d[i,j], X2d[i,j] + qx2[i,j]*0.001],
                    y=[Y2d[i,j], Y2d[i,j] + qy2[i,j]*0.001],
                    mode="lines", showlegend=False
                ))
        fig_q.update_layout(title="Flux thermique 2D", template="plotly_dark", height=900,
                            xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig_q, use_container_width=True)
    with tab2d[3]:
        fig_surf = go.Figure(go.Surface(
            z=Z2d, x=X2d, y=Y2d, colorscale="Viridis",
            colorbar=dict(title="T [°F]")
        ))
        fig_surf.update_layout(title="Surface 3D – Température", template="plotly_dark", height=800,
                               scene=dict(xaxis=dict(visible=False),
                                          yaxis=dict(visible=False),
                                          zaxis=dict(title="T [°F]")))
        st.plotly_chart(fig_surf, use_container_width=True)
    with tab2d[4]:
        fig_sc3d = go.Figure(go.Scatter3d(
            x=X2d.flatten(), y=Y2d.flatten(), z=Z2d.flatten(),
            mode="markers", marker=dict(size=2, color=Z2d.flatten(), colorscale="Viridis",
                                       colorbar=dict(title="T [°F]"))
        ))
        fig_sc3d.update_layout(title="Scatter 3D – Température", template="plotly_dark", height=800,
                               scene=dict(xaxis=dict(visible=False),
                                          yaxis=dict(visible=False),
                                          zaxis=dict(title="T [°F]")))
        st.plotly_chart(fig_sc3d, use_container_width=True)

    # ───────────────────────── 3D SURFACE ANIMATION ───────────────────────── #
    initial_Z = np.full_like(Z2d, Tin_hot)
    n_frames  = 30
    alphas    = np.linspace(0, 1, n_frames)
    frames    = []
    for α in alphas:
        Zf = initial_Z * (1 - α) + Z2d * α
        frames.append(go.Frame(
            data=[go.Surface(x=X2d, y=Y2d, z=Zf, colorscale="Viridis")],
            name=f"{α:.2f}"
        ))

    fig_anim = go.Figure(data=frames[0].data, frames=frames)
    fig_anim.update_layout(
        title="Animation 3D – Distribution de température",
        scene=dict(xaxis_title="X [m]", yaxis_title="Y [m]", zaxis_title="T [°F]"),
        updatemenus=[dict(
            type="buttons", showactive=False,
            y=1, x=1.15, pad=dict(t=0, r=10),
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, {"frame": {"duration": 100, "redraw": True},
                                  "fromcurrent": True, "transition": {"duration": 0}}]),
                dict(label="■ Pause", method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate", "transition": {"duration": 0}}])
            ]
        )]
    )
    st.plotly_chart(fig_anim, use_container_width=True)



    # Assume X2d, Y2d, Z2d are already defined from your FiPy solve

    # 1) Create the static surface once
    surface = go.Surface(
        x=X2d, y=Y2d, z=Z2d,
        colorscale="Viridis",
        showscale=True
    )

    # 2) Build camera‐rotation frames
    n_frames = 60
    thetas   = np.linspace(0, 2*np.pi, n_frames)
    frames   = []
    radius   = 1.25  # distance of camera from center

    for θ in thetas:
        camera = dict(
            eye=dict(
                x= radius * np.cos(θ),
                y= radius * np.sin(θ),
                z= 0.75           # tilt above the XY plane
            )
        )
        frames.append(go.Frame(layout=dict(scene_camera=camera), name=f"{θ:.2f}"))

    # 3) Assemble the figure
    fig = go.Figure(
        data=[surface],
        frames=frames,
        layout=go.Layout(
            title="🔄 3D Surface Rotation",
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(title="T [°F]")
            ),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                y=1.1, x=0.0,
                pad=dict(t=0, r=10),
                buttons=[dict(
                    label="▶ Play",
                    method="animate",
                    args=[None, dict(
                        frame=dict(duration=50, redraw=False),
                        fromcurrent=True,
                        transition=dict(duration=0)
                    )]
                ), dict(
                    label="■ Pause",
                    method="animate",
                    args=[[None], dict(
                        frame=dict(duration=0, redraw=False),
                        mode="immediate",
                        transition=dict(duration=0)
                    )]
                )]
            )]
        )
    )

    # 4) Render inside Streamlit
    st.plotly_chart(fig, use_container_width=True)



else:
    st.info("Définissez vos paramètres puis cliquez sur « Lancer le calcul ».")
