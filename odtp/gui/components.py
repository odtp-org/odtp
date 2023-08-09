import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi


st.set_page_config(
    page_title="ODPT",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.markdown("# Components")

def getDTInMongoDB(mongoString):
    # Connect to the MongoDB server. Replace 'localhost' with your server address and 27017 with your port if different.
    client = MongoClient(mongoString,  server_api=ServerApi('1'))

    # Connect to your database. Replace 'mydatabase' with your database name.
    db = client['odtp']

    # Connect to your collection. Replace 'mycollection' with your collection name.
    collection = db['components']

    # Fetch all documents and store them in a list.
    documentList = list(collection.find())

    # Close the connection.
    client.close()

    return documentList

st.markdown("## Components Available")
mongoString = st.text_input("MongoString", value="mongodb://USER:PASS@10.95.48.38:27017/")
mdbbutton = st.button("Get components entries in MongoDB")

if mdbbutton:
    mdbOut = getDTInMongoDB(mongoString)
    st.json(mdbOut)


from streamlit_card import card

columns = st.columns(4,gap="small")

for i,c in enumerate(columns):
    with c:
        hasClicked = card(
        title="Hello World!",
        text="Some description",
        image="http://placekitten.com/150/200",
        url="https://github.com/gamcoh/st-card",
        styles={
        "card": {
            "width": "250px",
            "height": "200px",
            "border-radius": "10px",
            "box-shadow": "0 0 5px rgba(0,0,0,0.5)",
        },},
        key=str(i)
        )

columns = st.columns(4,gap="small")

for i,c in enumerate(columns):
    with c:
        hasClicked = card(
        title="Hello World!",
        text="Some description",
        image="http://placekitten.com/150/200",
        url="https://github.com/gamcoh/st-card",
        styles={
        "card": {
            "width": "250px",
            "height": "200px",
            "border-radius": "10px",
            "box-shadow": "0 0 5px rgba(0,0,0,0.5)",
        },},
        key=str(i+4)
        )