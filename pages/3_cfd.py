##############################################################################
#  Échangeur tubulaire – Calcul, CFD & Explications
##############################################################################
import os, math
os.environ["FIPY_COMM"] = "serial"

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from fipy import Grid1D, CellVariable, DiffusionTerm

st.set_page_config(page_title="Échangeur tubulaire – CFD", layout="wide")
st.title("🔥  Échangeur Tubulaire — Calcul & Visualisation CFD")

inch = 0.0254  # m

# ───────────────────────── FORMULAIRE ───────────────────────── #
with st.form(key="form_hx"):
    ong = st.tabs(["Géométrie", "Fluide chaud", "Fluide froid",
                   "Paroi & encrassement", "Maillage"])

    # — GEOMETRIE —
    with ong[0]:
        c1, c2 = st.columns(2)
        with c1:
            N_tube = st.number_input("Nombre de tubes", 56,
                                     help="Total des tubes du faisceau")
            L_tube_in = st.number_input("Longueur tubes [pouce]", 112.20,
                                        format="%.2f",
                                        help="Longueur développée d’un tube")
            pitch_in = st.number_input("Pas triangulaire [pouce]", 0.9375,
                                       format="%.4f",
                                       help="Distance entre axes de deux tubes adjacents")
        with c2:
            Do_in = st.number_input("Ø ext. tube [pouce]", 0.75, format="%.3f")
            Di_in = st.number_input("Ø int. tube [pouce]", 0.584, format="%.3f")
            Ds_in = st.number_input("Ø int. calandre [pouce]", 10.136, format="%.3f")

    # — FLUIDE CHAUD —
    with ong[1]:
        c1, c2 = st.columns(2)
        with c1:
            m_hot = st.number_input("Débit chaud [lb/h]", 11023.1, format="%.1f")
            Tin_hot = st.number_input("T° entrée chaud [°F]", 206.33, format="%.2f")
            Tout_hot = st.number_input("T° sortie chaud [°F]", 117.04, format="%.2f")
        with c2:
            cp_hot = st.number_input("cᵖ chaud [BTU/(lb·°F)]", 0.624, format="%.4f")
            mu_hot = st.number_input("μ chaud [cP]", 4.83, format="%.3f")
            k_hot = st.number_input("k chaud [BTU/(ft·h·°F)]", 0.1495, format="%.4f")
            rho_hot = st.number_input("ρ chaud [lb/ft³]", 67.20, format="%.2f")

    # — FLUIDE FROID —
    with ong[2]:
        c1, c2 = st.columns(2)
        with c1:
            m_cold = st.number_input("Débit froid [lb/h]", 26455.5, format="%.1f")
            Tin_cold = st.number_input("T° entrée froid [°F]", -9.67, format="%.2f")
        with c2:
            cp_cold = st.number_input("cᵖ froid [BTU/(lb·°F)]", 0.261, format="%.4f")
            mu_cold = st.number_input("μ froid [cP]", 0.276, format="%.3f")
            k_cold = st.number_input("k froid [BTU/(ft·h·°F)]", 0.0465, format="%.4f")
            rho_cold = st.number_input("ρ froid [lb/ft³]", 86.4, format="%.2f")

    # — PAROI & ENCRASSEMENT —
    with ong[3]:
        k_wall = st.number_input("k métal tube [W/m·K]", 16.5, format="%.2f")
        c1, c2 = st.columns(2)
        with c1:
            Rf_hot = st.number_input("Encrassement calandre [ft²·h·°F/BTU]",
                                     0.0006, format="%.5f")
        with c2:
            Rf_cold = st.number_input("Encrassement tubes [ft²·h·°F/BTU]",
                                      0.0006, format="%.5f")

    # — MAILLAGE —
    with ong[4]:
        c1, c2 = st.columns(2)
        with c1:
            nx = st.slider("Cellules radiales", 10, 300, 60,
                           help="Volumes finis à travers l’épaisseur du tube")
        with c2:
            nang = st.slider("Cellules angulaires", 4, 360, 90,
                             help="Résolution pour la réplication polaire")

    run = st.form_submit_button("🚀  Lancer le calcul")

