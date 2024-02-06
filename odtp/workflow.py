import os
from .storage import s3Manager
from .run import DockerManager
from .db import MongoManager
from .setup import odtpDatabase
import logging

from barfi import st_barfi, barfi_schemas, Block
import zipfile

# TODO: Extract barfi examples for 1 component run, 2 components run, Confluence 3 components, Divergence 3 components
# TODO: Upper method that created the execution document. 
    # def create_entry_in_db(self):
    #     # This will create a execution entry in the database. Maybe this needs to happen outside this method. 
    #     pass

class WorkflowManager:
    def __init__(self, execution_data, working_path):
        # This workflow will have one execution ID associated
        # This class should contain flags used to know the status of the workflow. 
        self.execution = execution_data
        self.schema = execution_data["workflowSchema"]
        self.working_path = working_path

        self.image_names = []
        self.repo_urls = []
        self.instance_names = []
        self.steps_folder_paths = []

        for step_index in self.schema["workflowExecutorSchema"]:
            step_index = int(step_index)

            component_id = self.schema["components"][step_index]["component"]
            version_id = self.schema["components"][step_index]["version"]

            odtpDB = odtpDatabase()
            component_doc = odtpDB.dbManager.get_document_by_id_as_dict(component_id, "components")
            odtpDB.close()

            odtpDB = odtpDatabase()
            version_doc = odtpDB.dbManager.get_document_by_id_as_dict(version_id, "versions")
            odtpDB.close()

            step_name = "{}_{}_{}".format(component_doc["componentName"], version_doc["version"], step_index)

            # Create folder structure
            step_folder_path = os.path.join(self.working_path, step_name)
            self.steps_folder_paths.append(step_folder_path)

            image_name = "{}_{}_{}".format(component_doc["componentName"], version_doc["version"], step_index)

            self.image_names.append(image_name)
            self.repo_urls.append(version_doc["commitHash"])
            self.instance_names.append(image_name)



    def prepare_workflow(self):
        # This method will download all needed files and components to run the workflow
        # It will Build the images needed too. 
        
        for step_index in self.schema["workflowExecutorSchema"]:
            step_index = int(step_index)

            # component_id = self.schema["components"][step_index]["component"]
            # version_id = self.schema["components"][step_index]["version"]

            # odtpDB = odtpDatabase()
            # component_doc = odtpDB.dbManager.get_document_by_id_as_dict(component_id, "components")
            # odtpDB.close()

            # odtpDB = odtpDatabase()
            # version_doc = odtpDB.dbManager.get_document_by_id_as_dict(version_id, "versions")
            # odtpDB.close()

            # step_name = "{}_{}_{}".format(component_doc["componentName"], version_doc["version"], step_index)

            # Create folder structure
            # step_folder_path = os.path.join(self.working_path, step_name)
            os.makedirs(self.steps_folder_paths[step_index], exist_ok=True)

            #self.steps_folder_paths.append(step_folder_path)

            #image_name = "{}_{}_{}".format(component_doc["componentName"], version_doc["version"], step_index)

            # By now the image_name is just the name of the component and the version
            componentManager = DockerManager(repo_url=self.repo_urls[step_index], 
                                    image_name=self.image_names[step_index], 
                                    project_folder=self.steps_folder_paths[step_index])
            
            componentManager.download_repo()
            componentManager.build_image()

            logging.info("COMPONENTS DOWNLOADED AND BUILT")

    def download_data_from_storage(self):
        # Implement the logic to download data from S3
        pass

    def download_and_build_components(self):
        # This method will clone the githubs and build the components.
        pass

    def extract_parameters(self):
        # Implement the logic to extract parameters from the Barfi schema
        # THese parameters will be send as environment variable.
        self.paramenters = {}
        pass

    def run_workflow(self, env_files):
        # Implement the logic to send tasks following the DAG schema. 
        # This can make use of barfi workflow execution function. Each 
        # call will make call of the run_task

        # Temporally the parameters are taken from the environment files and not 
        # taken from the steps documents
        logging.info(self.steps_folder_paths)
        for step_index in self.schema["workflowExecutorSchema"]:
            step_index = int(step_index)

            step_id = self.execution["steps"][step_index]

            odtpDB = odtpDatabase()
            step_doc = odtpDB.dbManager.get_document_by_id_as_dict(step_id, "steps")
            odtpDB.close()

            ports = step_doc["ports"]


            # Copying the compressed output files into the new input ones
            # Extracting the files
            if step_index !=0:
                previous_output_path = os.path.join(self.steps_folder_paths[step_index-1], "odtp-output")

                # Specify the path to the output.zip file and the actual_input_path
                output_zip_path = os.path.join(previous_output_path, 'odtp-output.zip')
                actual_input_path = os.path.join(self.steps_folder_paths[step_index], 'odtp-input')

                logging.info(output_zip_path)
                logging.info(actual_input_path)
                
                # Extract the contents of the output.zip file into the actual_input_path
                with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(actual_input_path)

                # List the contents of the actual_input_path directory
                contents = os.listdir(actual_input_path)
                logging.info(f"Contents of the folder: {contents}")


            # Change image_name by Component ID_version
            # image_name = "{}_{}_{}".format(component_doc["componentName"], version_doc["version"], step_index)
            # By now the image_name is just the name of the component and the version
            componentManager = DockerManager(repo_url=self.repo_urls[step_index], 
                                    image_name=self.image_names[step_index], 
                                    project_folder=self.steps_folder_paths[step_index])
            
            # instance_name = "{}_{}".format(component_doc["componentName"], version_doc["version"])
            logging.info(env_files[step_index])
            componentManager.run_component(env_files[step_index],
                                           ports=ports,
                                           instance_name=self.instance_names[step_index],
                                           step_id=self.execution["steps"][step_index])


    def run_task(self):
        # Implement the logic of running one single task. 
        # Send the step ID as Environment variable so the component can log the progress
        pass

    def stop_workflow(self):
        # This will stop the execution of the workflow. 
        pass

    def stop_task(self):
        # This will stop one single task
        pass

    def delete_workflow(self):
        # This method will delete all records in the DB and related docker components downloaded in the folder. 
        pass

    def delete_db_entry(self):
        # Method to remove the workflow execution from the database
        pass

    def delete_docker_components(self):
        # Method to remove all docker containers used by this workflow.
        pass

    def restart_workflow(self):
        # This will restart the execution of the workflow. 
        pass

