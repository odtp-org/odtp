import logging
import os
import subprocess
# Send to the docker as env
# Step id for logging
# Output id for uploading the data

# The component will upload automatically all to s3

# Method to take the component
# Get the URL
# Build the image
# Run the component with a list of parameters
# 



class DockerManager:
    def __init__(self, repo_url):
        self.repo_url = repo_url

    def download_repo(self, destination):
        """
        Download a GitHub repository to the specified destination.

        Args:
            destination (str): The destination directory to download the repository.
        """
        logging.info(f"Downloading repository from {self.repo_url} to {destination}")
        subprocess.run(["git", "clone", self.repo_url, destination])


    def build_image(self, dockerfile_path, image_name):
        """
        Build a Docker image from the specified Dockerfile.

        Args:
            dockerfile_path (str): The path to the Dockerfile.
            image_name (str): The name of the Docker image to build.
        """
        logging.info(f"Building Docker image {image_name} from {dockerfile_path}")
        subprocess.run(["docker", "build", "-t", image_name, dockerfile_path])


    def create_volume(self, volume_name):
        """
        Create a Docker volume with the specified name.

        Args:
            volume_name (str): The name of the Docker volume to create.
        """
        logging.info(f"Creating Docker volume {volume_name}")
        subprocess.run(["docker", "volume", "create", volume_name])
        

    def run_component(self, component, volume, env, name="odtp_component"):
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
        logging.info(f"Running Docker component {component} with volume {volume} and name {name}")
        env_args = [f"-e {key}={value}" for key, value in env.items()]
        docker_run_command = ["docker", "run", "--detach", "--name", name, "--volume", f"{volume}:/mount"] + env_args + [component]
        process = subprocess.Popen(docker_run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode != 0:
            logging.error(f"Failed to run Docker component {component}: {error.decode()}")
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

    def delete_component(self, name="odtpruntest"):
        """
        Delete a Docker component.

        Args:
            name (str, optional): The name of the Docker container. Defaults to "odtpruntest".

        Returns:
            str: A message indicating the Docker component has been deleted.
        """
        logging.info(f"Deleting Docker component {name}")
        docker_rm_command = ["docker", "rm", name]
        process = subprocess.Popen(docker_rm_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode != 0:
            logging.error(f"Failed to delete Docker component {name}: {error.decode()}")
            return None
        else:
            return f"Docker component {name} has been deleted."


# def runDockerComponent(component, volume, env, name="odtpruntest"):

#     # Create env file 
#     write_string_to_file(".env", env)

#     # Run 
#     if component == "Eqasim":
#         dockerimage = "caviri/odtp-eqasim:pipeline_parameter"
#     elif component == "Matsim":
#         dockerimage = "TODO"
#     else:
#         return "Component not found"

#     # We can use detach from docker too
#     cmd = ["nohup","docker", "run", "--rm", "-v", f"{volume}:/odtp/odtp-volume", "--env-file", ".env", "--name", name, dockerimage, ">" ,"output.log", "2>&1", "&"] 
#     print(cmd)

#     process = subprocess.Popen(cmd)
#     print(process)

#     return f"Running {cmd}"

# def stopDockerComponent(name="odtpruntest"):
#     cmd = ["docker", "stop", name]

#     process = subprocess.Popen(cmd)

#     return "Docker stopped"