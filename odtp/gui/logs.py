import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from db import MongoManager

st.set_page_config(layout="wide")

if 'logs' not in st.session_state:
    st.session_state['logs'] = {}

if 'textlogs' not in st.session_state:
    st.session_state['textlogs'] = ""

def loadMongoLogs(mongoString, collection):
    # Connect to the MongoDB server. Replace 'localhost' with your server address and 27017 with your port if different.
    client = MongoClient(mongoString,  server_api=ServerApi('1'))

    # Connect to your database. Replace 'mydatabase' with your database name.
    db = client['odtp']

    # Connect to your collection. Replace 'mycollection' with your collection name.
    collection = db['logs']

    # Fetch all documents and store them in a list.
    documentList = list(collection.find())

    # Close the connection.
    client.close()

    return documentList


st.write("# ODTP Logs")

col1, col2 = st.columns(2)

with col1:
    st.write("Mongo String")
    mongoString = st.text_input("MongoString", value="mongodb://USER:PASS@10.95.48.38:27017/")
    collection = st.text_input("Collection", value="logs")
    digital_twin_index = st.number_input("Digital Twin Index", value=0)
    execution_index = st.number_input("Execution Index", value=0)
    step_index = st.number_input("Step Index", value=0)
    mongoOK = st.button("Load Mongo Logs")

    if mongoOK:
        mongo_manager = MongoManager(mongoString, "odtp")
        logs = mongo_manager.print_logs_by_indices(digital_twin_index, execution_index, step_index)
        print(logs)
        
        st.session_state['logs'] = logs
        st.session_state['textlogs'] = "".join([log["logstring"] + " \n" for log in logs])
    
    st.json(st.session_state['logs'])

with col2: 
    
    st.code(st.session_state['textlogs'])
