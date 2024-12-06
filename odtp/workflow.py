import os
from odtp.run import DockerManager, OdtpRunSetupException
import odtp.helpers.utils as odtp_utils
import odtp.helpers.settings as config
import odtp.helpers.environment as env_helpers
import odtp.mongodb.db as db
import logging
import zipfile

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(config.get_command_log_handler())


class WorkflowManager:
    def __init__(self, execution_data, working_path, secrets):
        # This workflow will have one execution ID associated
        # This class should contain flags used to know the status of the workflow. 
        self.execution = execution_data
        self.schema = execution_data["workflowSchema"]
        self.working_path = working_path
        self.docker_image_names = []
        self.docker_image_links = []
        self.repo_urls = []
        self.commits = []
        self.container_names = []
        self.steps_folder_paths = []
        self.secrets = secrets

        for step_index in self.schema["workflowExecutorSchema"]:
            try: 
                step_index = int(step_index)

                version_id = self.schema["component_versions"][step_index]
                version_doc = db.get_document_by_id(
                    document_id=version_id, 
                    collection=db.collection_versions
                )
                component_name = version_doc["component"]["componentName"]
                component_version = version_doc["component_version"]
                repo_link = version_doc["component"]["repoLink"]
                image_link = version_doc["imageLink"]
                commit_hash = version_doc["commitHash"]

                step_name = odtp_utils.get_execution_step_name(
                    component_name=component_name, 
                    component_version=component_version, 
                    step_index=step_index
                )
                
                # Create folder structure
                step_folder_path = os.path.join(self.working_path, step_name)
                self.steps_folder_paths.append(step_folder_path)

                image_name = odtp_utils.get_execution_step_image_name(
                    component_name=component_name, 
                    component_version=component_version
                )

                self.docker_image_names.append(image_name)
                self.docker_image_links.append(image_link)
                self.repo_urls.append(repo_link)
                self.commits.append(commit_hash)
                self.container_names.append(step_name)
            except Exception as e:
                raise OdtpRunSetupException(
                    f"Workflowmanager could not be intialized: Exception occured: {e}"
                )    
    

    def check_env_for_prepare_workflow(self):
        env_helpers.check_project_folder_empty(self.working_path)


    def prepare_workflow(self):
        """
        This method will download all needed files and components to run the workflow
        It will Build the images needed too. 
        """  
        self.check_env_for_prepare_workflow()
        for step_index in self.schema["workflowExecutorSchema"]:
            step_index = int(step_index)

            # Create folder structure
            # step_folder_path = os.path.join(self.working_path, step_name)
            os.makedirs(
                self.steps_folder_paths[step_index], 
                exist_ok=True
            )

            # By now the image_name is just the name of the component and the version
            componentManager = DockerManager(
                repo_url=self.repo_urls[step_index],
                commit_hash=self.commits[step_index],
                image_name=self.docker_image_names[step_index],
                image_link=self.docker_image_links[step_index],
                project_folder=self.steps_folder_paths[step_index]
            )

            componentManager.prepare_component()

            log.info("COMPONENTS DOWNLOADED AND BUILT")

    def run_workflow(self):
        # Implement the logic to send tasks following the DAG schema. 
        # This can make use of barfi workflow execution function. Each 
        # call will make call of the run_task

        # Temporally the parameters are taken from the environment files and not 
        # taken from the steps documents

        # Start execution timestamp
        db.set_document_timestamp(self.execution["_id"], db.collection_executions, "start_timestamp")

        for step_index in self.schema["workflowExecutorSchema"]:
            log.info(f"running step {step_index}")
            step_index = int(step_index)

            step_id = self.execution["steps"][step_index]

            # Start step timestamp
            db.set_document_timestamp(step_id, db.collection_steps, "start_timestamp")

            secrets = self.secrets[step_index]

            step_doc = db.get_document_by_id(
                document_id=step_id, 
                collection=db.collection_steps
            )

            ports = step_doc["ports"]
            log.info(f"set ports {ports}")
            parameters = step_doc["parameters"]
            log.info(f"set parameters {parameters}")

            # Copying the compressed output files into the new input ones
            # Extracting the files
            if step_index !=0:
                log.info(f"get output from previous step {step_index-1}")
                previous_output_path = os.path.join(self.steps_folder_paths[step_index-1], "odtp-output")

                # Specify the path to the output.zip file and the actual_input_path
                output_zip_path = os.path.join(previous_output_path, 'odtp-output.zip')
                actual_input_path = os.path.join(self.steps_folder_paths[step_index], 'odtp-input')
                
                # Extract the contents of the output.zip file into the actual_input_path
                if output_zip_path:
                    log.info(f"output found at {output_zip_path}")
                    with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
                        zip_ref.extractall(actual_input_path)
                else:
                    log.info(f"no output found from step {step_index-1}. Did it run with success?")

                # List the contents of the actual_input_path directory
                contents = os.listdir(actual_input_path)
                log.info(f"Contents of the folder: {contents}")


            # Change image_name by Component ID_version
            # image_name = "{}_{}_{}".format(step_index, component_doc["componentName"], version_doc["version"])
            # By now the image_name is just the name of the component and the version
            componentManager = DockerManager(
                repo_url=self.repo_urls[step_index], 
                image_name=self.docker_image_names[step_index],
                project_folder=self.steps_folder_paths[step_index]
            )
            
            # instance_name = "{}_{}".format(component_doc["componentName"], version_doc["version"])
            #log.info(env_files[step_index])
            log.info(f"run docker image {self.docker_image_names[step_index]} at path {self.steps_folder_paths[step_index]}")
            componentManager.run_component(
                parameters,
                secrets,
                ports=ports,
                container_name=self.container_names[step_index],
                step_id=self.execution["steps"][step_index]
            )
            
            # End step timestamp
            db.set_document_timestamp(step_id, db.collection_steps, "end_timestamp")

        # End execution timestamp
        db.set_document_timestamp(self.execution["_id"], db.collection_executions, "end_timestamp")