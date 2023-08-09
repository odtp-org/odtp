import streamlit as st

st.write("ODTP dev platform")
st.markdown("List Components")

st.sidebar.image("img/logo.png", width=300)
from st_pages import show_pages_from_config

show_pages_from_config()