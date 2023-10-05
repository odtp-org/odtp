import streamlit as st
import boto3
from pymongo import MongoClient
from pymongo.server_api import ServerApi

st.write("# Snapshots/Output Available")


def getSnapshotsInS3(pathPrefix, bucketName, s3ClientString, accessKey, secretKey):
    s3 = boto3.client('s3', endpoint_url=s3ClientString,
                      aws_access_key_id=accessKey, 
                      aws_secret_access_key=secretKey)


    paginator = s3.get_paginator('list_objects_v2')

    snapshotPaths = []

    for page in paginator.paginate(Bucket=bucketName, Prefix=pathPrefix):
        for obj in page.get('Contents', []):
            if obj['Key'].endswith('.zip'):  # Filtering out snapshot files. You can adjust the condition based on your need.
                snapshotPaths.append(obj['Key'])

    return snapshotPaths



def getSnapshotsInMongoDB(mongoString):
    # Connect to the MongoDB server. Replace 'localhost' with your server address and 27017 with your port if different.
    client = MongoClient(mongoString,  server_api=ServerApi('1'))

    # Connect to your database. Replace 'mydatabase' with your database name.
    db = client['odtp']

    # Connect to your collection. Replace 'mycollection' with your collection name.
    collection = db['snapshots']

    # Fetch all documents and store them in a list.
    documentList = list(collection.find())

    # Close the connection.
    client.close()

    return documentList

col1, col2 = st.columns(2)

with col1:
    st.markdown("## MongoDB Entries")
    mongoString = st.text_input("MongoString", value="mongodb://USER:PASS@10.95.48.38:27017/")
    mdbbutton = st.button("Get snapshots entries in MongoDB")

    if mdbbutton:
        mdbOut = getSnapshotsInMongoDB(mongoString)
        st.json(mdbOut)


with col2:
    ################################
    st.markdown("## S3 Files")
    s3ClientString = st.text_input("clientString", value="https://s3.epfl.ch")
    bucketName=st.text_input("bucketName", value="13301-6bcec4f9e8e75c799891ee1a336725ec")
    accessKey=st.text_input("accessKey", value="Q0ISQFAAKTVB9J3VAQJF")
    secretKey=st.text_input("secretKey")

    s3button = st.button("Get Zip files in S3 snapshot")

    if s3button:
        s3out = getSnapshotsInS3("odtp/odtp-snapshots", bucketName, s3ClientString, accessKey, secretKey)
        st.json(s3out)


## TODO: Turn it into a table and provide link to donwload


class S3PresignedURLGenerator:
    def __init__(self, s3ClientString, access_key, secret_key):
        self.s3 = boto3.client('s3',  endpoint_url=s3ClientString,
                               aws_access_key_id=access_key, 
                               aws_secret_access_key=secret_key)

    def generate_url(self, bucket_name, object_key, expiration=3600):
        """Generate a presigned URL for downloading an S3 object.

        :param bucket_name: Name of the S3 bucket.
        :param object_key: Key of the object within the S3 bucket.
        :param expiration: Expiration time for the URL in seconds. Default is 1 hour.
        :return: Presigned URL string.
        """
        url = self.s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name, 'Key': object_key},
                                             ExpiresIn=expiration)
        return url
    
fileToDownload = st.text_input("File to Download", value=None)
downloadbutton = st.button("Get presigned Link")


if downloadbutton:
    generator = S3PresignedURLGenerator(s3ClientString, accessKey, secretKey)
    url = generator.generate_url(bucketName, fileToDownload)
    st.write(f"[Click here to download]({url})")





