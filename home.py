import streamlit as st

# Pagina-instellingen: geen sidebar tonen
st.set_page_config(page_title="🧭 Statica Toolbox", layout="wide", initial_sidebar_state="collapsed")

# Sidebar + hamburger-knop volledig verbergen
HIDE_SIDEBAR_CSS = """
<style>
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
</style>
"""
st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)

# ----------------------------
# Home UI
# ----------------------------
st.title("🧭 Statica Toolbox")
st.markdown("Welkom. Kies een module hieronder.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Beschikbaar")

    # 3D
    if st.button("🚀 3D Vector Visualisatie", use_container_width=True):
        try:
            st.switch_page("pages/1_3D_Vector_Visualisatie.py")
        except Exception:
            st.error("Kon niet schakelen via switch_page. Bestaat 'pages/1_3D_Vector_Visualisatie.py'?")

    # 2D
    if st.button("🟦 2D Vector Visualisatie", use_container_width=True):
        try:
            st.switch_page("pages/2_2D_Vector_Visualisatie.py")
        except Exception:
            st.error("Kon niet schakelen naar 2D. Bestaat 'pages/2_2D_Vector_Visualisatie.py'?")

with col2:
    st.subheader("In ontwikkeling")
    st.button("📦 Project 3 (binnenkort)", disabled=True, use_container_width=True)
    st.button("📦 Project 4 (binnenkort)", disabled=True, use_container_width=True)
    st.button("📦 Project 5 (binnenkort)", disabled=True, use_container_width=True)

st.markdown("---")

