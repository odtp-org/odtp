import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import boto3
import ast

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

st.write("# Init section")
st.write("This section is for rebooting all the services that make the ODTP")

col1, col2 = st.columns(2)

# This is to provide an easy configuration and reseting of MONGODB and the S3 Enviroment

#################################################################################

def createCollections(mongoString, collectionsToCreate):
    # Connect to the MongoDB server. Replace 'localhost' with your server address and 27017 with your port if different.
    client = MongoClient(mongoString,  server_api=ServerApi('1'))
    st.write(client)

    db = client["odtp"]

    # List of collection names you want to create.
    collectionsToCreate = ast.literal_eval(collectionsToCreate)

    for coll_name in collectionsToCreate:
        # This will create a new collection or will do nothing if the collection already exists.
        db.create_collection(coll_name)

    print("Collections created!")

    # Close the connection.
    client.close()

def deleteCollections(mongoString):
    # Connect to the MongoDB server. Replace 'localhost' with your server address and 27017 with your port if different.
    client = MongoClient(mongoString,  server_api=ServerApi('1'))

    # Connect to your database. Replace 'mydatabase' with your database name.
    db = client["odtp"]

    # Get a list of all collections in the database
    collections = db.list_collection_names()

    # Drop each collection
    for collection in collections:
        db.drop_collection(collection)

    print("All collections dropped!")

    # Close the connection.
    client.close()

def checkCollections(mongoString):
    client = MongoClient(mongoString,  server_api=ServerApi('1'))
    st.write(client)
    db = client["odtp"]
    st.write(client)

    # Fetch the names of all collections
    collection_names = db.list_collection_names()
    st.write(collection_names)

    return collection_names

    # Close the connection.
    client.close()

with col1: 
    st.markdown("## MongoDB")

    mongoString = st.text_input("MongoString", value="mongodb://USER:PASS@10.95.48.38:27017/")
    collectionsText = st.text_input("Introduce collections to create", value=['logs', 'users', 'components', 'snapshots', 'digitalTwins'])
    create = st.button("Create Collections on MongoDB")
    delete = st.button("Delete Collections on MongoDB")
    check = st.button("Check Collections on MongoDB")

    if create:
        createCollections(mongoString, collectionsText)
        st.write("Collections Created")

    if delete:
        deleteCollections(mongoString)
        st.write("Collections Deleted")

    if check:
        coll = checkCollections(mongoString)
        st.write("Collections Check")
        st.json(coll)


####################################################

def createFolderStructure(s3ClientString, bucketName, structure,  accessKey, secretKey):
    s3 = boto3.client('s3', endpoint_url=s3ClientString,
                      aws_access_key_id=accessKey, 
                      aws_secret_access_key=secretKey)

    for path in structure:
        # Add a trailing slash to make S3 recognize it as a folder
        s3.put_object(Bucket=bucketName, Key=path + '/')

    print("Folder Structure Created")

def deleteAllObjects(s3ClientString, bucketName, accessKey, secretKey):
    s3 = boto3.resource('s3', endpoint_url=s3ClientString,
                      aws_access_key_id=accessKey, 
                      aws_secret_access_key=secretKey)
    
    bucket = s3.Bucket(bucketName)
    
    # This will delete all objects in the bucket.
    bucket.objects.all().delete()

    print("Folder Structure Deleted")

def checkObjects(s3ClientString, bucketName, accessKey, secretKey):

    s3 = boto3.client('s3', endpoint_url=s3ClientString,
                      aws_access_key_id=accessKey, 
                      aws_secret_access_key=secretKey)
    
    response = s3.list_objects_v2(Bucket=bucketName, Delimiter='/')
    
    folders = []
    if 'CommonPrefixes' in response:
        for prefix in response['CommonPrefixes']:
            folders.append(prefix['Prefix'])
            
    return folders


with col2:
    st.markdown("## S3")

    folderStructure = [
        'odtp',
        'odtp/snapshots'
    ]

    s3ClientString = st.text_input("clientString", value="https://s3.epfl.ch")
    bucketName=st.text_input("bucketName", value="13301-6bcec4f9e8e75c799891ee1a336725ec")
    accessKey=st.text_input("accessKey", value="Q0ISQFAAKTVB9J3VAQJF")
    secretKey=st.text_input("secretKey", type="password")
    structure=st.text_area("structure", value=folderStructure)

    createBucketStructure = st.button("createBucketStructure")
    deleteBucketStructure = st.button("deleteBucketStructure")
    checkBucketStructure = st.button("checkBucketStructure")

    if createBucketStructure:
        structure = ast.literal_eval(structure)
        createFolderStructure(s3ClientString, bucketName, structure, accessKey, secretKey)

    if deleteBucketStructure:
        structure = ast.literal_eval(structure)
        deleteAllObjects(s3ClientString, bucketName, accessKey, secretKey)

    if checkBucketStructure:
        objects = checkObjects(s3ClientString, bucketName, accessKey, secretKey)
        st.json(objects)

    