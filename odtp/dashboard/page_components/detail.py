from nicegui import ui
import odtp.mongodb.db as db


from nicegui import ui

class VersionDisplay:
    def __init__(self):
        """init form"""
        self.component = None
        self.version = None
        self.component_id = None
        self.version_id = None
        self.component_options = None
        self.version_options = None
        self.get_component_options()
        self.build_form()

    def get_component_options(self):
        """get component options for the filtering"""
        components = db.get_collection(db.collection_components)
        self.component_options = {
            str(component["_id"]): f"{component.get('componentName')}"
            for component in components
        }

    @ui.refreshable
    def build_form(self):
        """render form elements"""
        self.ui_component_select()
        self.ui_version_select()
        self.show_version_info()

    def reset_version_form(self):
        """reset version form"""
        self.version = None
        self.version_id = None
        self.version_options = None
        self.ui_version_select.refresh()
        self.show_version_info.refresh()

    @ui.refreshable
    def ui_component_select(self):
        """ui element for component select"""
        ui.select(
            self.component_options,
            value=self.component_id,
            on_change=lambda e: self.set_component(str(e.value)),
            label="component",
            with_input=True,
        ).classes("w-1/2")

    def set_component(self, component_id):
        """called when a new component has been selected"""
        self.reset_version_form()
        self.compoment_id = component_id
        self.component = db.get_document_by_id(
            document_id=component_id, collection=db.collection_components
        )
        versions = db.get_sub_collection_items(
            collection=db.collection_components,
            sub_collection=db.collection_versions,
            item_id=component_id,
            ref_name=db.collection_versions,
        )
        self.version_options = {
            str(version["_id"]): f"{version.get('component_version')}"
            for version in versions
        }
        self.ui_version_select.refresh()

    @ui.refreshable
    def ui_version_select(self):
        """ui element version select: rendered when there are version options"""
        if not self.version_options:
            return
        ui.select(
            self.version_options,
            value=self.version_id,
            on_change=lambda e: self.set_version(str(e.value)),
            label="component version",
            with_input=True,
        ).classes("w-1/2")

    def set_version(self, version_id):
        """called from version selection"""
        self.version_id = version_id
        self.version = db.get_document_by_id(
            document_id=version_id, collection=db.collection_versions
        )
        self.show_version_info.refresh()

    @ui.refreshable
    def show_version_info(self):
        """ui element for version info as it comes from github"""
        if not self.version:
            return
        print(self.version)
        parameters = self.version.get("parameters", [])
        if parameters:
            self.display_dict_list("Parameters", "parameters")
        ports = self.version.get("ports", [])
        if ports:
            self.display_dict_list("Ports", "ports")
        secrets = self.version.get("secrets", [])
        if secrets:
            self.display_dict_list("Secrets", "secrets")
        self.display_dict_list("Tool Info", "tools")

    def display_dict_list(self, label, dict_list_name):
        """Display a list of dicts, merging nested structures into key-value pairs."""
        ui.label(label)
        with ui.grid(columns='1fr 5fr').classes('w-full gap-0'):
            for dict_item in self.version.get(dict_list_name, []):
                # Flatten nested dictionaries or lists
                for key, value in dict_item.items():
                    if isinstance(value, dict):  # Merge nested dicts
                        merged_value = ", ".join(f"{k}: {v}" for k, v in value.items())
                    elif isinstance(value, list):  # Merge list of dicts or other values
                        if all(isinstance(i, dict) for i in value):  # List of dicts
                            merged_value = "; ".join(
                                ", ".join(f"{k}: {v}" for k, v in sub_item.items())
                                for sub_item in value
                            )
                        else:  # Simple list
                            merged_value = ", ".join(str(i) for i in value)
                    else:  # Simple key-value pair
                        merged_value = value

                    # Display the key and merged value
                    ui.label(key).classes('bg-gray-200 border p-1')
                    ui.label(merged_value).classes('border p-1')
