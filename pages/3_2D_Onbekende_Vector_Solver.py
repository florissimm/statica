import math
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="🧭 2D Onbekende Vector Solver", layout="wide", initial_sidebar_state="expanded")
st.title("🧭 2D Onbekende Vector Solver")

# =========================
# Helpers
# =========================
def deg2rad(d): return math.radians(d)
def rad2deg(r): return math.degrees(r)
def norm2(x,y): return math.sqrt(x*x + y*y)
def angle_deg(x,y): 
    return None if (abs(x)<1e-12 and abs(y)<1e-12) else rad2deg(math.atan2(y,x))

def xy_from_F_theta(F, theta_deg):
    c, s = math.cos(deg2rad(theta_deg)), math.sin(deg2rad(theta_deg))
    return F*c, F*s

# =========================
# Sidebar: Resultant target
# =========================
with st.sidebar:
    st.header("Doel (resultante)")
    colA, colB = st.columns(2)
    with colA:
        Rmag = st.number_input("|R| (N)", value=1000.0, min_value=0.0, step=10.0)
    ori_choice = st.radio("Richting van R kiezen als:", ["Hoek vanaf X-as (φ)", "Langs x′-as (met rotatie α)"])
    if ori_choice == "Hoek vanaf X-as (φ)":
        phi = st.number_input("φ (° vanaf X-as)", value=0.0, step=1.0)
    else:
        alpha = st.number_input("α (° van X naar x′)", value=-30.0, step=1.0)
        phi = alpha  # R ligt langs x′ → zelfde richting als rotatie-as
    st.markdown("---")
    
# =========================
# Invoer bekende krachten
# =========================
st.subheader("Bekende krachten (grootte + hoek vanaf X-as)")
if "known_forces" not in st.session_state:
    st.session_state.known_forces = [
        {"F": 450.0, "theta": 45.0, "color": "#1f77b4"},  # F2
        {"F": 200.0, "theta": 0.0,   "color": "#ff7f0e"}  # F3
    ]
if "color_idx" not in st.session_state:
    st.session_state.color_idx = 2

PALETTE = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd",
           "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"]

col_btn1, col_btn2 = st.columns([1,3])
with col_btn1:
    if st.button("➕ Voeg bekende kracht toe"):
        st.session_state.known_forces.append({"F":0.0,"theta":0.0,"color":PALETTE[st.session_state.color_idx%len(PALETTE)]})
        st.session_state.color_idx += 1
with col_btn2:
    if st.button("🗑️ Leeg lijst"):
        st.session_state.known_forces = []
        st.session_state.color_idx = 0

rows = []
new_list = []
for i, ent in enumerate(st.session_state.known_forces):
    c = st.columns([1.2,1.2,1.5,0.6])
    with c[0]:
        Fi = st.number_input(f"F{i+1} (N)", value=float(ent["F"]), min_value=0.0, key=f"F_{i}")
    with c[1]:
        thetai = st.number_input(f"θ{i+1} (°)", value=float(ent["theta"]), key=f"th_{i}")
    with c[2]:
        colori = st.color_picker(f"Kleur {i+1}", value=ent["color"], key=f"col_{i}")
    with c[3]:
        if st.button("🗑️", key=f"del_{i}"):
            continue
    new_list.append({"F":Fi,"theta":thetai,"color":colori})
st.session_state.known_forces = new_list

st.markdown("---")

# =========================
# Onbekende kracht F1
# =========================
st.subheader("Onbekende kracht F₁ (wordt berekend)")
st.caption("We nemen precies **één** onbekende kracht F₁. Het programma kiest F₁ zó dat de som exact de gewenste resultante geeft.")

# =========================
# Rekenen
# =========================
# Som van bekende krachten
Sx = Sy = 0.0
for ent in st.session_state.known_forces:
    x,y = xy_from_F_theta(ent["F"], ent["theta"])
    Sx += x; Sy += y

# Doelcomponenten van R
Rx_target, Ry_target = xy_from_F_theta(Rmag, phi)

# Wat F₁ moet leveren
Dx = Rx_target - Sx
Dy = Ry_target - Sy
F1 = norm2(Dx, Dy)
theta1 = angle_deg(Dx, Dy)

# =========================
# Visualisatie
# =========================
fig = go.Figure()

