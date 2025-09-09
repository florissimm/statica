import math
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="🧭 3D Vector Visualisatie", layout="wide")
st.title("🧭 3D Vector Visualisatie")

# ===================================
# Helpers
# ===================================
def vec_norm(x, y, z):
    return math.sqrt(x*x + y*y + z*z)

def cart_to_alpha_beta_gamma(x, y, z):
    mag = vec_norm(x,y,z)
    if mag < 1e-12:
        return None, None, None, 0.0
    a = math.degrees(math.acos(max(-1,min(1,x/mag))))
    b = math.degrees(math.acos(max(-1,min(1,y/mag))))
    g = math.degrees(math.acos(max(-1,min(1,z/mag))))
    return a, b, g, mag

def alpha_beta_gamma_to_cart(mag, alpha_deg, beta_deg, gamma_deg, normalize_if_needed=True):
    ca = math.cos(math.radians(alpha_deg))
    cb = math.cos(math.radians(beta_deg))
    cg = math.cos(math.radians(gamma_deg))
    s = ca*ca + cb*cb + cg*cg
    if s <= 1e-12:
        return 0.0, 0.0, 0.0
    if normalize_if_needed and abs(s - 1.0) > 1e-3:
        k = math.sqrt(s)
        ca, cb, cg = ca/k, cb/k, cg/k
    return mag*ca, mag*cb, mag*cg

def add_arrow(fig, x, y, z, color, linewidth, markersize, show_points, draw_arrowheads, name):
    fig.add_trace(go.Scatter3d(
        x=[0, x], y=[0, y], z=[0, z],
        mode="lines+markers" if show_points else "lines",
        line=dict(width=linewidth, color=color),
        marker=dict(size=markersize, color=color),
        name=name
    ))
    if draw_arrowheads and (abs(x)+abs(y)+abs(z) > 1e-12):
        norm = vec_norm(x,y,z)
        frac = 0.04
        bx, by, bz = (1-frac)*x, (1-frac)*y, (1-frac)*z
        colorscale = [[0, color], [1, color]]
        fig.add_trace(go.Cone(
            x=[bx], y=[by], z=[bz],
            u=[x], v=[y], w=[z],
            sizemode="absolute",
            sizeref=max(1e-9, norm * 0.06),
            showscale=False,
            colorscale=colorscale,
            name=f"{name} arrow"
        ))

def entry_to_cart(ent, normalize_dircos=True):
    if ent["mode"] == "cart":
        x,y,z = ent["x"], ent["y"], ent["z"]
        mag = vec_norm(x,y,z)
        if (ent["force"] or 0) > 0 and mag > 1e-12:
            scale = ent["force"] / mag
            return x*scale, y*scale, z*scale
        return x,y,z
    else:
        mag = ent["force"] or 0.0
        return alpha_beta_gamma_to_cart(mag, ent["alpha"], ent["beta"], ent["gamma"], normalize_if_needed=normalize_dircos)

def pad_range(vals, pr=0.15):
    vmin, vmax = min(vals), max(vals)
    if abs(vmax - vmin) < 1e-9:
        vmin -= 1.0; vmax += 1.0
    pad = (vmax - vmin) * pr
    return (vmin - pad, vmax + pad)

def add_origin_axes(fig, xr, yr, zr, color="#9e9e9e", width=2, with_labels=False):
    """Voeg X/Y/Z-assen door (0,0,0) toe en optioneel labels X,Y,Z op de +uiteinden."""
    # X
    fig.add_trace(go.Scatter3d(
        x=[xr[0], xr[1]], y=[0,0], z=[0,0],
        mode="lines", line=dict(color=color, width=width),
        name="X-as (0)", showlegend=False
    ))
    # Y
    fig.add_trace(go.Scatter3d(
        x=[0,0], y=[yr[0], yr[1]], z=[0,0],
        mode="lines", line=dict(color=color, width=width),
        name="Y-as (0)", showlegend=False
    ))
    # Z
    fig.add_trace(go.Scatter3d(
        x=[0,0], y=[0,0], z=[zr[0], zr[1]],
        mode="lines", line=dict(color=color, width=width),
        name="Z-as (0)", showlegend=False
    ))
    if with_labels:
        fig.add_trace(go.Scatter3d(
            x=[xr[1], 0, 0],
            y=[0,     yr[1], 0],
            z=[0,     0,     zr[1]],
            mode="text",
            text=["X","Y","Z"],
            textposition="middle center",
            showlegend=False
        ))

