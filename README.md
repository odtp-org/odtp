# odtp

This tools allows you to: 

- Serve an user interface to manage and run your digital twins. 
- Execute ODTP components.
- Check digital twins iterations.
- Check running container logs.
- Design and run digital twins using a node base workflow tool.
- Restart and test different schemas for MongoDB / S3.
- Check outputs/snapshots and download results. 

## Roadmap


- v.0.1.0: Basic UI
    - Streamlit APP with different
    - User tagging
    - Component listing placeholder
    - Digital Twins listing
    - Snapshots listing
    - Workflow desginer
    - pygwalker data visualization
    - MongoDB is required to be deployed independtly
    - S3 is required to be deployed indepently 

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


## Development 

Developed by SDSC/CSFM