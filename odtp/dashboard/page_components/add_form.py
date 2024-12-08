from nicegui import ui
import odtp.mongodb.db as db
import odtp.helpers.git as git_helpers


from nicegui import ui

class ComponentVersionForm:
    def __init__(self):
        self.repo_info = None
        self.repo_url = None
        self.version_options = []
        self.component_version = None
        self.commit_hash = None
        self.metadata = None
        self.build_form()

    def build_form(self):
        self.ui_component_url_input()
        self.ui_version_select()
        self.ui_tool_info()
        self.ui_add_component_version_button()

    def ui_component_url_input(self):
        ui.input(
            label="Enter Repository URL",
            placeholder="repo url",
            on_change=lambda e: self.get_version_options(e.value),
        ).classes("w-1/2")

    def ui_reset_form(self):
        self.version_options = None
        self.repo_info = None
        self.repo_url = None
        self.version_options = []
        self.component_version = None
        self.commit_hash = None
        self.metadata = None
        self.ui_add_component_version_button.refresh()
        self.ui_version_select.refresh()
        self.ui_tool_info.refresh()

    def get_version_options(self, repository):
        self.ui_reset_form()
        self.repo_info = git_helpers.get_github_repo_info(repository)
        self.repo_url = self.repo_info["html_url"]
        self.version_options = {
            (item["name"], item["commit"]): item["name"]
            for item in self.repo_info.get("tagged_versions")
        }
        self.ui_version_select.refresh()

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
        self.commit_hash = version_tuple[1]
        self.metadata = git_helpers.get_metadata_from_github(self.repo_info, self.commit_hash)
        with ui.row().classes("w-full"):
            ui.table
            ui.icon("check").classes("text-teal text-lg")
            ui.label("Metadata parsed from odtp.yml file").classes("text-teal")
        self.ui_add_component_version_button.refresh()
        self.ui_tool_info.refresh()

    @ui.refreshable
    def ui_tool_info(self):
        if not self.metadata:
            return
        for tool in self.metadata['tools']:
            with ui.card().classes("mb-4"):
                ui.label(f"Tool Name: {tool['tool-name']}").classes("text-lg font-bold")
                ui.label(f"Author: {tool['tool-author']}")
                ui.label(f"Version: {tool['tool-version']}")
                ui.label(f"License: {tool['tool-license']}")
                ui.label(f"Repository: {tool['tool-repository']}")

    @ui.refreshable
    def ui_add_component_version_button(self):
        if not self.component_version:
            return
        ui.button(
            "add version",
            icon="add",
            on_click=lambda: self.add_component_version()
        )

    def add_component_version(self):
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