# Plotly default palette (10)
COLOR_PALETTE = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd",
                 "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"]

# ===================================
# Session state
# ===================================
if "entries" not in st.session_state:
    st.session_state.entries = [
        {"mode":"cart","force":0.0,"x":0.0,"y":0.0,"z":0.0,
         "alpha":0.0,"beta":0.0,"gamma":0.0,"color":COLOR_PALETTE[0]},
    ]
if "color_index" not in st.session_state:
    st.session_state.color_index = 1

# ===================================
# Sidebar opties
# ===================================
with st.sidebar:
    st.header("Instellingen")
    draw_arrowheads = st.checkbox("Pijlkoppen tonen", value=True)
    show_points = st.checkbox("Eindpunten tonen", value=True)
    linewidth = st.slider("Lijndikte", 1, 12, 6)
    markersize = st.slider("Marker grootte", 1, 12, 5)
    autoscale = st.checkbox("Autoschaal assen", value=True)
    normalize_dircos = st.checkbox("Normaliseer αβγ (cos²-som → 1)", value=True)
    show_resultant = st.checkbox("Toon resultante vector in 3D", value=True)
    resultant_color = st.color_picker("Kleur resultante", value="#e41a1c")

    st.markdown("---")
    # Nieuw: assen door oorsprong + opties
    show_origin_axes = st.checkbox("Toon assen door oorsprong (X/Y/Z)", value=True)
    origin_axes_color = st.color_picker("Kleur assen (0,0,0)", value="#9e9e9e")
    origin_axes_width = st.slider("Lijndikte assen (0,0,0)", 1, 8, 2)
    show_origin_axis_labels = st.checkbox("Toon labels bij oorsprong-assen (X/Y/Z)", value=True)

    st.markdown("---")
    # Nieuw: grid/titels/assen
    show_axis_numbers = st.checkbox("Toon as-getallen (ticks)", value=True)
    show_grid = st.checkbox("Toon rasterlijnen (grid)", value=True)
    hide_xyz_axes = st.checkbox("Verberg X/Y/Z-assen (alles van Plotly-assen)", value=False)

    st.markdown("---")
    if not autoscale:
        st.caption("As-bereiken")
        xmin = st.number_input("Xmin", value=-10.0)
        xmax = st.number_input("Xmax", value=10.0)
        ymin = st.number_input("Ymin", value=-10.0)
        ymax = st.number_input("Ymax", value=10.0)
        zmin = st.number_input("Zmin", value=-10.0)
        zmax = st.number_input("Zmax", value=10.0)
    st.markdown("---")
    if st.button("🗑️ Verwijder alle vectoren"):
        st.session_state.entries = [{"mode":"cart","force":0.0,"x":0.0,"y":0.0,"z":0.0,
                                     "alpha":0.0,"beta":0.0,"gamma":0.0,"color":COLOR_PALETTE[0]}]
        st.session_state.color_index = 1

# ===================================
# Invoer per vector
# ===================================
st.subheader("Vectoren invoeren (van oorsprong)")

if st.button("➕ Voeg rij toe"):
    color = COLOR_PALETTE[st.session_state.color_index % len(COLOR_PALETTE)]
    st.session_state.entries.append({
        "mode": "cart",
        "force": 0.0,
        "x": 0.0, "y": 0.0, "z": 0.0,
        "alpha": 0.0, "beta": 0.0, "gamma": 0.0,
        "color": color
    })
    st.session_state.color_index += 1