# ───────────────────────── CALCULS ──────────────────────────── #
if run:
    # Convertir géométrie
    L_tube = L_tube_in*inch
    Do, Di, Ds, pitch = Do_in*inch, Di_in*inch, Ds_in*inch, pitch_in*inch

    # Fonctions de conversion
    f2c = lambda F: (F-32)*5/9
    BTU2W = lambda Q: Q*1055.06/3600
    cp_SI = lambda cp: cp*4186.8/778
    k_SI = lambda k: k*1.7307
    mu_SI = lambda mu: mu*0.001
    rho_SI = lambda r: r*16.0185

    μ_hot, μ_cold = mu_SI(mu_hot), mu_SI(mu_cold)
    ρ_hot, ρ_cold = rho_SI(rho_hot), rho_SI(rho_cold)
    k_hot_SI, k_cold_SI = k_SI(k_hot), k_SI(k_cold)
    cp_hot_SI, cp_cold_SI = cp_SI(cp_hot), cp_SI(cp_cold)

    # Tube side : Dittus‑Boelter
    m_cold_kg_s = m_cold*0.4536/3600
    v_cold = m_cold_kg_s/(ρ_cold*np.pi*(Di/2)**2*N_tube)
    Re_c = ρ_cold*v_cold*Di/μ_cold
    Pr_c = cp_cold_SI*μ_cold/k_cold_SI
    Nu_c = 0.023*Re_c**0.8*Pr_c**0.4
    h_i = Nu_c*k_cold_SI/Di

    # Shell side : Kern
    m_hot_kg_s = m_hot*0.4536/3600
    A_shell = np.pi*(Ds/2)**2
    v_shell = m_hot_kg_s/(ρ_hot*A_shell)
    De = 4*(pitch**2 - np.pi*Do**2/4)/(np.pi*Do)
    Re_s = ρ_hot*v_shell*De/μ_hot
    Pr_s = cp_hot_SI*μ_hot/k_hot_SI
    j_h = 0.36*Re_s**-0.55
    Nu_s = j_h*Re_s*Pr_s**(1/3)
    h_o = Nu_s*k_hot_SI/De

    # Uo
    R_conv_o = 1/h_o
    R_conv_i = 1/h_i*(Do/Di)
    R_wall = np.log(Do/Di)/(2*np.pi*k_wall*L_tube)
    R_foul = (Rf_hot+Rf_cold)/(0.3048**2)
    Uo = 1/(R_conv_o+R_conv_i+R_wall+R_foul)

    # Puissance & T sortie froid
    Q_BTUh = m_hot*cp_hot*(Tin_hot-Tout_hot)
    Q_W = BTU2W(Q_BTUh)
    T_cold_out = Tin_cold + Q_BTUh/(m_cold*cp_cold)

    # METRIQUES
    m1, m2, m3 = st.columns(3)
    m1.metric("U₀", f"{Uo:.1f} W/m²·K")
    m2.metric("Puissance Q", f"{Q_BTUh:,.0f} BTU/h")
    m3.metric("T° sortie froid", f"{T_cold_out:.2f} °F")

    # Profils axiaux
    z = np.linspace(0, L_tube, 30)
    T_hot_z = Tin_hot - (Tin_hot-Tout_hot)*(z/L_tube)
    T_cold_z = Tin_cold + (T_cold_out-Tin_cold)*(z/L_tube)

    # Profil radial (FiPy)
    mesh = Grid1D(nx=nx, dx=(Do-Di)/2/nx)
    T_r = CellVariable(mesh=mesh, value=f2c(T_cold_out))
    T_r.constrain(f2c(Tin_hot), mesh.facesLeft)
    T_r.constrain(f2c(T_cold_out), mesh.facesRight)
    DiffusionTerm(k_wall).solve(var=T_r)
    r_n = np.array(mesh.cellCenters[0]+Di/2)
    T_n = np.array(T_r.value)*9/5+32
    dTdr = np.gradient(T_n, r_n)
    q_r = -k_wall*dTdr  # W/m²

    # Maillage polaire pour cartes
    ang = np.linspace(0, 2*np.pi, nang)
    Rg, Ag = np.meshgrid(r_n, ang, indexing="ij")
    Zg = np.tile(T_n[:,None], (1,nang))
    Zq = np.tile(np.abs(q_r)[:,None], (1,nang))

    # VISUELS
    colA, colB = st.columns(2)

    with colA:
        figA = go.Figure()
        figA.add_trace(go.Scatter(x=z, y=T_hot_z, name="Chaude (vrac)"))
        figA.add_trace(go.Scatter(x=z, y=T_cold_z, name="Froide (vrac)"))
        figA.update_layout(title="Profils axiaux",
                           xaxis_title="Longueur tube [m]",
                           yaxis_title="T [°F]",
                           template="plotly_dark", height=320)
        st.plotly_chart(figA, use_container_width=True)

    with colB:
        figB = go.Figure(go.Scatter(x=r_n, y=T_n, mode="lines"))
        figB.update_layout(title="Profil radial paroi",
                           xaxis_title="Rayon [m]", yaxis_title="T [°F]",
                           template="plotly_dark", height=320)
        st.plotly_chart(figB, use_container_width=True)

    # Tabs visuels CFD
    t1, t2, t3, t4, t5 = st.tabs(
        ["Carte T", "Isothermes", "Vecteurs qʺ", "Carte |qʺ|", "Surface 3D"])

    with t1:
        st.plotly_chart(
            go.Figure(go.Heatmap(z=Zg, colorscale="Viridis",
                                 colorbar=dict(title="T [°F]")))
            .update_layout(template="plotly_dark", height=380,
                           xaxis=dict(visible=False), yaxis=dict(visible=False)),
            use_container_width=True)

    with t2:
        st.plotly_chart(
            go.Figure(go.Contour(z=Zg, colorscale="Viridis",
                                 contours=dict(showlabels=True),
                                 line_smoothing=0.9))
            .update_layout(template="plotly_dark", height=380,
                           xaxis=dict(visible=False), yaxis=dict(visible=False)),
            use_container_width=True)

    with t3:
        fig_vec = go.Figure()
        step = max(1, nx//25)
        for i in range(0, len(r_n), step):
            x0, y0 = r_n[i], 0
            mag = q_r[i]*0.004
            fig_vec.add_trace(go.Scatter(x=[0, x0+mag], y=[0, 0],
                                         mode="lines",
                                         line=dict(color="cyan", width=1),
                                         hoverinfo="skip", showlegend=False))
        fig_vec.update_layout(template="plotly_dark", height=380,
                              xaxis=dict(visible=False), yaxis=dict(visible=False),
                              title="Flux radial (vue simplifiée)")
        st.plotly_chart(fig_vec, use_container_width=True)

    with t4:
        st.plotly_chart(
            go.Figure(go.Heatmap(z=Zq, colorscale="Plasma",
                                 colorbar=dict(title="|qʺ| [W/m²]")))
            .update_layout(template="plotly_dark", height=380,
                           xaxis=dict(visible=False), yaxis=dict(visible=False)),
            use_container_width=True)

    with t5:
        st.plotly_chart(
            go.Figure(go.Surface(z=Zg, colorscale="Viridis"))
            .update_layout(template="plotly_dark", height=380,
                           scene=dict(xaxis=dict(visible=False),
                                      yaxis=dict(visible=False),
                                      zaxis=dict(title="T [°F]"))),
            use_container_width=True)

    # ── EXPLICATIONS PHYSIQUES ────────────────────────────────
    with st.expander("📚  Explications physiques (cliquer pour développer)"):
        st.markdown(
        r"""
### 1. Conduction radiale (paroi du tube)

On résout en régime permanent :

\[
\frac{1}{r}\,\frac{d}{dr}\!\left(r\,\frac{dT}{dr}\right)=0
\]

FiPy discrétise cette équation (volumes finis) entre \(r = D_i/2\) et \(r = D_o/2\)  
avec conditions de Dirichlet \(T(r_i)=T_{\text{chaud}}\) et \(T(r_o)=T_{\text{froid}}\).

---

### 2. Convection filmique

| Côté | Corrélation | Formule |
|------|-------------|---------|
| Tubes (fluide froid) | **Dittus‑Boelter** (turbulent) | \(Nu = 0{,}023\,Re^{0,8}Pr^{0,4}\) |
| Calandre (fluide chaud) | **Kern** simplifié | \(Nu = j_H Re Pr^{1/3}\) avec \(j_H =0{,}36 Re^{-0,55}\) |

De là, on déduit \(h_i\) et \(h_o\).

---

### 3. Résistance globale

\[
U_o^{-1}= \frac1{h_o}+ \frac1{h_i}\frac{D_o}{D_i}+R_\text{mur}+R_\text{encr}
\]

où \(R_\text{mur}= \dfrac{\ln(D_o/D_i)}{2\pi k_\text{métal} L}\).

---

### 4. Bilan thermique

\[
Q = \dot m_{\text{chaud}} c_p (T_{\text{in}}-T_{\text{out}})
\]

Même \(Q\) chauffe le fluide froid :

\[
T_{\text{froid,out}} = T_{\text{froid,in}} + \frac{Q}{\dot m_{\text{froid}} c_p}
\]

---

### 5. Visuels

* **Carte T / isothermes / surface 3D** : duplication du profil 1 D sur 360 ° → rendu CFD.
* **Carte |qʺ|** : module du flux radial \(q_r=-k\,dT/dr\).
* **Vecteurs** : orientation radiale + magnitude proportionnelle à \(|qʺ|\).
""")
else:
    st.info("Définissez vos paramètres puis cliquez sur « Lancer le calcul ».")
