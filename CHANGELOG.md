## Changelog

- v0.4.0
    - gui: the general workflow for the user was improved (new Items are selected automatically for example)
    - gui: validation has been implemented in the forms to make sure data that is entered will be valid
    - gui: the run page for executions has been improved in the gui: logs are now also available from the gui when a workflow runs
    - gui: on the dashboard homepage you can now directly see whether all services including github are connected
    - gui: the workarea in the dashboard was removed and replace by an info section on top of the pages
    - logging: improve logging at GUI/CLI: run commands are now logged to a file, while everything else is still logged to the command line: this is so run commands can be easier debugged by knowing what was run in docker and how that run was triggered 
    - logging: the logs of the execution runs are now exposed as volumes, so that will be directly available when the component starts and will remain in the project path even after a component exited prematurely
    - execution: execution and step timestamps
    - cli: printing table from mongodb colleciton
    - cli: delete methods for execution and related items. 
    - components: avoid rebuilding image if component is available
    - compose: a dev version for docker compose has been added to facilitate development

- v0.3.1 
    - hotfixes for bugs
    - removal of unused dependencies and adition of pandas

- v0.3.0 dashboard refactoring
    - dashboard was refactored since code files were getting too long
    - homepage of the dashboard got an upgrade and also contains now connection checks
    - the execution run page is now only accessible via the execution
    - the workflow in the dashboard has been improved
    - the docker compose setup has now a dev and a prod file
    - log levels for dashboard and docker runs can now be set separately   

- v0.2.8: bug fixes and settings updates

- v0.2.7 hotfix for environment variable
    - hotfix ODTP port in docker compose

- v0.2.6: Bugs correction
    - Missing `ODTP_PATH` in `compose.yml`. 

- v0.2.5: Bugs corrections and new features
    - Components tags parsing
    - CLI compatibility with digital twins and executions names
    - GUI user's working directory implementation
    - GUI executions improvements

- v0.2.4: Feature
    - Network added to compose so odtp components can use it
    - Introducing `secrets` compatibility

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