new_entries = []
for i, ent in enumerate(st.session_state.entries):
    cols = st.columns([1.4, 1.8, 1.6, 1.6, 1.6, 1.8, 0.8], gap="small")
    with cols[0]:
        mode = st.selectbox(
            f"Modus {i+1}",
            ["cart", "dir"],
            index=0 if ent["mode"]=="cart" else 1,
            key=f"mode_{i}",
        )
    with cols[1]:
        force = st.number_input(f"Kracht N {i+1}", value=float(ent["force"]), min_value=0.0, key=f"force_{i}")
    if mode == "cart":
        with cols[2]:
            x = st.number_input(f"X{i+1}", value=float(ent["x"]), key=f"x_{i}")
        with cols[3]:
            y = st.number_input(f"Y{i+1}", value=float(ent["y"]), key=f"y_{i}")
        with cols[4]:
            z = st.number_input(f"Z{i+1}", value=float(ent["z"]), key=f"z_{i}")
        with cols[5]:
            color = st.color_picker(f"Kleur {i+1}", value=ent.get("color",COLOR_PALETTE[i%len(COLOR_PALETTE)]), key=f"color_{i}")
        with cols[6]:
            if st.button("🗑️", key=f"del_{i}"):
                pass
            else:
                new_entries.append({"mode":"cart","force":force,"x":x,"y":y,"z":z,
                                    "alpha":0.0,"beta":0.0,"gamma":0.0,"color":color})
    else:
        with cols[2]:
            alpha = st.number_input(f"α°{i+1}", value=float(ent["alpha"]), key=f"alpha_{i}")
        with cols[3]:
            beta = st.number_input(f"β°{i+1}", value=float(ent["beta"]), key=f"beta_{i}")
        with cols[4]:
            gamma = st.number_input(f"γ°{i+1}", value=float(ent["gamma"]), key=f"gamma_{i}")
        with cols[5]:
            color = st.color_picker(f"Kleur {i+1}", value=ent.get("color",COLOR_PALETTE[i%len(COLOR_PALETTE)]), key=f"color_{i}")
        with cols[6]:
            if st.button("🗑️", key=f"del_{i}"):
                pass
            else:
                new_entries.append({"mode":"dir","force":force,"x":0.0,"y":0.0,"z":0.0,
                                    "alpha":alpha,"beta":beta,"gamma":gamma,"color":color})

st.session_state.entries = new_entries

# ===================================
# Plot
# ===================================
def is_blank(ent):
    if ent["mode"] == "cart":
        return (ent["force"] or 0) <= 0 and vec_norm(ent["x"],ent["y"],ent["z"]) <= 0
    else:
        return (ent["force"] or 0) <= 0

usable_entries = [e for e in st.session_state.entries if not is_blank(e)]
vectors = [entry_to_cart(ent, normalize_dircos=normalize_dircos) for ent in usable_entries]
colors  = [ent.get("color",COLOR_PALETTE[i%len(COLOR_PALETTE)]) for i,ent in enumerate(usable_entries)]

with st.sidebar:
    st.markdown("---")
    st.caption(f"Aantal getekende vectoren: **{len(vectors)}**")

fig = go.Figure()
xs, ys, zs = [], [], []
for i, ((x, y, z), color) in enumerate(zip(vectors, colors), start=1):
    add_arrow(fig, x, y, z, color, linewidth, markersize, show_points, draw_arrowheads, f"Vector {i}")
    xs += [0, x]; ys += [0, y]; zs += [0, z]

# Resultante vector optioneel
Rx = Ry = Rz = 0.0
if vectors and show_resultant:
    Rx = sum(x for x,y,z in vectors)
    Ry = sum(y for x,y,z in vectors)
    Rz = sum(z for x,y,z in vectors)
    add_arrow(fig, Rx, Ry, Rz, resultant_color, linewidth+2, markersize+2, show_points, draw_arrowheads, "Resultante")

# Asbereiken
if xs and ys and zs:
    if show_resultant and (Rx or Ry or Rz):
        xs += [0, Rx]; ys += [0, Ry]; zs += [0, Rz]
    if autoscale:
        xr = pad_range(xs); yr = pad_range(ys); zr = pad_range(zs)
    else:
        xr, yr, zr = (xmin, xmax), (ymin, ymax), (zmin, zmax)
else:
    xr, yr, zr = (-1, 1), (-1, 1), (-1, 1)

# Oorsprong-assen (optioneel met labels)
if show_origin_axes:
    add_origin_axes(fig, xr, yr, zr, color=origin_axes_color, width=origin_axes_width, with_labels=show_origin_axis_labels)

# As layout toggles
def axis_cfg(title):
    if hide_xyz_axes:
        return dict(visible=False)
    return dict(
        title=title,
        range=[xr[0], xr[1]] if title=="X" else ([yr[0], yr[1]] if title=="Y" else [zr[0], zr[1]]),
        showticklabels=show_axis_numbers,
        showgrid=show_grid
    )

