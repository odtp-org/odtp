# odtp

This tools allows you to: 

- Serve an user interface to manage and run your digital twins. 
- Execute ODTP components.
- Check digital twins iterations.
- Check running container logs.
- Design and run digital twins using a node base workflow tool.
- Restart and test different schemas for MongoDB / S3.
- Check outputs/snapshots and download results. 

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
    - New MongoDB Schema. It will be apply after restarting the server. 


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
- Barfi (Worflow manager)
- MongoDB (Document Database)
- S3 (Storage Sytem)
- Docker (Container Technology)
- pygwalker (Data Visualization)

## How to install ODTP
### How to install ODTP in Conda

```
conda create --name odtp-main python=3.10
conda activate odpt-main
pip install streamlit streamlit-aggrid 
pip install st_pages barfi boto3 pymongo
pip install pygwalker streamlit-card
```

For running the GUI
```
cd odtp/gui
streamlit run app.py --server.port 8502
```

### How to run the odtp in docker
```
docker build -t caviri/odtp .
```

```
docker run -it --rm -p 8501:8501 caviri/odtp
```

## Documentation 

### How to deploy a mongoDB

```
docker run --name mongodb-instance -it -v /home/[USER]/mongodb:/data/db -e MONGO_INITDB_ROOT_USERNAME=[USER] -e MONGO_INITDB_ROOT_PASSWORD=[PASS] -e MONGO_INITDB_DATABASE=odtp -p 27017:27017 mongo:latest
```

### How to request an EPFL S3 Instance

TOBEDONE

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
    "author": ObjectId(),  # Reference to Users collection
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
    "status": "active",
    "public": True,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "executions": [{
        "executionId": ObjectId(),
        "title": "Title for Execution",
        "description": "Description for Execution",
        "tags": ["tag1", "tag2"],
        "workflowSchema": {
            "workflowExecutor": "barfi",
            "worflowExecutorVersion": "v2.0",
            "components": [ObjectId()],
            "WorkflowExecutorSchema": {}
        },
        "start_timestamp": datetime.utcnow(),
        "end_timestamp": datetime.utcnow(),
        "steps": [{
            "stepId": ObjectId(),
            "timestamp": datetime.utcnow(),
            "start_timestamp": datetime.utcnow(),
            "end_timestamp": datetime.utcnow(),
            "logs": "...",
            "inputs": {},
            "outputs": {},
            "component": ObjectId(),
            "component_version": "v1.0",
            "parameters": {}, 
            "snapshot": "..."
        }]
    }]
}

# Results Collection
results = {
    "_id": ObjectId(),
    "executionRef": ObjectId(),
    "digitalTwinRef": ObjectId(),  # Direct reference to the DigitalTwin
    "outputs": {},
    "title": "Title for Result",
    "description": "Description for Result",
    "tags": ["tag1", "tag2"],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}
```


## Development.

Developed by SDSC/CSFM