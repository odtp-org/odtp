import logging
import os
import json
import subprocess
import docker
import odtp.helpers.settings as config
import odtp.helpers.git as git_helpers
import odtp.helpers.environment as env_helpers
import odtp.mongodb.utils as db_utils
import odtp.mongodb.db as db


REPO_DIR = "repository"
INPUT_DIR = "odtp-input"
OUTPUT_DIR = "odtp-output"
LOG_DIR = "odtp-logs"


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(config.get_command_log_handler())


class OdtpRunSetupException(Exception):
    pass


class DockerManager:
    def __init__(self, repo_url="", commit_hash="", image_name="", project_folder="", image_link=None):
        log.debug(f"""Docker manager initialized with repo_url: {repo_url},
                     commit_hash: {commit_hash}, 
                     project_folder: {project_folder}, 
                     image_name: {image_name}""")
        self.repo_url = repo_url
        self.commit_hash = commit_hash
        self.project_folder = project_folder
        self.repository_path = os.path.join(self.project_folder, REPO_DIR)
        self.dockerfile_path = os.path.join(self.project_folder, REPO_DIR)
        self.docker_image_link = image_link
        self.docker_image_name = image_name
        self.input_volume = os.path.join(self.project_folder, INPUT_DIR)
        self.log_volume = os.path.join(self.project_folder, LOG_DIR)
        self.output_volume = os.path.join(self.project_folder, OUTPUT_DIR)

    def prepare_component(self):
        self._checks_for_prepare()
        self._create_project_folder_structure()
        if not self._check_if_image_exists():
            if not self.docker_image_link:
                self._download_repo()
                self._build_image()
            else:
                self._pull_image()  

    def _create_project_folder_structure(self):
        """Create all the folder structure in project_folder""" 
        log.debug("PREPARE create project folder structure")
        os.makedirs(self.repository_path, exist_ok=True)
        os.makedirs(self.input_volume, exist_ok=True)
        os.makedirs(self.output_volume, exist_ok=True)    
        os.makedirs(self.log_volume, exist_ok=True)

    def _check_project_folder_prepared(self):  
        log.debug(f"VALIDATION: check project folder structure: {self.project_folder}")  
        """check whether the project folder is prepared with the expected 
        structure of repository_path, input and output volume"""
        subdirs = []
        with os.scandir(self.project_folder) as entries:
            for entry in entries:
                if entry.is_dir():
                    subdirs.append(entry.name)
        if set(subdirs) != set(REPO_DIR, INPUT_DIR, OUTPUT_DIR, LOG_DIR):
            raise OdtpRunSetupException(
                f"""project folder {self.project_folder} does not have 
                expected directory structure with {REPO_DIR}, {INPUT_DIR}, {OUTPUT_DIR}"""
            )
        
    def _checks_for_prepare(self):
        log.debug(f"VALIDATION: check commit hash {self.commit_hash} for prepare") 
        env_helpers.check_project_folder_empty(self.project_folder)
        self.commit_hash = git_helpers.check_commit_for_repo(
            repo_url=self.repo_url, 
            commit_hash=self.commit_hash
        )

    def _checks_for_run(self, parameters, ports, image_name):
        log.info("VALIDATION: check for run")
        self._check_project_folder_prepared()
        self._check_image_exists()
        try:
            json.dumps(parameters)
        except Exception as e:
            raise OdtpRunSetupException(f"parameters are not transformable to json: {parameters}")
        
        db_utils.check_port_mappings_for_component_runs(ports)
        self._check_image_exists()

    def _check_if_image_exists(self):
        """
        Check whether a docker image exists
        """
        logging.info(f"VALIDATION: Checking if Docker image exists: {self.docker_image_name}")
        client = docker.from_env()
        images = client.images.list(name=self.docker_image_name)
        logging.info(f"Images found: {images}") 

        if len(images) > 0:
            return True
        else:
            return False   

    def _download_repo(self):
        """
        Download a GitHub repository to the specified destination.

        Args:
            destination (str): The destination directory to download the repository.
        """
        log.debug(f"PREPARE: Downloading repository from {self.repo_url} to {self.repository_path}")
        git_clone_command = [
            "git",
             "clone",
             self.repo_url, 
             self.repository_path,
        ]
        log.info(" ".join(git_clone_command))
        subprocess.run(git_clone_command)
        git_checkout_command = [
            "git",
             "-C", 
             self.repository_path,
             "checkout", 
             self.commit_hash,
        ]
        log.info(" ".join(git_checkout_command))
        subprocess.run(git_checkout_command)
        git_submodule_command = [
            "git",
             "-C",
             self.repository_path,
             "submodule",
             "update",
            "--init",
        ]
        log.info(" ".join(git_submodule_command))
        subprocess.run(git_submodule_command)

    def _build_image(self):
        """
        Build a Docker image from the specified Dockerfile.

        Args:
            dockerfile_path (str): The path to the Dockerfile.
            image_name (str): The name of the Docker image to build.
        """
        log.info(f"RUN: Building Docker image {self.docker_image_name} from {self.dockerfile_path}")
        subprocess.check_output(["docker", "build", "-t", self.docker_image_name, self.dockerfile_path])

    def _pull_image(self):
        """
        Pull a Docker image from a Docker registry.
    
        Args:
            image_name (str): The name of the Docker image to pull.
        """
        log.info(f"RUN: Pulling Docker image {self.docker_image_name}")
        subprocess.check_output(["docker", "pull", self.docker_image_link])
        subprocess.check_output(["docker", "tag", self.docker_image_link, self.docker_image_name])
        subprocess.check_output(["docker", "rmi", self.docker_image_link])

    def _check_image_exists(self):
        """
        Check whether a docker image exists
        """
        log.info(f"VALIDATION: Checking if Docker image exists: {self.docker_image_name}")
        image_exists = subprocess.run(['docker', 'image', 'inspect', self.docker_image_name])
        if not image_exists:
            raise OdtpRunSetupException(f"docker image {self.docker_image_name} does not exist" )   

    def _create_volume(self, volume_name):
        """
        Create a Docker volume with the specified name.

        Args:
            volume_name (str): The name of the Docker volume to create.
        """
        log.info(f"RUN: Creating Docker volume {volume_name}")
        subprocess.run(["docker", "volume", "create", volume_name])
        
    def run_component(self, parameters, secrets, ports, container_name, step_id=None):
        """
        Run a Docker component with the specified parameters.

        Args:
            secrets (dict): The secrets variables to pass to the Docker component.
            parameters (dict): The environment variables to pass to the Docker component.
            container_name (str, optional): The name of the Docker container. Defaults to "odtp_component".

        Returns:
            str: The ID of the Docker run.
        """
        log.info(f"RUN: Running ODTP component. Repo: {self.repo_url}, Image name: {self.docker_image_name}, Container Name: {container_name}")
        
        if step_id:
            parameters["ODTP_STEP_ID"] = step_id
        parameters["ODTP_MONGO_SERVER"] = config.ODTP_MONGO_SERVER
        parameters["ODTP_S3_SERVER"] = config.ODTP_S3_SERVER
        parameters["ODTP_BUCKET_NAME"] = config.ODTP_BUCKET_NAME
        parameters["ODTP_ACCESS_KEY"] = config.ODTP_ACCESS_KEY
        parameters["ODTP_SECRET_KEY"] = config.ODTP_SECRET_KEY

        env_args = [f"-e \"{key}={value}\"" for key, value in parameters.items() if key]

        if ports:
            ports_args = [f"-p {port_pair}" for port_pair in ports]
        else:
            ports_args = [""]

        if secrets:
            secrets_args = [f"-e \"{key}={value}\"" for key, value in secrets.items()]
        else:
            secrets_args = [""]

        docker_run_command = ["docker", "run", "--rm", "-it", "--name", container_name,
                              "--network", "odtp_odtp-network",
                              "--gpus", "all",
                              "--volume", f"{os.path.abspath(self.input_volume)}:/odtp/odtp-input",
                              "--volume", f"{os.path.abspath(self.log_volume)}:/odtp/odtp-logs",
                              "--volume", f"{os.path.abspath(self.output_volume)}:/odtp/odtp-output"] + env_args + ports_args + secrets_args + [self.docker_image_name]

        command_string = ' '.join(docker_run_command)
        command_string_log_safe = command_string
        for value in [parameters["ODTP_SECRET_KEY"], parameters["ODTP_ACCESS_KEY"], parameters["ODTP_MONGO_SERVER"]]:
            command_string_log_safe = command_string_log_safe.replace(value, "x")
        if secrets:
            for value in secrets.values():
                command_string_log_safe = command_string_log_safe.replace(value, "x")

        log.info(command_string_log_safe)
        process = subprocess.Popen(command_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        output, error = process.communicate()
        
        if process.returncode != 0:
            log.exception(f"Failed to run Docker component {container_name}: {error.decode()}")
            return None
        else:
            docker_run_id = output.decode().strip()
            log.info(f"Docker run was started with success: {container_name}")
            return docker_run_id

    def stop_component(self, name="odtpruntest"):
        """
        Stop a running Docker component.

        Args:
            name (str, optional): The name of the Docker container. Defaults to "odtpruntest".

        Returns:
            str: A message indicating the Docker component has been stopped.
        """
        log.info(f"Stopping Docker component {name}")
        docker_stop_command = ["docker", "stop", name]
        process = subprocess.Popen(docker_stop_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = process.communicate()

        if process.returncode != 0:
            log.exception(f"Failed to stop Docker component {name}: {error.decode()}")
            return None
        else:
            return f"Docker component {name} has been stopped."

    def delete_component(self, container_name="odtpruntest"):
        """
        Delete a Docker component.

        Args:
            name (str, optional): The name of the Docker container. Defaults to "odtpruntest".

        Returns:
            str: A message indicating the Docker component has been deleted.
        """
        log.info(f"Deleting Docker component {container_name}")
        docker_rm_command = ["docker", "rm", container_name]
        process = subprocess.Popen(docker_rm_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = process.communicate()

        if process.returncode != 0:
            log.exception(f"Failed to delete Docker component {container_name}: {error.decode()}")
            return None
        else:
            return f"Docker component {container_name} has been deleted."
        
    def delete_image(self):
        """
        Delete a Docker image.

        Returns:
            str: A message indicating the Docker image has been deleted.
        """
        log.info(f"Deleting Docker image {self.docker_image_name}")
        docker_rmi_command = ["docker", "rmi", self.docker_image_name]
        process = subprocess.Popen(docker_rmi_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = process.communicate()

        if process.returncode != 0:
            log.exception(f"Failed to delete Docker image {self.docker_image_name}: {error.decode()}")
            return None
        else:
            return f"Docker image {self.docker_image_name} has been deleted."
