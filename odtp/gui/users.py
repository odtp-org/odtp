import streamlit as st
from odtp.setup import odtpDatabase
import pandas as pd

from odtp.mongodb.db import MongoManager

st.set_page_config(layout="wide")

def get_digital_twins():
    with odtpDatabase() as dbManager:
        documents = dbManager.get_all_documents("digitalTwins")
    print(documents)

    return documents

def get_users():
    with odtpDatabase() as dbManager:
        documents = dbManager.get_all_documents("users")
    print(documents)

    return documents


if 'users_df' not in st.session_state:
    st.session_state['users_df'] = pd.DataFrame({})

if 'users_email' not in st.session_state:
    st.session_state['users_email'] = ["None"]

if 'users_id' not in st.session_state:
    st.session_state['users_id'] = []

if 'digital_twins_df' not in st.session_state:
    st.session_state['digital_twins_df'] = pd.DataFrame({})



st.markdown("# Users")
st.markdown("## Users Registered")
mongoString = st.text_input("MongoString", value="mongodb://USER:PASS@10.95.48.38:27017/")


with st.form("users_registed"):
    mdbbutton = st.form_submit_button("Get users entries in MongoDB")
    if mdbbutton:
        st.write("Loading users")

        all_users = get_users()
        users_df = pd.DataFrame(all_users)
        
        st.session_state['users_df'] = users_df
        st.session_state['users_id'] = list(users_df['_id'])
        st.session_state['users_email'] = list(users_df['email'])

        st.write(st.session_state)

st.dataframe(st.session_state['users_df'])

all_digital_twins = get_digital_twins()
digital_twin_df = pd.DataFrame(all_digital_twins)
print(digital_twin_df)
#st.write(digital_twin_df)

# if mdbbutton:
#     # mdbOut = getDTInMongoDB(mongoString)
#     # st.json(mdbOut)
#     mongo_manager = MongoManager(mongoString, "odtp")
#     all_users = mongo_manager.get_all_users()
#     users_df = pd.DataFrame(all_users)
#     st.dataframe(users_df)

"""
st.write("## Digital Twins Entries")
with st.form("digital_twins_registered"):
    index_selected = st.selectbox('Select one user to check the associated digital twins.', 
                                  range(len(st.session_state['users_email'])),
                                  format_func=lambda x: st.session_state['users_email'][x])
    print(st.session_state['users_id'])
    submit = st.form_submit_button("Load DTs")
    if submit:
        st.write("Loading DTs")
        mongo_manager = MongoManager(mongoString, "odtp")
        digital_twins_by_user = mongo_manager.get_digital_twins_by_user_id(
            st.session_state['users_id'][index_selected])
        digital_twins_df = pd.DataFrame(digital_twins_by_user)
        st.session_state['digital_twins_df'] = digital_twins_df

        # Add len of
        st.write(st.session_state)

st.dataframe(st.session_state['digital_twins_df'])

"""
# ##########################

# import pandas as pd 
# from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

# data = {"username": ["userA","userB"],
#         "role": ["administrator", "user"],
#         "projects": [["A","B"],["B","C"]]}

# df=pd.DataFrame(data)
# gb = GridOptionsBuilder.from_dataframe(df)
# gb.configure_grid_options(domLayout='normal')
# gridOptions = gb.build()


# grid_response = AgGrid(
#     df, 
#     gridOptions=gridOptions,
#     height=300, 
#     width='100%',
#     data_return_mode="FILTERED", 
#     update_mode='GRID_CHANGED',
#     fit_columns_on_grid_load=False,
#     allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
#     enable_enterprise_modules=False
#     )