# bekende krachten
for i, ent in enumerate(st.session_state.known_forces, start=1):
    x,y = xy_from_F_theta(ent["F"], ent["theta"])
    fig.add_trace(go.Scatter(
        x=[0,x], y=[0,y],
        mode="lines+markers",
        line=dict(color=ent["color"], width=3),
        marker=dict(size=6, color=ent["color"]),
        name=f"F{i} = {ent['F']:.0f} N @ {ent['theta']:.0f}°"
    ))

# F1 (oplossing)
fig.add_trace(go.Scatter(
    x=[0,Dx], y=[0,Dy],
    mode="lines+markers",
    line=dict(color="#d62728", width=4),
    marker=dict(size=7, color="#d62728"),
    name=f"F1 (onbekend) = {F1:.0f} N @ {0.0 if theta1 is None else theta1:.1f}°"
))

# R (doel)
fig.add_trace(go.Scatter(
    x=[0,Rx_target], y=[0,Ry_target],
    mode="lines+markers",
    line=dict(color="#e41a1c", width=5, dash="dash"),
    marker=dict(size=8, color="#e41a1c"),
    name=f"Gewenste R = {Rmag:.0f} N @ {phi:.1f}°"
))

# Asbereik
xs = [0, Rx_target, Dx] + [xy_from_F_theta(ent["F"], ent["theta"])[0] for ent in st.session_state.known_forces]
ys = [0, Ry_target, Dy] + [xy_from_F_theta(ent["F"], ent["theta"])[1] for ent in st.session_state.known_forces]

def pad_range(vals, pr=0.15):
    vmin, vmax = min(vals), max(vals)
    if abs(vmax - vmin) < 1e-9: vmin -= 1.0; vmax += 1.0
    pad = (vmax - vmin) * pr
    return (vmin - pad, vmax + pad)

xr = pad_range(xs); yr = pad_range(ys)

fig.update_layout(
    xaxis=dict(title="X", zeroline=True, range=[xr[0], xr[1]]),
    yaxis=dict(title="Y", zeroline=True, scaleanchor="x", scaleratio=1, range=[yr[0], yr[1]]),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0.0)
)

st.markdown("## Vectoren")
st.plotly_chart(fig, use_container_width=True)

# =========================
# Resultaten
# =========================
st.markdown("### Uitkomst F₁ (zodat ΣF = R)")
st.write(f"**F₁ = {F1:.2f} N**, **θ₁ = {0.0 if theta1 is None else theta1:.2f}°** (vanaf X-as)")
st.write(f"Doelresultante: **R = {Rmag:.2f} N** @ **{phi:.2f}°**")

# Controle / toelichting
st.markdown("### Controle & Uitleg")
# tabel
rows = []
for i, ent in enumerate(st.session_state.known_forces, start=1):
    x,y = xy_from_F_theta(ent["F"], ent["theta"])
    rows.append({"Kracht": f"F{i}", "F (N)": round(ent["F"],2), "θ (°)": round(ent["theta"],2),
                 "X": round(x,2), "Y": round(y,2)})
rows.append({"Kracht": "F1 (oplossing)", "F (N)": round(F1,2), "θ (°)": None if theta1 is None else round(theta1,2),
             "X": round(Dx,2), "Y": round(Dy,2)})
Sx2 = Sx + Dx; Sy2 = Sy + Dy
rows.append({"Kracht": "Som = R (check)", "F (N)": round(norm2(Sx2,Sy2),2), "θ (°)": round(angle_deg(Sx2,Sy2),2),
             "X": round(Sx2,2), "Y": round(Sy2,2)})
rows.append({"Kracht": "R (gewenst)", "F (N)": round(Rmag,2), "θ (°)": round(phi,2),
             "X": round(Rx_target,2), "Y": round(Ry_target,2)})

st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.markdown("**Werkwijze (in het kort):**")
st.markdown(
f"""
- Bekend: som van bekende componenten: **Sx = {Sx:.2f}**, **Sy = {Sy:.2f}**.  
- Doelcomponenten: **Rx = |R|cosφ = {Rmag:.2f}·cos({phi:.2f}°) = {Rx_target:.2f}**, **Ry = |R|sinφ = {Rmag:.2f}·sin({phi:.2f}°) = {Ry_target:.2f}**.  
- F₁ moet leveren: **Dx = Rx − Sx = {Dx:.2f}**, **Dy = Ry − Sy = {Dy:.2f}**.  
- Dus **F₁ = √(Dx² + Dy²) = {F1:.2f} N**, **θ₁ = atan2(Dy, Dx) = atan2({Dy:.2f}, {Dx:.2f}) = {0.0 if theta1 is None else theta1:.2f}°**.
"""
)
