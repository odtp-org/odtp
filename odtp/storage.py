import boto3
import logging
from odtp.helpers import settings


log = logging.getLogger(__name__)


class s3Manager:
    def __init__(self):
        self.s3 = boto3.client('s3',
            endpoint_url=settings.ODTP_S3_SERVER,
            aws_access_key_id=settings.ODTP_ACCESS_KEY,
            aws_secret_access_key=settings.ODTP_SECRET_KEY
        )
        self.bucketName = settings.ODTP_BUCKET_NAME

    def test_connection(self):
        bucket = self.s3.head_bucket(Bucket=self.bucketName)
        return bucket    

    # Method to close the client connection
    def closeConnection(self):
        """
        Closes the connection to the S3 client.
        """
        self.s3.meta.client.close()
        log.info("Connection closed")

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
        log.info(f"Folder '{path}' created")

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
        log.info(f"File '{local_path}' uploaded to '{s3_path}'")

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
        log.info(f"File '{s3_path}' downloaded to '{local_path}'")

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
        log.info(f"File '{s3_path}' deleted from S3 bucket")

    def create_folders(self, structure):
        self.s3.createFolderStructure(structure)
        log.info("Folder structure generated")

    def close(self):
        del self.s3
        log.info("S3 Session deleted")
