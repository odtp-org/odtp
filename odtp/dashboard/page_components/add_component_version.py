import json
from nicegui import ui
import odtp.mongodb.db as db
import odtp.helpers.git as git_helpers


from nicegui import ui

class ComponentVersionForm:
    def __init__(self):
        """intialize form"""
        self.repo_info = None
        self.parse_error = None
        self.repo_url = None
        self.add_new_component = False
        self.component_id = None
        self.version_options = []
        self.component_version = None
        self.metadata = None
        self.build_form()

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_component_or_version()
        self.ui_component_select_form()
        self.ui_new_component_form()
        self.ui_version_select()
        self.ui_metadata()
        self.ui_parse_error()
        self.ui_add_component_version_button()

    @ui.refreshable
    def ui_component_or_version(self):
        with ui.row().classes("w-full items-center"):
            ui.label("Add new version of existing component")
            ui.switch(
                "Add new Component",
                value=self.add_new_component,
                on_change=lambda e: self.set_add_new_component(e.value)
            )

    def set_add_new_component(self, value):
        print(f"set add new component {value}")
        self.add_new_component = value
        self.repo_info = None
        self.parse_error = None
        self.repo_url = None
        self.component_id = None
        self.version_options = []
        self.component_version = None
        self.commit_hash = None
        self.metadata = None
        self.build_form.refresh()

    @ui.refreshable
    def ui_new_component_form(self):
        if not self.add_new_component:
            return
        ui.input(
            label="Enter Repository URL",
            placeholder="repo url",
            on_change=lambda e: self.get_version_options_new_component(repository=e.value),
        ).classes("w-1/2")

    @ui.refreshable
    def ui_component_select_form(self):
        if self.add_new_component:
            return
        components = db.get_collection(db.collection_components)
        self.component_options = {
            str(component["_id"]): f"{component.get('componentName')}"
            for component in components
        }
        ui.select(
            self.component_options,
            on_change=lambda e: self.get_version_option_existing_component(component_id=e.value),
            label="component",
            with_input=True,
        ).classes("w-1/2")

    def get_version_options_new_component(self, repository):
        self.repo_info = None
        self.parse_error = None
        self.repo_url = None
        self.component_id = None
        self.version_options = []
        self.component_version = None
        self.metadata = None
        self.repo_info = git_helpers.get_github_repo_info(repository)
        self.repo_url = self.repo_info["html_url"]
        self.version_options = {
            (item["name"], item["commit"]): item["name"]
            for item in self.repo_info.get("tagged_versions")
        }
        self.ui_version_select.refresh()
        self.ui_metadata.refresh()
        self.ui_parse_error.refresh()
        self.ui_add_component_version_button.refresh()

    def get_version_option_existing_component(self, component_id):
        self.repo_info = None
        self.parse_error = None
        self.repo_url = None
        self.component_id = None
        self.version_options = []
        self.component_version = None
        self.metadata = None
        if not component_id:
            return
        self.component_id = component_id
        self.component = db.get_document_by_id(
            document_id=component_id, collection=db.collection_components
        )
        repository = self.component["repoLink"]
        self.existing_versions = db.get_sub_collection_items(
            collection=db.collection_components,
            sub_collection=db.collection_versions,
            item_id=self.component_id,
            ref_name=db.collection_versions,
        )
        existing_component_versions = [
            version["component_version"] for version in self.existing_versions
        ]
        self.repo_info = git_helpers.get_github_repo_info(repository)
        self.repo_url = self.repo_info["html_url"]
        self.version_options = {
            (item["name"], item["commit"]): item["name"]
            for item in self.repo_info.get("tagged_versions")
            if item["name"] not in existing_component_versions
        }
        self.ui_version_select.refresh()
        self.ui_metadata.refresh()
        self.ui_parse_error.refresh()
        self.ui_add_component_version_button.refresh()

    @ui.refreshable
    def ui_version_select(self):
        if not self.version_options:
            return
        ui.select(
            label="component version",
            options=self.version_options,
            on_change=lambda e: self.parse_metadata(e.value),
        ).classes("w-1/3")

    def parse_metadata(self, version_tuple):
        self.component_version = version_tuple[0]
        commit_hash = version_tuple[1]
        try:
             self.metadata = git_helpers.get_metadata_from_github(self.repo_info, commit_hash)
        except Exception as e:
            self.parse_error = e
        self.ui_metadata.refresh()
        self.ui_parse_error.refresh()


    @ui.refreshable
    def ui_parse_error(self):
        if not self.parse_error:
            return
        with ui.row().classes("w-full"):
            ui.icon("clear").classes("text-red text-lg")
            ui.label("Metadata parsed from odtp.yml file:").classes("text-red")
        ui.label(str(self.parse_error)).classes("text-red")

    @ui.refreshable
    def ui_metadata(self):
        if not self.metadata:
            return
        with ui.row().classes("w-full"):
            ui.icon("check").classes("text-teal text-lg")
            ui.label("Metadata parsed from odtp.yml file").classes("text-teal")
        self.ui_add_component_version_button.refresh()

    @ui.refreshable
    def ui_add_component_version_button(self):
        if not self.component_version:
            return
        ui.button(
            "add version",
            icon="add",
            on_click=lambda: self.db_add_component_version()
        )

    def db_add_component_version(self):
        """add component version"""
        component_id, version_id = db.add_component_version(
            repository=self.repo_url,
            component_version=self.component_version
        )
        ui.notify(
            f"Component version {component_id} / {version_id} has been added",
            type="positive",
        )
        from odtp.dashboard.page_components.main import ui_tabs
        ui_tabs.refresh()
