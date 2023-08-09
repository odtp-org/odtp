import streamlit as st

st.markdown("# Semantics")
st.write("## Access to GraphDB?")

## Introduce tab with Query. 

graphDBURL = st.text_input("Insert GraphDB API Endpoint")
graphDBUser = st.text_input("Insert GraphDB Username")
graphDBPassword = st.text_input("Insert GraphDB Password")
pingGDB = st.button("Ping GraphDB")
if pingGDB:
    st.write("Connection tried")

st.markdown("## Preloaded queries")
tab1, tab2, tab3 = st.tabs(["New Query", "Query A", "Query B"])
with tab1: 
    st.text_area("Write Query")
    query1 = st.button("Query 1")
    if query1:
        st.json({"Output":"data"})

with tab2: 
    st.text_area("Query A", value="TEST TEST TEST")
    query2 = st.button("Query 2")
    if query2:
        st.json({"Output":"data"})

with tab3: 
    st.text_area("Query B", value="TEST TEST TEST")
    query3 = st.button("Query 3")
    if query3:
        st.json({"Output":"data"})


## Run validation

## Swiss Data Custodian


