import streamlit as st

# Pagina-instellingen: geen sidebar tonen
st.set_page_config(page_title="🧭 Statica Toolbox", layout="wide", initial_sidebar_state="collapsed")

# Sidebar + hamburger-knop volledig verbergen
HIDE_SIDEBAR_CSS = """
<style>
    /* Verberg de sidebar en de toggle-knop */
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
    if st.button("🚀 3D Vector Visualisatie", use_container_width=True):
        try:
            # Streamlit ≥ 1.22
            st.switch_page("pages/1_3D_Vector_Visualisatie.py")
        except Exception:
            st.error("Kon niet schakelen via switch_page. Controleer of het bestand bestaat: pages/1_3D_Vector_Visualisatie.py")

with col2:
    st.subheader("In ontwikkeling")
    st.button("📦 Project 2 (binnenkort)", disabled=True, use_container_width=True)
    st.button("📦 Project 3 (binnenkort)", disabled=True, use_container_width=True)
    st.button("📦 Project 4 (binnenkort)", disabled=True, use_container_width=True)
    st.button("📦 Project 5 (binnenkort)", disabled=True, use_container_width=True)

st.markdown("---")
st.caption("De zijbalk is verborgen. Navigeren kan via de knoppen op deze pagina.")
