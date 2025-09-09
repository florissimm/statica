import math
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Sidebar zichtbaar
st.set_page_config(page_title="🧭 2D Vector Visualisatie", layout="wide", initial_sidebar_state="expanded")
st.title("🧭 2D Vector Visualisatie")

# ----------------------------
# Helpers
# ----------------------------
def vec_norm2(x, y):
    return math.sqrt(x*x + y*y)

def angle_from_x_deg(x, y):
    """Richtingshoek t.o.v. X-as ([-180,180])"""
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        return None
    return math.degrees(math.atan2(y, x))

def pad_range(vals, pr=0.15):
    vmin, vmax = min(vals), max(vals)
    if abs(vmax - vmin) < 1e-9:
        vmin -= 1.0; vmax += 1.0
    pad = (vmax - vmin) * pr
    return (vmin - pad, vmax + pad)

def add_arrow2d(fig, x, y, color, linewidth, markersize, name, draw_arrowhead=True):
    fig.add_trace(go.Scatter(
        x=[0, x], y=[0, y],
        mode="lines+markers",
        line=dict(color=color, width=linewidth),
        marker=dict(size=markersize, color=color),
        name=name
    ))
    if draw_arrowhead and (abs(x) + abs(y) > 1e-12):
        fig.add_annotation(
            x=x, y=y, ax=0, ay=0,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.2,
            arrowwidth=max(1, linewidth-1), arrowcolor=color,
            opacity=0
        )

# Plotly default 10-kleuren
COLOR_PALETTE = [
    "#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd",
    "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"
]

# ----------------------------
# Session state
# ----------------------------
if "entries2d" not in st.session_state:
    st.session_state.entries2d = [{
        "mode": "cart",      # "cart" of "angle"
        "force": 0.0,        # optioneel: schaal de (x,y) naar F
        "x": 0.0, "y": 0.0,  # gebruikt in cart
        "theta": 0.0,        # graden
        "ref": "X-as",       # "X-as" of "Y-as" (alleen voor angle)
        "color": COLOR_PALETTE[0]
    }]
if "color_index_2d" not in st.session_state:
    st.session_state.color_index_2d = 1

# ----------------------------
# Sidebar
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
            "mode":"cart","force":0.0,"x":0.0,"y":0.0,"theta":0.0,"ref":"X-as","color":COLOR_PALETTE[0]
        }]
        st.session_state.color_index_2d = 1

# ----------------------------
# Invoer
# ----------------------------
st.subheader("Vectoren invoeren (van oorsprong)")

if st.button("➕ Voeg rij toe"):
    color = COLOR_PALETTE[st.session_state.color_index_2d % len(COLOR_PALETTE)]
    st.session_state.entries2d.append({
        "mode":"cart","force":0.0,"x":0.0,"y":0.0,"theta":0.0,"ref":"X-as","color":color
    })
    st.session_state.color_index_2d += 1

new_entries = []
for i, ent in enumerate(st.session_state.entries2d):
    cols = st.columns([1.1, 1.1, 1.2, 1.2, 1.3, 0.7], gap="small")
    with cols[0]:
        mode = st.selectbox(
            f"Modus {i+1}",
            ["cart", "angle"],  # cart: X,Y | angle: F, θ, ref
            index=0 if ent["mode"]=="cart" else 1,
            key=f"mode2d_{i}"
        )
    with cols[1]:
        force = st.number_input(f"Kracht N {i+1}", value=float(ent["force"]), min_value=0.0, key=f"force2d_{i}")

    if mode == "cart":
        with cols[2]:
            x = st.number_input(f"X{i+1}", value=float(ent["x"]), key=f"x2d_{i}")
        with cols[3]:
            y = st.number_input(f"Y{i+1}", value=float(ent["y"]), key=f"y2d_{i}")
        with cols[4]:
            color = st.color_picker(f"Kleur {i+1}", value=ent.get("color", COLOR_PALETTE[i % len(COLOR_PALETTE)]), key=f"color2d_{i}")
        with cols[5]:
            if st.button("🗑️", key=f"del2d_{i}"):
                pass
            else:
                new_entries.append({
                    "mode":"cart","force":force,"x":x,"y":y,
                    "theta":0.0,"ref":"X-as","color":color
                })
    else:
        with cols[2]:
            theta = st.number_input(f"θ°{i+1}", value=float(ent["theta"]), key=f"theta2d_{i}")
        with cols[3]:
            ref_axis = st.selectbox(
                "Ref",
                ["X-as", "Y-as"],
                index=0 if ent.get("ref","X-as")=="X-as" else 1,
                key=f"ref2d_{i}"
            )
        with cols[4]:
            color = st.color_picker(f"Kleur {i+1}", value=ent.get("color", COLOR_PALETTE[i % len(COLOR_PALETTE)]), key=f"color2d_{i}")
        with cols[5]:
            if st.button("🗑️", key=f"del2d_{i}"):
                pass
            else:
                new_entries.append({
                    "mode":"angle","force":force,"x":0.0,"y":0.0,
                    "theta":theta,"ref":ref_axis,"color":color
                })

