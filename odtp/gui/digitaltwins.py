import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

st.write("Digital Twins")

def getDTInMongoDB(mongoString):
    # Connect to the MongoDB server. Replace 'localhost' with your server address and 27017 with your port if different.
    client = MongoClient(mongoString,  server_api=ServerApi('1'))

    # Connect to your database. Replace 'mydatabase' with your database name.
    db = client['odtp']

    # Connect to your collection. Replace 'mycollection' with your collection name.
    collection = db['digitalTwins']

    # Fetch all documents and store them in a list.
    documentList = list(collection.find())

    # Close the connection.
    client.close()

    return documentList

st.markdown("## MongoDB Entries")
mongoString = st.text_input("MongoString", value="mongodb://USER:PASS@10.95.48.38:27017/")
mdbbutton = st.button("Get Digital Twins entries in MongoDB")

if mdbbutton:
    mdbOut = getDTInMongoDB(mongoString)
    st.json(mdbOut)
