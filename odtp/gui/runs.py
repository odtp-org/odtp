import streamlit as st
import subprocess

def write_list_to_file(filename, string_list):
    with open(filename, 'w') as file:
        file.write('\n'.join(string_list))


def runDockerComponent(component, volume, env, name="odtpruntest"):

    # Create env file 
    write_list_to_file(".env", env)

    # Run 
    if component == "eqasim":
        dockerimage = "caviri/odtp-eqasim:environmentparameters_test"
    elif component == "matsim":
        dockerimage = "TODO"
    else:
        return "Component not found"

    cmd = ["docker", "run", "-it", "--rm", "-v", f"{volume}:/odtp/odtp-volume", "--env-file", ".env", "--name", name, dockerimage] 

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)

    return f"Running {cmd}"

def stopDockerComponent(name="odtpruntest"):
    cmd = ["docker", "stop", "my_container"]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)

    return "Docker stoped"

st.markdown("# Run components")
st.markdown("In order to run the component please be sure the component is built on the machine")

# Dropdown for component selection
component = st.selectbox(
    'Which component would you like to run?',
    ('Eqasim', 'Matsim'))

# Volume textinput
st.write("Please insert the volume used in the server")
volume = st.text_input('Please insert the docker volume folder', '/home/vivar/eqasim-tutorial/volume-idf')

# Create temporally folder from uploaded zip?

# Textbox for environment variables
st.write("Please define here the file containing the environment variables file.")
st.write("For instance in Eqasim, check the github documentation in README.md")

envValue = """SCENARIO=IDF
MONGODB_CLIENT=mongodb://.....
S3_ACCESS_KEY=Q0ISQ....
S3_SERVER=https://..
S3_SECRET_KEY=OoPthI....
S3_BUCKET_NAME=13301....
processes=8
sampling_rate=0.001
random_seed=1234
java_memory=24G
hts=entd
"""

env = st.text_area("Environment file", value=envValue, height=600)


if st.button('Run'):
    out = runDockerComponent(component, volume, env)
    st.write(out)

if st.button("Stop"):
    out = stopDockerComponent(name="odtpruntest")
    st.write(out)