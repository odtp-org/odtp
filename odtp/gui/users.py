import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

st.markdown("# Users")

def getDTInMongoDB(mongoString):
    # Connect to the MongoDB server. Replace 'localhost' with your server address and 27017 with your port if different.
    client = MongoClient(mongoString,  server_api=ServerApi('1'))

    # Connect to your database. Replace 'mydatabase' with your database name.
    db = client['odtp']

    # Connect to your collection. Replace 'mycollection' with your collection name.
    collection = db['users']

    # Fetch all documents and store them in a list.
    documentList = list(collection.find())

    # Close the connection.
    client.close()

    return documentList

st.markdown("## Users Registered")
mongoString = st.text_input("MongoString", value="mongodb://USER:PASS@10.95.48.38:27017/")
mdbbutton = st.button("Get users entries in MongoDB")

if mdbbutton:
    mdbOut = getDTInMongoDB(mongoString)
    st.json(mdbOut)


##########################

import pandas as pd 
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

data = {"username": ["userA","userB"],
        "role": ["administrator", "user"],
        "projects": [["A","B"],["B","C"]]}

df=pd.DataFrame(data)
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_grid_options(domLayout='normal')
gridOptions = gb.build()


grid_response = AgGrid(
    df, 
    gridOptions=gridOptions,
    height=300, 
    width='100%',
    data_return_mode="FILTERED", 
    update_mode='GRID_CHANGED',
    fit_columns_on_grid_load=False,
    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
    enable_enterprise_modules=False
    )