import logging
import os
import subprocess
import shutil
from dotenv import dotenv_values

"odtp"

class DockerManager:
    def __init__(self, repo_url="", image_name="", project_folder=""):
        self.repo_url = repo_url
        self.project_folder = project_folder
        self.repository_path = os.path.join(self.project_folder, "repository")
        self.dockerfile_path = os.path.join(self.project_folder, "repository")
        self.docker_image_name = image_name
        self.input_volume = os.path.join(self.project_folder, "odtp-input")
        self.output_volume = os.path.join(self.project_folder, "odtp-output")


        # Create all the folder structure in project_folder 
        os.makedirs(self.repository_path, exist_ok=True)
        os.makedirs(self.input_volume, exist_ok=True)
        os.makedirs(self.output_volume, exist_ok=True)
        
        # logging.info("Removing all files and directories")
        # shutil.rmtree(self.repository_path)
        # shutil.rmtree(self.input_volume)
        # shutil.rmtree(self.output_volume)

    def download_repo(self):
        """
        Download a GitHub repository to the specified destination.

        Args:
            destination (str): The destination directory to download the repository.
        """
        logging.info(f"Downloading repository from {self.repo_url} to {self.repository_path}")
        subprocess.run(["git", "clone", self.repo_url, os.path.join(self.project_folder, "repository")])


    def build_image(self):
        """
        Build a Docker image from the specified Dockerfile.

        Args:
            dockerfile_path (str): The path to the Dockerfile.
            image_name (str): The name of the Docker image to build.
        """
        logging.info(f"Building Docker image {self.docker_image_name} from {self.dockerfile_path}")
        subprocess.run(["docker", "build", "-t", self.docker_image_name, self.dockerfile_path])


    def create_volume(self, volume_name):
        """
        Create a Docker volume with the specified name.

        Args:
            volume_name (str): The name of the Docker volume to create.
        """
        logging.info(f"Creating Docker volume {volume_name}")
        subprocess.run(["docker", "volume", "create", volume_name])
        

    def run_component(self, env, instance_name, step_id=None):
        """
        Run a Docker component with the specified parameters.

        Args:
            component (str): The name of the Docker component to run.
            volume (str): The name of the Docker volume to mount.
            env (dict): The environment variables to pass to the Docker component.
            name (str, optional): The name of the Docker container. Defaults to "odtp_component".

        Returns:
            str: The ID of the Docker run.
        """
        logging.info(f"Running Docker component {self.repo_url} in docker with name {self.docker_image_name}")
        

        env_values = dotenv_values(env)
        
        # REMPLACE env by the ones for step, execution, ...
        if step_id:
            env_values["ODTP_STEP_ID"] = step_id

        env_args = [f"-e \"{key}={value}\"" for key, value in env_values.items()]
        #logging.info(env_args)

        #docker_run_command = ["docker", "run", "--detach", "--name", name, "--volume", f"{volume}:/mount"] + env_args + [component]
        docker_run_command = ["docker", "run", "-it", "--name", instance_name, 
                              "--volume", f"{os.path.abspath(self.input_volume)}:/odtp/odtp-input",
                              "--volume", f"{os.path.abspath(self.output_volume)}:/odtp/odtp-output"] + env_args + [self.docker_image_name]
        
        command_string = ' '.join(docker_run_command)
        #logging.info("Command to be executed:")
        #logging.info(command_string) 

        process = subprocess.Popen(command_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # # Print standard output in real-time
        # while True:
        #     output = process.stdout.readline()
        #     if output == b'' and process.poll() is not None:
        #         break
        #     if output:
        #         logging.info(output.replace('\r', '\n').strip())

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
        output, error = process.communicate()

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
        output, error = process.communicate()

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
            output, error = process.communicate()

            if process.returncode != 0:
                logging.error(f"Failed to delete Docker image {self.docker_image_name}: {error.decode()}")
                return None
            else:
                return f"Docker image {self.docker_image_name} has been deleted."
