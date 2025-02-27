from collections import namedtuple
from nicegui import ui
import odtp.mongodb.db as db
import odtp.dashboard.utils.ui_theme as ui_theme

DisplayItem = namedtuple('DisplayItem', ['key', 'display_value', 'url'])

class VersionDisplay:
    def __init__(self, version_id):
        self.component = None
        self.version = None
        self.component_id = None
        self.component_options = None
        self.version_options = None
        if version_id:
            self.version_id = version_id
            self.set_component_version()
        else:
            self.version_id = None
        self.get_component_options()
        self.build_form()

    def get_component_options(self):
        components = db.get_collection(db.collection_components, include_deprecated=False)
        self.component_options = {
            str(component["_id"]): f"{component.get('componentName')}"
            for component in components
        }

    def get_version_options(self):
        if not self.component_id:
            return
        versions = db.get_sub_collection_items(
            collection=db.collection_components,
            sub_collection=db.collection_versions,
            item_id=self.component_id,
            ref_name=db.collection_versions,
            include_deprecated=False,
        )
        self.version_options = {
            str(version["_id"]): f"{version.get('component_version')}"
            for version in versions
        }

    @ui.refreshable
    def build_form(self):
        self.ui_component_select()
        self.ui_version_select()
        self.ui_component_version_info()

    @ui.refreshable
    def ui_component_select(self):
        ui.select(
            self.component_options,
            value=self.component_id,
            on_change=lambda e: self.set_component_from_form(str(e.value)),
            label="component",
            with_input=True,
        ).classes("w-1/2")

    def set_component_from_form(self, component_id):
        if self.component_id == component_id:
            return
        self.component_id = component_id
        self.version = None
        self.version_id = None
        self.version_options = None
        self.component = db.get_document_by_id(
            document_id=component_id, collection=db.collection_components
        )
        self.get_version_options()
        self.ui_version_select.refresh()
        self.ui_component_version_info.refresh()

    @ui.refreshable
    def ui_component_version_info(self):
        if not self.version:
            return
        with ui.grid(columns="1fr 1fr"):
            with ui.column():
                self.show_version_info()
            with ui.column():
                self.show_component_info()
                self.show_tools_info()

    @ui.refreshable
    def ui_version_select(self):
        if not self.version_options:
            return
        ui.select(
            self.version_options,
            value=self.version_id,
            on_change=lambda e: self.form_set_component_version(str(e.value)),
            label="component version",
            with_input=True,
        ).classes("w-1/2")

    def form_set_component_version(self, version_id):
        if version_id == self.version_id:
            return
        self.version_id = version_id
        self.set_component_version()
        self.ui_component_version_info.refresh()

    def set_component_version(self):
        self.version = db.get_document_by_id(
            document_id=self.version_id, collection=db.collection_versions
        )
        if not self.version:
            self.version_id = None
            return
        if not self.component_id:
            self.component_id = str(self.version["componentId"])
            self.component = db.get_document_by_id(
                document_id=self.component_id,
                collection=db.collection_components
            )

    def show_component_info(self):
        if not self.version:
            return
        component = self.version["component"]
        required_devices = []
        for device in self.version["devices"]:
            if device["required"] == True:
                required_devices.append(device)
        component_display_item_list = [
            DisplayItem("repository", component["componentName"], component["repoLink"]),
            DisplayItem("description", self.version["description"], None),
            DisplayItem("type", component["type"], None),
            DisplayItem("commit", self.version["commitHash"], None),
            DisplayItem("build args", self.version["build-args"], None),
            DisplayItem("created at", self.version["created_at"], None),
            DisplayItem("license", self.version["license"], None),
            DisplayItem("image link", component["componentName"], None),
            DisplayItem("devices", required_devices, None),
            DisplayItem("odtp_version", self.version["odtp_version"], None),
        ]
        ui.label(f"Component Version Info").classes("text-lg")
        ui_theme.display_items_dict_with_links(component_display_item_list)

    def show_tools_info(self):
        if not self.version:
            return
        tools = self.version.get("tools")
        if not tools:
            self.display_section_empty("Tools Info")
            return
        ui.label("Tools Info").classes("text-lg")
        tool_display_item_list = []
        for tool in tools:
            authors = tool.get("tool-authors")
            if authors:
                author = authors[0]
                tool_display_item_list.append(
                    DisplayItem(
                        "authors",
                        author["name"],
                        author.get("orchid", None)
                    )
                )
                if len(authors) > 1:
                    for author in authors[1:]:
                        tool_display_item_list.append(
                            DisplayItem(
                                "",
                                author["name"],
                                author.get("orchid", None)
                            )
                        )
            tool_display_item_list.extend([
                DisplayItem("license", tool.get("tool-license", "no license"), None),
                DisplayItem("name", tool.get("tool-name"), None),
                DisplayItem("repository url", tool["tool-repository"].get("url"), None),
                DisplayItem("           doi", tool["tool-repository"].get("doi"), None),
                DisplayItem("version", tool.get("tool-version"), None),
            ])
            ui_theme.display_items_dict_with_links(tool_display_item_list)

    def show_version_info(self):
        if not self.version:
            return
        ui_theme.ui_version_section_content(self.version, "Parameters", "parameters")
        ui_theme.ui_version_section_content(self.version, "Ports", "ports")
        ui_theme.ui_version_section_content(self.version, "Secrets", "secrets")
        ui_theme.ui_version_section_content(self.version, "Inputs", "data-inputs")
        ui_theme.ui_version_section_content(self.version, "Outputs", "data-outputs")
