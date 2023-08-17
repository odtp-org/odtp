import streamlit as st

st.write("# ODTP dev platform")
st.markdown("""
            This is a GUI to support the development of ODTP. 
            It can:

            - Restart the folder structure in S3
            - Restart the schema in MONGODB
            - Visualize logs
            - Visualize and download files in S3
            - Visualize datasets in output.zip
            """)

#st.sidebar.image("img/logo.png", width=300)
from st_pages import show_pages_from_config

show_pages_from_config()