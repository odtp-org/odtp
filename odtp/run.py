import logging
import os
import json
import subprocess
import odtp.helpers.settings as config
import odtp.helpers.git as git_helpers
import odtp.helpers.environment as env_helpers
import odtp.mongodb.utils as db_utils
import odtp.mongodb.db as db


REPO_DIR = "repository"
INPUT_DIR = "odtp-input"
OUTPUT_DIR = "odtp-output"


class OdtpRunSetupException(Exception):
    pass


class DockerManager:
    def __init__(self, repo_url="", commit_hash="", image_name="", project_folder=""):
        logging.info(f"""Docker manager intialized with repo_url: {repo_url},
                     commit_hash: {commit_hash}, project_folder: {project_folder}, image_name: {image_name}""")
        self.repo_url = repo_url
        self.commit_hash = commit_hash
        self.project_folder = project_folder
        self.repository_path = os.path.join(self.project_folder, REPO_DIR)
        self.dockerfile_path = os.path.join(self.project_folder, REPO_DIR)
        self.docker_image_name = image_name
        self.input_volume = os.path.join(self.project_folder, INPUT_DIR)
        self.output_volume = os.path.join(self.project_folder, OUTPUT_DIR)

    def prepare_component(self):
        self._checks_for_prepare()
        self._create_project_folder_structure()
        self._download_repo()
        self._build_image()    

    def _create_project_folder_structure(self):
        """Create all the folder structure in project_folder""" 
        logging.info("PREPARE create project folder structure")
        os.makedirs(self.repository_path, exist_ok=True)
        os.makedirs(self.input_volume, exist_ok=True)
        os.makedirs(self.output_volume, exist_ok=True)    
    
    def _check_project_folder_prepared(self):  
        logging.info("VALIDATION: check project folder structure")  
        """check whether the project folder is prepared with the expected 
        structure of repository_path, input and output volume"""
        subdirs = []
        with os.scandir(self.project_folder) as entries:
            for entry in entries:
                if entry.is_dir():
                    subdirs.append(entry.name)
        if set(subdirs) != set(REPO_DIR, INPUT_DIR, OUTPUT_DIR):
            raise OdtpRunSetupException(
                f"""project folder {self.project_folder} does not have 
                expected directory structure with {REPO_DIR}, {INPUT_DIR}, {OUTPUT_DIR}"""
            )
        
    def _checks_for_prepare(self):
        logging.info("VALIDATION: check for prepare") 
        env_helpers.check_project_folder_empty(self.project_folder)
        self.commit_hash = git_helpers.check_commit_for_repo(
            repo_url=self.repo_url, 
            commit_hash=self.commit_hash
        )

    def _checks_for_run(self, parameters, ports, image_name):
        logging.info("VALIDATION: check for run") 
        self._check_project_folder_prepared()
        self._check_image_exists()
        try:
            json.dumps(parameters)
        except Exception as e:
            raise OdtpRunSetupException(f"parameters are not transformable to json: {parameters}")
        
        db_utils.check_ports_for_component(ports)
        self._check_image_exists()

    def _download_repo(self):
        """
        Download a GitHub repository to the specified destination.

        Args:
            destination (str): The destination directory to download the repository.
        """
        logging.info(f"PREPARE: Downloading repository from {self.repo_url} to {self.repository_path}")
        subprocess.run(
            ["git", 
             "clone", 
             self.repo_url, 
             os.path.join(self.project_folder, "repository")
            ]
        )
        subprocess.run(
            ["git", 
             "-C", 
             os.path.join(self.project_folder, 
             "repository"), 
             "checkout", 
             self.commit_hash
            ]
        )

    def _build_image(self):
        """
        Build a Docker image from the specified Dockerfile.

        Args:
            dockerfile_path (str): The path to the Dockerfile.
            image_name (str): The name of the Docker image to build.
        """
        logging.info(f"RUN: Building Docker image {self.docker_image_name} from {self.dockerfile_path}")
        subprocess.check_output(["docker", "build", "-t", self.docker_image_name, self.dockerfile_path])

    def _check_image_exists(self):
        """
        Check whether a docker image exists
        """
        logging.info(f"VALIDATION: Checking if Docker image exists: {self.docker_image_name}")
        image_exists = subprocess.run(['docker', 'image', 'inspect', self.docker_image_name])
        if not image_exists:
            raise OdtpRunSetupException(f"docker image {self.docker_image_name} does not exist" )   

    def _create_volume(self, volume_name):
        """
        Create a Docker volume with the specified name.

        Args:
            volume_name (str): The name of the Docker volume to create.
        """
        logging.info(f"RUN: Creating Docker volume {volume_name}")
        subprocess.run(["docker", "volume", "create", volume_name])
        
    def run_component(self, parameters, ports, instance_name, step_id=None):
        """
        Run a Docker component with the specified parameters.

        Args:
            component (str): The name of the Docker component to run.
            volume (str): The name of the Docker volume to mount.
            parameters (dict): The environment variables to pass to the Docker component.
            name (str, optional): The name of the Docker container. Defaults to "odtp_component".

        Returns:
            str: The ID of the Docker run.
        """
        logging.info(f"RUN: Running Docker component {self.repo_url} in docker with name {self.docker_image_name}")
        
        if step_id:
            parameters["ODTP_STEP_ID"] = step_id
            parameters["ODTP_MONGO_SERVER"] = config.ODTP_MONGO_SERVER
            parameters["ODTP_S3_SERVER"] = config.ODTP_S3_SERVER
            parameters["ODTP_BUCKET_NAME"] = config.ODTP_BUCKET_NAME
            parameters["ODTP_ACCESS_KEY"] = config.ODTP_ACCESS_KEY
            parameters["ODTP_SECRET_KEY"] = config.ODTP_SECRET_KEY

        env_args = [f"-e \"{key}={value}\"" for key, value in parameters.items()]

        if ports:
            logging.info(ports)
            ports_args = [f"-p {port_pair}" for port_pair in ports]
        else:
            ports_args = [""]

        docker_run_command = ["docker", "run", "-it", "--name", instance_name, 
                              "--volume", f"{os.path.abspath(self.input_volume)}:/odtp/odtp-input",
                              "--volume", f"{os.path.abspath(self.output_volume)}:/odtp/odtp-output"] + env_args + ports_args + [self.docker_image_name]
        
        command_string = ' '.join(docker_run_command)
        logging.info("Command to be executed:")
        logging.info(command_string) 

        process = subprocess.Popen(command_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        output, error = process.communicate()

        if process.returncode != 0:
            logging.error(f"Failed to run Docker component {instance_name}: {error.decode()}")
            return None
        else:
            docker_run_id = output.decode().strip()
            return docker_run_id

    def stop_component(self, name="odtpruntest"):
        """
        Stop a running Docker component.

        Args:
            name (str, optional): The name of the Docker container. Defaults to "odtpruntest".

        Returns:
            str: A message indicating the Docker component has been stopped.
        """
        logging.info(f"Stopping Docker component {name}")
        docker_stop_command = ["docker", "stop", name]
        process = subprocess.Popen(docker_stop_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = process.communicate()

        if process.returncode != 0:
            logging.error(f"Failed to stop Docker component {name}: {error.decode()}")
            return None
        else:
            return f"Docker component {name} has been stopped."

    def delete_component(self, instance_name="odtpruntest"):
        """
        Delete a Docker component.

        Args:
            name (str, optional): The name of the Docker container. Defaults to "odtpruntest".

        Returns:
            str: A message indicating the Docker component has been deleted.
        """
        logging.info(f"Deleting Docker component {instance_name}")
        docker_rm_command = ["docker", "rm", instance_name]
        process = subprocess.Popen(docker_rm_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = process.communicate()

        if process.returncode != 0:
            logging.error(f"Failed to delete Docker component {instance_name}: {error.decode()}")
            return None
        else:
            return f"Docker component {instance_name} has been deleted."
        
    def delete_image(self):
        """
        Delete a Docker image.

        Returns:
            str: A message indicating the Docker image has been deleted.
        """
        logging.info(f"Deleting Docker image {self.docker_image_name}")
        docker_rmi_command = ["docker", "rmi", self.docker_image_name]
        process = subprocess.Popen(docker_rmi_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = process.communicate()

        if process.returncode != 0:
            logging.error(f"Failed to delete Docker image {self.docker_image_name}: {error.decode()}")
            return None
        else:
            return f"Docker image {self.docker_image_name} has been deleted."
