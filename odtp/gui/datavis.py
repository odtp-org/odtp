import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import pygwalker as pyg
 
# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="Data Visualization",
    layout="wide"
)
 
# Add Title
st.title("Data Visualization")


uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("Loaded")
    except Exception as e:
        st.write("Oops! There was an error: ", e)
 

loadB = st.button("Load")

if loadB:
    # Import your data
    #df = pd.read_csv("https://kanaries-app.s3.ap-northeast-1.amazonaws.com/public-datasets/bike_sharing_dc.csv")
    
    # Generate the HTML using Pygwalker
    pyg_html = pyg.walk(df, return_html=True)
    
    # Embed the HTML into the Streamlit app
    components.html(pyg_html, height=1000, scrolling=True)