import math
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Pagina-instellingen: geen sidebar tonen
st.set_page_config(page_title="🧭 2D Vector Visualisatie", layout="wide", initial_sidebar_state="collapsed")
HIDE_SIDEBAR_CSS = """
<style>
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
</style>
"""
st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)

st.title("🧭 2D Vector Visualisatie")

# ----------------------------
# Helpers
# ----------------------------
def vec_norm2(x, y):
    return math.sqrt(x*x + y*y)

def angle_deg(x, y):
    # θ t.o.v. X-as (in graden), bereik [-180, 180]
    if x == 0 and y == 0:
        return None
    return math.degrees(math.atan2(y, x))

def add_arrow2d(fig, x, y, color, linewidth, markersize, name, draw_arrowhead=True):
    # Lijn + punt
    fig.add_trace(go.Scatter(
        x=[0, x], y=[0, y],
        mode="lines+markers",
        line=dict(color=color, width=linewidth),
        marker=dict(size=markersize, color=color),
        name=name
    ))
    # Eenvoudige pijlpunten via annotation (werkt goed in 2D)
    if draw_arrowhead and (abs(x) + abs(y) > 1e-12):
        fig.add_annotation(
            x=x, y=y,
            ax=0, ay=0,
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=3, arrowsize=1.2, arrowwidth=max(1, linewidth-1), arrowcolor=color,
            opacity=0  # lijn al getekend; annotation vooral voor punt
        )

def pad_range(vals, pr=0.15):
    vmin, vmax = min(vals), max(vals)
    if abs(vmax - vmin) < 1e-9:
        vmin -= 1.0; vmax += 1.0
    pad = (vmax - vmin) * pr
    return (vmin - pad, vmax + pad)

# Plotly default palette (10)
COLOR_PALETTE = [
    "#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd",
    "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"
]

# ----------------------------
# Session state
# ----------------------------
if "entries2d" not in st.session_state:
    st.session_state.entries2d = [{
        "x": 0.0, "y": 0.0, "force": 0.0, "color": COLOR_PALETTE[0]
    }]
if "color_index_2d" not in st.session_state:
    st.session_state.color_index_2d = 1

# ----------------------------
# Sidebar-instellingen (rechtsboven verborgen, maar we gebruiken de waarden)
# ----------------------------
with st.sidebar:
    st.header("Instellingen")
    draw_arrowheads = st.checkbox("Pijlkoppen tonen", value=True)
    linewidth = st.slider("Lijndikte", 1, 12, 4)
    markersize = st.slider("Marker grootte", 1, 12, 6)
    autoscale = st.checkbox("Autoschaal assen", value=True)
    show_resultant = st.checkbox("Toon resultante vector", value=True)
    resultant_color = st.color_picker("Kleur resultante", value="#e41a1c")
    if not autoscale:
        st.caption("As-bereiken")
        xmin = st.number_input("Xmin", value=-10.0)
        xmax = st.number_input("Xmax", value=10.0)
        ymin = st.number_input("Ymin", value=-10.0)
        ymax = st.number_input("Ymax", value=10.0)
    st.markdown("---")
    if st.button("🗑️ Verwijder alle vectoren"):
        st.session_state.entries2d = [{
            "x": 0.0, "y": 0.0, "force": 0.0, "color": COLOR_PALETTE[0]
        }]
        st.session_state.color_index_2d = 1

# ----------------------------
# Invoer
# ----------------------------
st.subheader("Vectoren invoeren (van oorsprong)")

if st.button("➕ Voeg rij toe"):
    color = COLOR_PALETTE[st.session_state.color_index_2d % len(COLOR_PALETTE)]
    st.session_state.entries2d.append({"x": 0.0, "y": 0.0, "force": 0.0, "color": color})
    st.session_state.color_index_2d += 1

new_entries = []
for i, ent in enumerate(st.session_state.entries2d):
    cols = st.columns([1.4, 1.2, 1.2, 1.4, 0.6], gap="small")
    with cols[0]:
        force = st.number_input(f"Kracht N {i+1}", value=float(ent["force"]), min_value=0.0, key=f"force2_{i}")
    with cols[1]:
        x = st.number_input(f"X{i+1}", value=float(ent["x"]), key=f"x2_{i}")
    with cols[2]:
        y = st.number_input(f"Y{i+1}", value=float(ent["y"]), key=f"y2_{i}")
    with cols[3]:
        color = st.color_picker(f"Kleur {i+1}", value=ent.get("color", COLOR_PALETTE[i % len(COLOR_PALETTE)]), key=f"color2_{i}")
    with cols[4]:
        if st.button("🗑️", key=f"del2_{i}"):
            pass
        else:
            new_entries.append({"x": x, "y": y, "force": force, "color": color})

