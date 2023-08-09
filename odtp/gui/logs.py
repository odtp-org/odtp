import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

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


st.write("ODTP Logs")
st.write("Mongo String")
mongoString = st.text_input("MongoString", value="mongodb://USER:PASS@10.95.48.38:27017/")
collection = st.text_input("Collection", value="logs")
mongoOK = st.button("Load Mongo Logs")

if mongoOK:
    docs = loadMongoLogs(mongoString, collection)
    st.json(docs)
