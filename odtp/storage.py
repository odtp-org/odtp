# Here is where all  the s3Manager related methods should be placed.

# Env variables needed: 


# Some previous methods

####################################################

import boto3
import logging

class s3Manager:
    def __init__(self, s3ClientString, bucketName, accessKey, secretKey):
        self.s3ClientString = s3ClientString
        self.bucketName = bucketName
        self.accessKey = accessKey
        self.secretKey = secretKey

        self.connect()

        # Add logging Info
        
    # Method to connect to s3 server
    def connect(self):
        s3 = boto3.client('s3', endpoint_url=self.s3ClientString,
                    aws_access_key_id=self.accessKey, 
                    aws_secret_access_key=self.secretKey)
        
        self.s3 = s3 

        # Add logging info

    # Method to close the client connection
    def closeConnection(self):
        """
        Closes the connection to the S3 client.
        """
        self.s3.meta.client.close()
        logging.info("Connection closed")

    # Create folder structure
    def createFolderStructure(self, structure=["odtp"]):
        """
        structure: is a list of paths to create. By default a single "odtp" folder
        """

        for path in structure:
            # Add a trailing slash to make S3 recognize it as a folder
            self.s3.put_object(Bucket=self.bucketName, Key=path + '/')

        print("Folder Structure Created")

    # Method to create a specific folder 
    # The idea is to create paths such as Digital Twin > Execution > Step > Output 
    def createFolder(self, path):
        """
        Creates a specific folder in the S3 bucket.

        Args:
            path (str): The path of the folder to create.

        Returns:
            None
        """
        self.s3.put_object(Bucket=self.bucketName, Key=path + '/')
        logging.info(f"Folder '{path}' created")

    # Method to upload one file to specific path in s3
    def uploadFile(self, local_path, s3_path):
        """
        Uploads a file to a specific path in the S3 bucket.

        Args:
            local_path (str): The local path of the file to upload.
            s3_path (str): The S3 path where the file should be uploaded.

        Returns:
            None
        """
        self.s3.upload_file(local_path, self.bucketName, s3_path)
        logging.info(f"File '{local_path}' uploaded to '{s3_path}'")

    # Method to download one file from s3 and place it in a folder
    # This is needed to make the input/output logic out of barfi
    def downloadFile(self, s3_path, local_path):
        """
        Downloads a file from a specific path in the S3 bucket and saves it locally.

        Args:
            s3_path (str): The S3 path of the file to download.
            local_path (str): The local path where the file should be saved.

        Returns:
            None
        """
        self.s3.download_file(self.bucketName, s3_path, local_path)
        logging.info(f"File '{s3_path}' downloaded to '{local_path}'")

    # Method to list folders in s3
    def checkObjects(self):

        response = self.s3.list_objects_v2(Bucket=self.bucketName, 
                                           Delimiter='/')
        
        folders = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                folders.append(prefix['Prefix'])
                
        return folders

    # Method to delete all objects in s3
    def deleteAll(self):
        
        bucket = self.s3.Bucket(self.bucketName)
        
        # This will delete all objects in the bucket.
        bucket.objects.all().delete()

        print("Folder Structure Deleted")

    # Method to delete one file in s3 
    def deleteFile(self, s3_path):
    
        """
        Deletes a file from a specific path in the S3 bucket.

        Args:
            s3_path (str): The S3 path of the file to delete.

        Returns:
            None
        """
        self.s3.delete_object(Bucket=self.bucketName, Key=s3_path)
        logging.info(f"File '{s3_path}' deleted from S3 bucket")

    def close(self):
        del self.s3
        logging.info("S3 Session deleted")