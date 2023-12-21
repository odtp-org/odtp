import os
from storage import s3Manager
from run import runManager
from db import MongoManager

from barfi import st_barfi, barfi_schemas, Block

# TODO: Extract barfi examples for 1 component run, 2 components run, Confluence 3 components, Divergence 3 components
# TODO: Upper method that created the execution document. 
    # def create_entry_in_db(self):
    #     # This will create a execution entry in the database. Maybe this needs to happen outside this method. 
    #     pass

class WorkflowManager:
    def __init__(self, barfi_schema):
        # This workflow will have one execution ID associated
        # This class should contain flags used to know the status of the workflow. 
        self.barfi_schema = barfi_schema

    def prepare_workflow(self):
        # This method will download all needed files and components to run the workflow
        # It will Build the images needed too. 
        pass

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

    def run_workflow(self):
        # Implement the logic to send tasks following the DAG schema. 
        # This can make use of barfi workflow execution function. Each 
        # call will make call of the run_task
        pass

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