class BarfiManager:
    """This class check all the components available in the components database, and prepare the Barfi class"""
    def __init__(self):
        self.blocks = []
        pass

    def addBlock(self, name, inputs, outputs, options, dockerfunc):
        b = Block(name="name")
        for option in options:
            # Different types of blocks contains different options parameters
            if option["type"] == "display":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"])
            elif option["type"] == "select":
                b.add_option(name=option["name"],
                            type=option["type"],
                            value=option["value"],
                            items=option["items"])
            elif option["type"] == "input":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"])
            elif option["type"] == "integer":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"])
            elif option["type"] == "checkbox":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"])
            elif option["type"] == "slider":
                b.add_option(name=option["name"],
                             type=option["type"],
                             value=option["value"],
                             min=option["min"],
                             max=option["max"])
                
        for input in inputs:
            b.add_input(name=input["name"])

        for output in outputs:
            b.add_output(name=output["name"])

        def barfiFunc(self):
            # Here we need to build the docker method that will be send to run
            envStringList = []
            for option in options:
                optionValue = self.get_option(name=option["name"])
                envStringList.append("{}={}".format(option['name'], optionValue))


            # Actually Inputs/Outputs will not be managed by Barfi
            for input in inputs:
                inputValue = self.get_interface(name=input["name"])
                # Need to be copied in a folder. How this works on Barfi?

            for output in outputs:
                self.set_interface(name=output["name"], 
                                   value=output["value"])

            # Run the Component
            # 1. Copy input files
            # 2. Run component

        b.add_compute(barfiFunc)
            
        self.blocks.append(b)