st.session_state.entries2d = new_entries

# ----------------------------
# Berekeningen
# ----------------------------
vectors = []        # (x,y,color)
explain_rows = []   # strings

for ent in st.session_state.entries2d:
    mode = ent["mode"]
    F = ent["force"] or 0.0

    if mode == "cart":
        x0, y0 = ent["x"], ent["y"]
        mag0 = vec_norm2(x0, y0)
        if F > 0 and mag0 > 1e-12:
            s = F / mag0
            x, y = x0*s, y0*s
            explain_rows.append(
                f"**cart**: basis (x0,y0)=({x0:.2f},{y0:.2f}), F={F:.2f} → s=F/||v0||={F:.2f}/{mag0:.2f}={s:.2f} → X={x:.2f}, Y={y:.2f}"
            )
        else:
            x, y = x0, y0
            explain_rows.append(f"**cart**: direct (X,Y)=({x:.2f},{y:.2f})")

    else:
        theta = float(ent["theta"])
        ref_axis = ent.get("ref", "X-as")
        if ref_axis == "X-as":
            x = F * math.cos(math.radians(theta))
            y = F * math.sin(math.radians(theta))
            explain_rows.append(
                f"**angle-X**: F={F:.2f} N, θ={theta:.2f}° vanaf X → X=F·cosθ={x:.2f}, Y=F·sinθ={y:.2f}"
            )
        else:  # Y-as
            # Hoek gemeten vanaf Y: componenten omgedraaid
            x = F * math.sin(math.radians(theta))
            y = F * math.cos(math.radians(theta))
            explain_rows.append(
                f"**angle-Y**: F={F:.2f} N, θ={theta:.2f}° vanaf Y → X=F·sinθ={x:.2f}, Y=F·cosθ={y:.2f}"
            )

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
        angx = angle_from_x_deg(x, y)
        rows.append({
            "Vector": f"{i}",
            "X": round(x, 2), "Y": round(y, 2),
            "|v| (N)": round(mag, 2),
            "θ (° vanaf X-as)": None if angx is None else round(angx, 2),
            "Kleur": color
        })

    Rmag = vec_norm2(Rx, Ry)
    Rang = angle_from_x_deg(Rx, Ry)

    rows.append({
        "Vector": "Resultante",
        "X": round(Rx, 2), "Y": round(Ry, 2),
        "|R| (N)": round(Rmag, 2),
        "θ (° vanaf X-as)": None if Rang is None else round(Rang, 2),
        "Kleur": resultant_color
    })

    st.markdown("### Resultaten")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.markdown("### Uitleg (stap voor stap)")
    for i, text in enumerate(explain_rows, start=1):
        st.markdown(f"- **Vector {i}:** {text}")

    st.markdown("**Som van componenten:**")
    st.markdown("Rx = " + " + ".join([f"{x:.2f}" for x, _, _ in vectors]) + f" = {Rx:.2f}")
    st.markdown("Ry = " + " + ".join([f"{y:.2f}" for _, y, _ in vectors]) + f" = {Ry:.2f}")

    st.markdown("**Resultante:**")
    st.markdown(f"R = (Rx, Ry) = ({Rx:.2f}, {Ry:.2f}), |R| = √(Rx²+Ry²) = {Rmag:.2f} N.")
    if Rmag > 0:
        st.markdown("**Richtingshoek van R (vanaf X-as):**")
        st.markdown(f"θ = atan2(Ry, Rx) = atan2({Ry:.2f}, {Rx:.2f}) = {Rang:.2f}°.")
