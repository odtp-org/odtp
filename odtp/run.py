# Send to the docker as env
# Step id for logging
# Output id for uploading the data

# The component will upload automatically all to s3

# Method to take the component
# Get the URL
# Build the image
# Run the component with a list of parameters
# 




def runDockerComponent(component, volume, env, name="odtpruntest"):

    # Create env file 
    write_string_to_file(".env", env)

    # Run 
    if component == "Eqasim":
        dockerimage = "caviri/odtp-eqasim:pipeline_parameter"
    elif component == "Matsim":
        dockerimage = "TODO"
    else:
        return "Component not found"

    # We can use detach from docker too
    cmd = ["nohup","docker", "run", "--rm", "-v", f"{volume}:/odtp/odtp-volume", "--env-file", ".env", "--name", name, dockerimage, ">" ,"output.log", "2>&1", "&"] 
    print(cmd)

    process = subprocess.Popen(cmd)
    print(process)

    return f"Running {cmd}"

def stopDockerComponent(name="odtpruntest"):
    cmd = ["docker", "stop", name]

    process = subprocess.Popen(cmd)

    return "Docker stopped"