fig.update_layout(
    scene=dict(
        xaxis=axis_cfg("X"),
        yaxis=axis_cfg("Y"),
        zaxis=axis_cfg("Z"),
        aspectmode="cube",
    ),
    margin=dict(l=0, r=0, t=40, b=0),
    legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0.0)
)

st.markdown("## Interactieve 3D Vectoren")
st.plotly_chart(fig, use_container_width=True)

# ===================================
# Resultaten onder de plot
# ===================================
if vectors:
    rows = []
    for i, ((x,y,z), color) in enumerate(zip(vectors, colors), start=1):
        a, b, g, mag = cart_to_alpha_beta_gamma(x, y, z)
        rows.append({
            "Vector": f"{i}",
            "X": round(x,2), "Y": round(y,2), "Z": round(z,2),
            "Kracht / |v| (N)": round(mag,2),
            "α (°) vanaf x-as": None if a is None else round(a,2),
            "β (°) vanaf y-as": None if b is None else round(b,2),
            "γ (°) vanaf z-as": None if g is None else round(g,2),
            "Kleur": color
        })

    Rx = sum(x for x,y,z in vectors)
    Ry = sum(y for x,y,z in vectors)
    Rz = sum(z for x,y,z in vectors)
    Ra, Rb, Rg, Rmag = cart_to_alpha_beta_gamma(Rx, Ry, Rz)
    rows.append({
        "Vector": "Resultante",
        "X": round(Rx,2), "Y": round(Ry,2), "Z": round(Rz,2),
        "Kracht / |v| (N)": round(Rmag,2),
        "α (°) vanaf x-as": None if Ra is None else round(Ra,2),
        "β (°) vanaf y-as": None if Rb is None else round(Rb,2),
        "γ (°) vanaf z-as": None if Rg is None else round(Rg,2),
        "Kleur": resultant_color
    })

    st.markdown("### Resultaten")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.markdown("### Uitleg (stap voor stap)")
    desc = []
    for i, ent in enumerate([e for e in st.session_state.entries if not is_blank(e)], start=1):
        if ent["mode"] == "dir":
            F = ent["force"] or 0.0
            a = ent["alpha"]; b = ent["beta"]; g = ent["gamma"]
            cx, cy, cz = math.cos(math.radians(a)), math.cos(math.radians(b)), math.cos(math.radians(g))
            X = F * cx; Y = F * cy; Z = F * cz
            desc.append(f"**Vector {i} (dir):** F={F:.2f} N, α={a:.2f}°, β={b:.2f}°, γ={g:.2f}° → X={X:.2f}, Y={Y:.2f}, Z={Z:.2f}")
        else:
            x0,y0,z0 = ent["x"], ent["y"], ent["z"]
            F = ent["force"] or 0.0
            base_mag = vec_norm(x0,y0,z0)
            if F > 0 and base_mag > 1e-12:
                s = F / base_mag
                X, Y, Z = x0*s, y0*s, z0*s
                desc.append(f"**Vector {i} (cart):** Basis=({x0:.2f},{y0:.2f},{z0:.2f}), F={F:.2f} N, s={s:.2f} → X={X:.2f}, Y={Y:.2f}, Z={Z:.2f}")
            else:
                desc.append(f"**Vector {i} (cart):** Direct (X,Y,Z)=({x0:.2f},{y0:.2f},{z0:.2f})")
    desc.append("**Som van componenten:**")
    desc.append("Rx = " + " + ".join([f"{x:.2f}" for x,_,_ in vectors]) + f" = {Rx:.2f}")
    desc.append("Ry = " + " + ".join([f"{y:.2f}" for _,y,_ in vectors]) + f" = {Ry:.2f}")
    desc.append("Rz = " + " + ".join([f"{z:.2f}" for _,_,z in vectors]) + f" = {Rz:.2f}")
    desc.append(f"**Resultante:** R=({Rx:.2f},{Ry:.2f},{Rz:.2f}), |R|={Rmag:.2f} N, hoeken: α={Ra:.2f}°, β={Rb:.2f}°, γ={Rg:.2f}°")
    st.markdown("\n\n".join(desc))

st.markdown("---")
st.caption("Assen door oorsprong, labels, rasterlijnen en zichtbaarheid van Plotly-assen kun je links instellen. Alle resultaten afgerond op 2 decimalen.")
