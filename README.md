# ODTP: Open Digital Twin Platform

ODTP offers a comprehensive suite of functionalities to enhance digital twins' management, operation, and analysis. In ODTP, a digital twin is an advanced virtual model, embodying a broad spectrum of scenarios and systems that mirror current conditions and forecast future scenarios, offering users a robust platform for strategic optimization and decision-making. With ODTP, the digital twin concept transcends traditional boundaries, providing a pivotal tool for various applications, ensuring adaptability, insight, and innovation across diverse domains.

## Features

- **Intuitive User Interface** to manage and operate your digital twins. 
- **Component Execution** to execute your or existing components for simulation, analysis or visualization.
- **Iteration Monitoring** to check digital twins iterations.
- **Log Analysis** to conveniently access and analyze container logs.
- **Workflow Design Tool** to design and run digital twins.
- **Schema Management & Testing** to restart and test different schemas for MongoDB / S3.
- **Result Analysis** to inspect outputs/snapshots and download results. 

## How to install and configure it?

You can install odtp by using [poetry](https://python-poetry.org/) and running: 

1. Download the repository. 
2. (Optional) Rename `.env.dist` as `.env` and populate it with the right credentials. This is essential if you want to use S3 and MongoDB. 
2. Run `poetry install`
3. Run `poetry shell`
4. Run `odtp --help`

This should print out the help for `odtp`

Hint: on a Mac with Apple Chip: change the default shell before you install
```bash
env /usr/bin/arch -x86_64 /bin/bash --login
```

### Configuring .env file. 

In order to connect to MongoDB and S3. You need to provide the credentials in an enviroment file with the following structure. This .env file needs to be in the folder where odtp is executed.

```
ODTP_MONGO_URL=
ODTP_S3_SERVER=
ODTP_BUCKET_NAME=
ODTP_ACCESS_KEY=
ODTP_SECRET_KEY=
```

## How to use it?

This will guide you through the most usual tasks when working with ODTP.

### How to run a single component?

In this example we are going to run ()[ODTP component example]. First, we will prepare the component which will automatically download the repostory, build the image and prepare all the folders needed for the input / output data. 

First let's create a project folder called `digital_twin_project`. In this folder is where all the folders will appear. 

```
mkdir digital_twin_project
```
 
 Then we can prepare the project by running the following. This will download the repo and build the image. 

 ```
 odtp component prepare --folder /Users/carlosvivarrios/pro/odtp/digital_twin_project --image_name image_test --repository https://github.com/odtp-org/odtp-component-example
 ```

 Now we need to run the component: 

 ```
 odtp component run --folder /Users/carlosvivarrios/pro/odtp/digital_twin_project --image_name image_test --repository https://github.com/odtp-org/odtp-component-example --env_file /Users/carlosvivarrios/pro/odtp/digital_twin_project/.env --instance_name instance_test
 ```

Then we can delete the instance by running. In docker terminology this will remove the container

```
odtp component delete-instance --instance_name instance_test
```

And finally if we want to delete the image we can run:

```
odtp component delete-image --image_name image_test 
```

### How to add a new user? 

```
odtp new user-entry --name Pedro --email vote@for.pedro --github pedro
```

You can check that the user is correctly stored using:

```
odtp db get --id 65843acbe473dfffb95371d7 --collection users
```

This should deliver:

```
INFO (21/12/2023 02:18:34 PM): Connected to: <odtp.db.MongoManager object at 0x137689610> (LineL 22 [initial_setup.py])
{'_id': ObjectId('65843acbe473dfffb95371d7'), 'displayName': 'Pedro', 'email': 'vote@for.pedro', 'github': 'pedro', 'created_at': datetime.datetime(2023, 12, 21, 13, 16, 59, 857000), 'updated_at': datetime.datetime(2023, 12, 21, 13, 16, 59, 857000)}
{
    "_id": {
        "$oid": "65843acbe473dfffb95371d7"
    },
    "displayName": "Pedro",
    "email": "vote@for.pedro",
    "github": "pedro",
    "created_at": {
        "$date": 1703164619857
    },
    "updated_at": {
        "$date": 1703164619857
    }
}
```

### How to index a new component?

```
odtp new odtp-component-entry --name component-example --version 0.0.1 --component-version 0.0.1 --repository https://github.com/odtp-org/odtp-component-example
```

Info:
```
odtp db get --id 65843bdf57da36bb8e8da182 --collection components
odtp db get --id 65843be057da36bb8e8da184 --collection versions
```

### How to create a new digital twin? 

```
odtp new digital-twin-entry --user-id 65843acbe473dfffb95371d7 --name example
```

Info:
```
odtp db get --id 65843c6cae2082459baeb575 --collection digitalTwins
```

### How to create a new execution of a digital twin?

```
odtp new execution-entry --digital-twin-id 65843acbe473dfffb95371d7 \
--name execution-example \
--components 65843bdf57da36bb8e8da182 \
--versions 65843be057da36bb8e8da184 \
--workflow 0
```

Info:
```
odtp db get --id 65843d8043feea167c5cbbe8 --collection executions
odtp db get --id 65843d8143feea167c5cbbea --collection steps
```

### How to prepare an execution with one ODTP Component?

Once the execution is configured and added to the database we can prepare it. This means that all the components will be downloaded and the docker images built. This step is necessary before running the execution.

```
odtp execution prepare --execution-id 65843d8043feea167c5cbbe8 --project-path [Path to your folder]
```
 A normal preparation should looks like:

 ```
INFO (21/12/2023 02:53:02 PM): Connected to: <odtp.db.MongoManager object at 0x138546950> (LineL 22 [initial_setup.py])
INFO (21/12/2023 02:53:03 PM): Connected to: <odtp.db.MongoManager object at 0x12eca4110> (LineL 22 [initial_setup.py])
INFO (21/12/2023 02:53:03 PM): Connected to: <odtp.db.MongoManager object at 0x138530bd0> (LineL 22 [initial_setup.py])
INFO (21/12/2023 02:53:04 PM): Removing all files and directories (LineL 23 [run.py])
INFO (21/12/2023 02:53:04 PM): Downloading repository from https://github.com/odtp-org/odtp-component-example to dt_test/component-example_0.0.1_0/repository (LineL 35 [run.py])
Cloning into 'dt_test/component-example_0.0.1_0/repository'...
remote: Enumerating objects: 65, done.
remote: Counting objects: 100% (65/65), done.
remote: Compressing objects: 100% (42/42), done.
remote: Total 65 (delta 30), reused 52 (delta 18), pack-reused 0
Receiving objects: 100% (65/65), 31.23 KiB | 376.00 KiB/s, done.
Resolving deltas: 100% (30/30), done.
INFO (21/12/2023 02:53:05 PM): Building Docker image component-example_0.0.1 from dt_test/component-example_0.0.1_0/repository (LineL 47 [run.py])

...

INFO (21/12/2023 03:24:36 PM): COMPONENTS DOWNLOADES AND BUILT (LineL 60 [workflow.py])
 ```

### How to run one execution with one ODTP Component?

We need to create one envfile containing the parameters per step.

```
odtp execution run --execution-id 65843d8043feea167c5cbbe8 --project-path [Path to your folder] --env-files [Path to the envfiles]
```

### How to run the GUI dashboard?

The dashboard functionality is limited right now and still require an update to the version v0.2.0. However it can be deployed by going to the repository folder and running: `odtp dashboard run --port 8501`


## Concept

The idea of odtp is to be installed as an instance in small-medium computing platform (such a servers, workstations, laptops, etc).  

The arquitecture of the odtp include different core-modules dealing with specific task. Between parenthesis you can find the technologies that are being considered for this modules.

- GUI (Streamlit)
- CLI
- Authentication (eduID, GH)
- Workflow manager (Barfi)
- ODTP orchestrator (ODTP original)
- License manager (Swiss Data Custodian) #core-optional
- Data governance (Swiss Data Custodian) #core-optional
- Semantic validator engine (TopBrains) #core-optional
- KG/Ontology storing (GraphDB) #core-optional
- Snapshots/Data transferring (MINION S3)
- Performance Logging (Grafana) 

All these core modules will be available in the full instance. However, for those users who wants to try a lighter version they can omit the core-optional modules having only the following configuration.

- Core Modules
    - GUI (Streamlit)
    - CLI
    - Authentication (eduID, GH)
    - Workflow manager (Barfi)
    - ODTP orchestrator (ODTP original)
    - Traces/Logging/Users data storing (MongoDB)
    - Snapshots/Data transferring (MINION S3)
    - Performance Logging (Grafana) 

- Core-Optional Modules
    - Semantic validator engine (TopBrains) #core-optional
    - KG/Ontology storing (GraphDB) #core-optional
    - License manager (Swiss Data Custodian) #core-optional
    - Data governance (Swiss Data Custodian) #core-optional

Finally the ODTP will be complemented with a components zoo that will include extensions of 3 types:

- X number of dataloaders.
- Y number of analytical components.
- Z number of visualization components.

## Changelog

- v.0.2.0: Improvements in database and files management.
    - New MongoDB Schema. (Here)
    - ODTP digital Zoo compatibility. 
    - Automatic generation/deletion of initial volumes for docker. 
    - S3 extended functionality.


- v.0.1.0: Basic UI
    - Streamlit APP with different
    - User tagging
    - Component listing placeholder
    - Digital Twins listing
    - Snapshots listing.
    - Workflow desginer.
    - pygwalker data visualization.
    - MongoDB is required to be deployed independtly.
    - S3 is required to be deployed indepently.

## Technologies involved

- Streamlit (UI)
- Barfi (Workflow manager)
- MongoDB (Document Database)
- S3 (Storage Sytem)
- Docker (Container Technology)
- pygwalker (Data Visualization)

## Terminology

- ODTP: A tool designed to manage, run, and design digital twins. It offers an interface (CLI, and GUI) for running and managing digital twins. It wraps different open source technologies to provide a high level API for the final user. 
- Components (ODTP Term): Extensions generated by us or the community that perform specific tasks in the digital twin. The input/output is validated semantically, and they run within a docker container as an independent micro-service. They can be one of the following categories:
	- Dataloader component. 
	- Analytical component.
	- Visualization component.
- Core/core-optional modules (ODTP Term): These modules are the different parts that we are developing for the ODTP. These core modules include the different classes/methods needed to run the tool and wrap the services used. Some of these modules are not mandatory in order to run ODTP with the minimal features (i.e. running manually odtp components).
- Services: One service or micro-service, in a micro-services architecture refers to one logical unit that performs one specific task in an independent manner. In ODTP we use different servers to support core modules, such as MongoDB for the database, Minion for the storage, or GraphDB for the knowledge graph storing. But also, from a technical standpoint every component is turned into a micro-service when running. I think this is the part that’s bringing more confusion. 

## Third party dependencies

### How to deploy a mongoDB

```
docker run --name mongodb-instance -it -v /home/[USER]/mongodb:/data/db -e MONGO_INITDB_ROOT_USERNAME=[USER] -e MONGO_INITDB_ROOT_PASSWORD=[PASS] -e MONGO_INITDB_DATABASE=odtp -p 27017:27017 mongo:latest
```

### MongoDB Schema

This is the schema for odtp database. 

v.0.2.0 Schema

```python
# Users Collection
users = {
    "_id": ObjectId(),
    "displayName": "John Doe",
    "email": "john@example.com",
    "github": "johnDoeRepo",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

# Components Collection
components = {
    "_id": ObjectId(),
    "author": "Test",
    "componentName": "ComponentX",
    "status": "active",
    "title": "Title for ComponentX",
    "description": "Description for ComponentX",
    "tags": ["tag1", "tag2"],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

# Versions Collection
versions = {
    "_id": ObjectId(),
    "componentId": ObjectId(),
    "version": "v1.0",
    "component_version": "1.0.0",
    "repoLink": "https://github.com/...",
    "dockerHubLink": "https://hub.docker.com/...",
    "parameters": {},
    "title": "Title for Version v1.0",
    "description": "Description for Version v1.0",
    "tags": ["tag1", "tag2"],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

# DigitalTwins Collection
digitalTwins = {
    "_id": ObjectId(),
    "userRef": ObjectId(),
    "name" : "title",
    "status": "active",
    "public": True,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "executions": [ObjectId()]  # Array of ObjectIds referencing Executions collection
}

# Executions
executions = {
    "_id": ObjectId(),
    "digitalTwinRef": ObjectId(),  # Reference to DigitalTwins collection
    "title": "Title for Execution",
    "description": "Description for Execution",
    "tags": ["tag1", "tag2"],
    "workflowSchema": {
        "workflowExecutor": "barfi",
        "workflowExecutorVersion": "v2.0",
        "components": [{"component": ObjectId(),
                        "version": ObjectId() }],  # Array of ObjectIds for components
        "WorkflowExecutorSchema": {}
    },
    "start_timestamp": datetime.utcnow(),
    "end_timestamp": datetime.utcnow(),
    "steps": [ObjectId()]  # Array of ObjectIds referencing Steps collection. Change in a future by DAG graph.
}

# Steps
steps = {
    "_id": ObjectId(),
    "executionRef": ObjectId(),  # Reference to Executions collection
    "timestamp": datetime.utcnow(),
    "start_timestamp": datetime.utcnow(),
    "end_timestamp": datetime.utcnow(),
    "type": "interactive" or "ephemeral",
    "logs": [{
        "timestamp": datetime.utcnow(),
        "type": "DEBUG",
        "logstring": "Test log"
    }],
    "inputs": {},
    "outputs": {},
    "component": ObjectId(),
    "component_version": ObjectId(),
    "parameters": {},
    "output": ObjectId()
}

output = {
    "_id": ObjectId(),
    "stepRef": ObjectId(),  # Reference to the Step this output is associated with
    "output_type": "snapshot" or "output",
    "s3_bucket": "bucket_name",  # Name of the S3 bucket where the output is stored
    "s3_key": "path/to/output",  # The key (path) in the S3 bucket to the output
    "file_name": "output_file_name",  # The name of the file in the output
    "file_size": 123456,  # Size of the file in bytes
    "file_type": "image/jpeg",  # MIME type or file type
    "created_at": datetime.utcnow(),  # Timestamp when the output was created
    "updated_at": datetime.utcnow(),  # Timestamp when the output was last updated
    "metadata": {  # Additional metadata associated with the output
        "description": "Description of the output",
        "tags": ["tag1", "tag2"],
        "other_info": "Other relevant information"
    },
    "access_control": {  # Information about who can access this output
        "public": False,  # Indicates if the output is public or private
        "authorized_users": [ObjectId()],  # Array of User ObjectIds who have access
    }
}


# Results Collection
results = {
    "_id": ObjectId(),
    "executionRef": ObjectId(),
    "digitalTwinRef": ObjectId(),  # Direct reference to the DigitalTwin
    "output": [ObjectId()],
    "title": "Title for Result",
    "description": "Description for Result",
    "tags": ["tag1", "tag2"],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}
```
# How to Contribute to the ODTP Project
We sincerely appreciate your interest in contributing to the ODTP project. Here is a step-by-step guide to help you through the process:
- **Step 1: Sign the Contributor License Agreement (CLA).** Before contributing, please sign a CLA, which clarifies the intellectual property licenses granted with contributions.
    - Individual Contributors (CLAI): If you're contributing independently (not on behalf of a company), sign the [Individual Contributor License Agreement (CLAI)](https://github.com/odtp-org/odtp/blob/main/CLAI.txt).
    - Corporate Contributors (CLAC): If contributions are made by employees on behalf of a company, the company should sign the [Corporate Contributor License Agreement (CLAC)](https://github.com/odtp-org/odtp/blob/main/CLAC.txt).

- **Step 2: Decide How to Contribute.** For minor improvements or fixes, consider opening a new issue or commenting on an existing relevant issue. For significant contributions or discussions before contributing, contact our coordinators at contact@datascience.ch.
- **Step 3: Follow Our Code of Conduct and Contribution Guidelines**.
Contributors are expected to adhere to our Code of Conduct, which promotes a respectful and collaborative environment:
  - Inclusivity & Empathy: Everyone is welcome. We value empathy, kindness, and patience.
  - Collaborative Spirit: Resolve conflicts together, assume good intentions, and respect each other’s work.
  - Openness: Encourage public communication for project-related discussions, reserving private channels for sensitive matters.
  - Responsibility & Respect: Be thoughtful in communication. Harassment, insults, or exclusionary behavior are not tolerated.
  - Diversity & Participation: We welcome diverse backgrounds and strive to make everyone feel valued.
  - Language: English is used for project development. Help maintain this standard.


# Acknowledgments, Copyright, and Licensing
## Acknowledgments and Funding
This work is part of the broader project **O**pen **D**igital **T**win **P**latform of the **S**wiss **M**obility **S**ystem (ODTP-SMS) funded by Swissuniversities CHORD grant Track B - Establish Projects. ODTP-SMS project is a joint endeavour by the Center for Sustainable Future Mobility - CSFM (ETH Zürich) and the Swiss Data Science Center - SDSC (EPFL and ETH Zürich). 
The Swiss Data Science Center (SDSC) develops domain-agnostic standards and containerized components to manage digital twins. This includes the creation of the Core Platform (both back-end and front-end), Service Component Integration Templates, Component Ontology, and the Component Zoo template. 
The Center for Sustainable Future Mobility (CSFM) develops mobility services and utilizes the components produced by SDSC to deploy a mobility digital twin platform. CSFM focuses on integrating mobility services and collecting available components in the mobility zoo, thereby applying the digital twin concept in the realm of mobility.
 
## Copyright
Copyright © 2023-2024 Swiss Data Science Center (SDSC), www.datascience.ch. All rights reserved.
The SDSC is jointly established and legally represented by the École Polytechnique Fédérale de Lausanne (EPFL) and the Eidgenössische Technische Hochschule Zürich (ETH Zürich). This copyright encompasses all materials, software, documentation, and other content created and developed by the SDSC.

## Intellectual Property (IP) Rights
The Open Digital Twin Platform (ODTP) is the result of a collaborative effort between ETH Zurich (ETHZ) and the École Polytechnique Fédérale de Lausanne (EPFL). Both institutions hold equal intellectual property rights for the ODTP project, reflecting the equitable and shared contributions of EPFL and ETH Zürich in the development and advancement of this initiative.  
 
## Licensing
The core component of the ODTP software is distributed as open-source under the AGPLv3 license. This ensures that all modifications and derivatives remain open source, fostering a collaborative and shared development environment. Detailed terms of the AGPLv3 license can be found in the LICENSE file within this distribution package.

### Distinct Licensing for Other Components
Service Component Integration Templates are licensed under the BSD-3 license, allowing for broad compatibility and standardization.
Ontology: The foundational ODTP ontology is licensed under the Creative Commons Attribution-ShareAlike (CC BY-SA), promoting open use and ensuring that any derivatives also remain open.
Component Zoo Template: The template for the Component Zoo operates under the BSD-3 license, emphasizing broad compatibility and open development. It's important to note that individual components within the Zoo retain their original licenses.

### Alternative Commercial Licensing
Alternative commercial licensing options for the core platform and other components are available and can be negotiated through the EPFL Technology Transfer Office (https://tto.epfl.ch) or ETH Zürich Technology Transfer Office (https://ethz.ch/en/industry/transfer.html).

## Ethical Use and Legal Compliance Disclaimer
Please note that this software should not be used to deliberately harm any individual or entity. Users and developers must adhere to ethical guidelines and use the software responsibly and legally. This disclaimer serves to remind all parties involved in the use or development of this software to engage in practices that are ethical, lawful, and in accordance with the intended purpose of the software.
