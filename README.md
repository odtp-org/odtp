# odtp

This tools allows you to: 

- Serve an user interface to manage and run your digital twins. 
- Execute ODTP components.
- Check digital twins iterations.
- Check running container logs.
- Design and run digital twins using a node base workflow tool.
- Restart and test different schemas for MongoDB / S3.
- Check outputs/snapshots and download results. 

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

v.0.1.0 Schema

```python
# Users Collection
users = {
    "_id": ObjectId(),   # MongoDB will automatically create an _id
    "displayName": "John Doe",
    "email": "john@example.com",
    "github": "johnDoeRepo"
}

# Components Collection
components = {
    "_id": ObjectId(),
    "author": ObjectId(),  # Reference to Users collection
    "componentName": "ComponentX"
}

# Versions Collection
versions = {
    "_id": ObjectId(),
    "componentId": ObjectId(),  # Reference to Components collection
    "version": "v1.0",
    "repoLink": "https://github.com/...",
    "dockerHubLink": "https://hub.docker.com/...",
    "parameters": {...}   # Parameters JSON object
}

# DigitalTwins Collection
digitalTwins = {
    "_id": ObjectId(),
    "userRef": ObjectId(),  # Reference to Users collection
    "workflowSchema": {
        "version": "v2.0",
        "components": [ObjectId()],  # Array of ObjectIds referring to Components
        "barfiSchema": {...},  # Barfi Schema JSON object
        "public": True
    },
    "executions": [{
        "timestamp": "2023-10-03T10:15:30Z",
        "steps": [{
            "timestamp": "2023-10-03T10:16:00Z",
            "logs": "...",
            "inputs": {...},
            "outputs": {...},
            "component": ObjectId(),  # Reference to Components collection
            "component_version": "v1.0",
            "parameters": {...}, 
            "snapshot": "..."
        }]
    }]
}

# Results Collection
results = {
    "_id": ObjectId(),
    "executionRef": ObjectId(),  # Reference to DigitalTwins.execution
    "outputs": {...}
}
```


## Development.

Developed by SDSC/CSFM