st.session_state.entries2d = new_entries

# ----------------------------
# Berekeningen
# ----------------------------
vectors = []
for ent in st.session_state.entries2d:
    x, y = ent["x"], ent["y"]
    mag = vec_norm2(x, y)
    if ent["force"] > 0 and mag > 1e-12:
        s = ent["force"] / mag
        x, y = x*s, y*s
    # sla alleen niet-lege vectoren op voor weergave
    if abs(x) + abs(y) > 0:
        vectors.append((x, y, ent["color"]))

# ----------------------------
# Plot
# ----------------------------
fig = go.Figure()
xs, ys = [], []
for i, (x, y, color) in enumerate(vectors, start=1):
    add_arrow2d(fig, x, y, color, linewidth, markersize, f"Vector {i}", draw_arrowheads)
    xs += [0, x]; ys += [0, y]

Rx = Ry = 0.0
if vectors:
    Rx = sum(x for x, y, _ in vectors)
    Ry = sum(y for x, y, _ in vectors)
    if show_resultant:
        add_arrow2d(fig, Rx, Ry, resultant_color, linewidth+1, markersize+2, "Resultante", True)
        xs += [0, Rx]; ys += [0, Ry]

# Assen & layout
if xs and ys:
    if autoscale:
        xr = pad_range(xs); yr = pad_range(ys)
    else:
        xr, yr = (xmin, xmax), (ymin, ymax)
else:
    xr, yr = (-1, 1), (-1, 1)

fig.update_layout(
    xaxis=dict(title="X", zeroline=True, range=[xr[0], xr[1]]),
    yaxis=dict(title="Y", zeroline=True, scaleanchor="x", scaleratio=1, range=[yr[0], yr[1]]),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0.0),
    showlegend=True
)

st.markdown("## Interactieve 2D Vectoren")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Resultaten + Uitleg
# ----------------------------
if vectors:
    rows = []
    for i, (x, y, color) in enumerate(vectors, start=1):
        mag = vec_norm2(x, y)
        ang = angle_deg(x, y)
        rows.append({
            "Vector": f"{i}",
            "X": round(x, 2), "Y": round(y, 2),
            "|v|": round(mag, 2),
            "θ (° vanaf X-as)": None if ang is None else round(ang, 2),
            "Kleur": color
        })

    Rmag = vec_norm2(Rx, Ry)
    Rang = angle_deg(Rx, Ry)

    rows.append({
        "Vector": "Resultante",
        "X": round(Rx, 2), "Y": round(Ry, 2),
        "|R|": round(Rmag, 2),
        "θ (° vanaf X-as)": None if Rang is None else round(Rang, 2),
        "Kleur": resultant_color
    })

    st.markdown("### Resultaten")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    # Uitleg
    st.markdown("### Uitleg (stap voor stap)")
    # 1) Per vector hoe verkregen
    for i, (x, y, color) in enumerate(vectors, start=1):
        mag0 = vec_norm2(x, y)
        ang0 = angle_deg(x, y)
        st.markdown(
            f"**Vector {i}:** componenten (X,Y)=({x:.2f}, {y:.2f}), |v|={mag0:.2f} N, "
            + (f"θ = atan2(Y,X) = atan2({y:.2f},{x:.2f}) = {ang0:.2f}°." if ang0 is not None else "θ niet gedefinieerd (nulvector).")
        )

    # 2) Som componenten
    st.markdown("**Som van componenten:**")
    st.markdown("Rx = " + " + ".join([f"{x:.2f}" for x, _, in vectors]) + f" = {Rx:.2f}")
    st.markdown("Ry = " + " + ".join([f"{y:.2f}" for _, y, in vectors]) + f" = {Ry:.2f}")

    # 3) Resultante en hoek-afleiding
    st.markdown("**Resultante:**")
    st.markdown(f"R = (Rx, Ry) = ({Rx:.2f}, {Ry:.2f}), |R| = √(Rx²+Ry²) = {Rmag:.2f} N.")
    if Rmag > 0:
        st.markdown("**Afleiding richtingshoek van R:**")
        st.markdown(f"θ = atan2(Ry, Rx) = atan2({Ry:.2f}, {Rx:.2f}) = {Rang:.2f}° (vanaf de X-as).")

st.markdown("---")
