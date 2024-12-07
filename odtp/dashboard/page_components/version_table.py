from nicegui import ui
import odtp.mongodb.db as db


from nicegui import ui

class VersionTable:
    def __init__(self, versions):
        self.versions = [self.clean_version(version) for version in versions]
        self.version_rows = []
        self.selected_version_ids = set()
        self.filtered_versions = [
            version for version in self.versions
            if not version.get("deprecated", False)
        ]
        self.component_id = None
        self.show_deprecated = False
        self.build_table()

    def clean_version(self, version):
        version["version_id"] = str(version["_id"])
        if version.get("deprecated") == None:
            version["deprecated"] = False
        if version["deprecated"]:
            version["deprecated_display"] = "deprecated"
        else:
            version["deprecated_display"] = ""
        return version

    def build_table(self):
        with ui.column().classes("w-full"):
            self.add_component_selector()
            self.add_header()
            self.add_rows()

    def add_component_selector(self):
        components = db.get_collection(db.collection_components)
        components_options = {
            str(component["_id"]): f"{component.get('componentName')}"
            for component in components
        }
        if components:
            with ui.row().classes("w-full"):
                ui.select(
                    components_options,
                    on_change=lambda e: self.filter_components(str(e.value)),
                    label="component",
                    with_input=True,
                ).classes("w-1/2")
                ui.checkbox(
                    "Show deprecated",
                    on_change=lambda e: self.filter_deprecated(e.value)
                ).classes("w-1/8")
                ui.button(
                    "Reset selection",
                    on_click=lambda e: self.filter_reset(),
                    icon="clear",
                ).props("flat").classes("w-1/8")
                ui.button(
                    "delete_selected",
                    on_click=lambda: self.delete_selected(),
                    icon="clear",
                ).props("flat").classes("w-1/8")

    def add_header(self):
        headers = [
            "Select",
            "Component",
            "Version",
            "Repository",
            "Commit",
            "Type",
            "Created At",
            "ODTP Version",
            "deprecated",
        ]
        with ui.row().classes("w-full bg-gray-200 p-2 border-b grid grid-cols-10 gap-4"):
            for header in headers:
                ui.label(header).classes("font-bold text-center truncate")

    @ui.refreshable
    def add_rows(self):
        self.version_rows.clear()
        for version in self.filtered_versions:
            with ui.row().classes("w-full p-2 border grid grid-cols-10 gap-4 items-center"):
                checkbox = ui.checkbox(
                    on_change=lambda e, version_id=version["version_id"]: self.toggle_selection(e.value, version_id)
                )
                ui.label(version['component']['componentName']).classes("truncate")
                ui.label(version['component_version']).classes("truncate")
                ui.link(version['component']['repoLink'], version['component']['repoLink']).classes("truncate")
                ui.label(version['commitHash'][:8]).classes("text-center truncate")
                ui.label(version['component'].get("type") or version.get("type")).classes("text-center truncate")
                ui.label(version['created_at'].strftime('%Y-%m-%d')).classes("text-center truncate")
                ui.label(version['odtp_version']).classes("text-center truncate")
                ui.label(version["deprecated_display"]).classes("truncate")
                #self.version_rows.append(checkbox)

    def toggle_selection(self, selected, version_id):
        print(f"Toggle called: {selected} for version_id: {version_id}")
        if selected:
            self.selected_version_ids.add(version_id)
        else:
            self.selected_version_ids.remove(version_id)

    def filter_components(self, component_id):
        self.component_id = component_id
        self.rebuild_rows()

    def filter_reset(self):
        self.component_id = None
        self.show_deprecated = False
        self.rebuild_rows()

    def filter_deprecated(self, show_deprecated):
        self.show_deprecated = show_deprecated
        self.rebuild_rows()

    def rebuild_rows(self):
        self.filtered_versions = self.versions
        if self.component_id:
            self.filtered_versions = [
                version for version in self.versions
                if str(version["componentId"]) == self.component_id
            ]
        if not self.show_deprecated:
            self.filtered_versions = [
                version for version in self.filtered_versions
                if not version.get("deprecated", False)
            ]
        self.add_rows.refresh()

    def delete_selected(self):
        db.delete_component_version_safe(self.selected_version_ids)
        ui.notify(
            f"The selected {len(self.selected_version_ids)} component versions have been deprecated/deleted.",
            type="positive"
        )
        from odtp.dashboard.page_components.main import ui_components_list
        ui_components_list.refresh()
