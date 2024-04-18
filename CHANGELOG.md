## Changelog
- v.0.2.3: Feature
    - Expose dashboard parameters: port and reload
    
- v.0.2.2: Bugs correction
    - Including submodules when cloning file

- v.0.2.1: Add docker compose for easy setup
    - add compose.yml: it can be build with `docker compose up`
    - check `.env` file with `docker compose config`
    - remove data mockup 
    - environment variables now loaded from the environment


- v.0.2.0: Improvements in database and files management.
    - New MongoDB Schema supporting users, digital twins, executions, and steps. 
    - Setup uses pyproject.toml and set up method changed to poetry
    - mongodb access function modified so that they can be used by both the GIU and the CLI
    - CLI refactored with methods for creating and managing digital twins, and executions. 
    - Automatic preparation of project folders for executions. 
    - S3 uploading of outputs from each component.
    - Switch UI from Streamlit to Nicegui


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
