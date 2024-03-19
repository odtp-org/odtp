"""
This scripts contains odtp subcommands for 'components'
"""
import typer
import time
import redis
from typing_extensions import Annotated

from odtp.run import DockerManager
import odtp.helpers.git as odtp_git
import odtp.helpers.parse as odtp_parse
import odtp.helpers.utils as odtp_utils
import odtp.helpers.middleware as odtp_middleware

current_user = None
token_data = {'token': None, 'expiration_time': 0}

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)







app = typer.Typer()

## Adding listing so we can have multiple flags
from typing import List

@app.command()
def prepare(
    folder: str = typer.Option(
        ..., "--folder", help="Specify the project folder location"
    ),
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the component image"
    ),
    repository: str = typer.Option(
        ..., "--repository", help="Specify the git repository url"
    ),
):  
    global current_user, token_data
    token_data = odtp_middleware.update_token_data(current_user)
    print(f"token_data {token_data}!")
    
    if token_data['token'] is None or token_data['expiration_time'] < time.time():
        print("The dictionary is empty")
        current_user = odtp_middleware.login()
        
        
        print(f"Welcome {current_user['preferred_username']}!")
      
        token_data = odtp_middleware.update_token_data(current_user)
        print(f"token_data {token_data}!")
    try:
        print(f"Welcome {token_data}!")
        componentManager = DockerManager(
            repo_url=repository, 
            image_name=image_name, 
            project_folder=folder
            )
        componentManager.prepare_component()
    except Exception as e:
        print(f"ERROR: Prepare component failed: {e}") 
        raise typer.Abort()           
    else:
        print("SUCCESS: image for the component has been build")

@app.command()
def run(
    folder: str = typer.Option(
        ..., "--folder", help="Specify the project folder location"
    ),
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the component image"
    ),
    instance_name: str = typer.Option(
        ..., "--instance_name", help="Specify the name of the instance"
    ),    
    repository: str = typer.Option(
        ..., "--repository", help="Specify the git repository url"
    ),
    commit: Annotated[str, typer.Option(
        help="You may specify the commit of the repository. If not provided the latest commit will be fetched"
    )] = None,
    parameter_file: Annotated[str, typer.Option(
        help="Specify the path to the environment file"
    )] = None,     
    ports: Annotated[str, typer.Option(
        help="Specify port mappings seperated by a plus sign i.e. 8501:8501+8201:8201"
    )] = None,  
):  
    global current_user
    token_data = odtp_middleware.update_token_data(current_user)
    print(f"token_data {token_data}!")
    expiration_time_struct = time.localtime(token_data['expiration_time'])
    expiration_time = token_data['expiration_time']
    # Convert the expiration_time to a struct_time object
    expiration_time_struct = time.localtime(expiration_time)
    # Convert the expiration_time_struct to a Unix timestamp
    expiration_timestamp = time.mktime(expiration_time_struct)
    print(f"expiration_time_struct {expiration_timestamp}")
    print(f"expiration_time_struct {time.time()}")
    
    # Convert the struct_time objects to human-readable dates
    expiration_time1 = time.strftime("%Y-%m-%d %H:%M:%S", expiration_time_struct)
    expiration_time2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    print("Expiration Time 1:", expiration_time1)
    print("current time:",  expiration_time2)
    if token_data['token'] is None or  expiration_time1  < expiration_time2:
        print("The dictionary is empty")
        current_user = odtp_middleware.login()
        
        
        print(f"Welcome {current_user['preferred_username']}!")
       
        token_data = odtp_middleware.update_token_data(current_user)
        print(f"token_data {token_data}!")
        try:
            componentManager = DockerManager(
                project_folder=folder,
                repo_url=repository,
                commit_hash=commit, 
                image_name=image_name, 
                )
            ports = odtp_parse.parse_port_mappings_for_one_component(ports) 
            parameters = odtp_parse.parse_paramters_for_one_file(parameter_file)
            componentManager.run_component(
                parameters=parameters, 
                ports=ports, 
                instance_name=instance_name
                )
        except Exception as e:
            print(f"ERROR: Run of component failed: {e}") 
            raise typer.Abort()           
    else:
        print("SUCCESS: container for the component has been started")


#### TODO: Stop Component
@app.command()
def stop():
    pass


@app.command()
def delete_instance(
    instance_name: str = typer.Option(
        ..., "--instance_name", help="Specify the name of the docker image"
    )
):
    componentManager = DockerManager()
    componentManager.delete_component(instance_name=instance_name)
    print("Container deleted")


@app.command()
def delete_image(
    image_name: str = typer.Option(
        ..., "--image_name", help="Specify the name of the docker image"
    )
):
    componentManager = DockerManager(image_name=image_name)
    componentManager.delete_image()
    print("Image deleted")


if __name__ == "__main__":
    app()
