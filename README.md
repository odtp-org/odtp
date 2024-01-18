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
