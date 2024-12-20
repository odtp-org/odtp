from nicegui import ui
import odtp.mongodb.db as db


from nicegui import ui

class VersionTable:
    def __init__(self):
        """intialize the form"""
        self.versions = db.get_collection(
            collection=db.collection_versions,
        )
        if not self.versions:
            ui.label("No components yet").classes("text-red-500")
            return
        self.version_rows = []
        self.selected_version_ids = set()
        self.filtered_versions = [
            version for version in self.versions
            if not version.get("deprecated", False)
        ]
        self.component_id = None
        self.component_name = None
        self.show_deprecated = False
        self.build_table()

    def build_table(self):
        """build the table"""
        with ui.column().classes("w-full"):
            self.table_selectors()
            self.add_header()
            self.add_rows()

    @ui.refreshable
    def table_selectors(self):
        """set the table selectors"""
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
            with ui.row().classes("w-full"):
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
                    "Deprecate selected",
                    on_click=lambda: self.deprecate_selected(),
                    icon="clear",
                ).props("flat").classes("w-1/8")
                ui.button(
                    "Activate selected",
                    on_click=lambda: self.activate_selected(),
                    icon="add",
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
        ]
        with ui.row().classes("w-full bg-gray-200 p-2 border-b grid grid-cols-10 gap-4"):
            for header in headers:
                ui.label(header).classes("font-bold text-center truncate")

    def get_deprecated_display(self, deprecated):
        if deprecated:
            return "deprecated"
        else:
            return ""

    @ui.refreshable
    def add_rows(self):
        """set the table rows"""
        self.version_rows.clear()
        for version in self.filtered_versions:
            if version.get("deprecated"):
                color = "text-gray-500"
            else:
                color = ""
            with ui.row().classes("w-full p-2 border grid grid-cols-10 gap-4 items-center"):
                ui.checkbox(
                    on_change=lambda e, version_id=version["_id"]: self.toggle_selection(e.value, version_id)
                )
                ui.label(version['component']['componentName']).classes(f"truncate {color}")
                ui.label(version['component_version']).classes(f"truncate {color}")
                ui.link(version['component']['repoLink'], version['component']['repoLink']).classes(f"truncate {color}")
                ui.label(version['commitHash'][:8]).classes(f"text-center truncate {color}")
                ui.label(version['component'].get("type") or version.get("type")).classes(f"text-center truncate {color}")
                ui.label(version['created_at'].strftime('%Y-%m-%d')).classes(f"text-center truncate {color}")
                ui.label(version['odtp_version']).classes(f"text-center truncate {color}")

    def toggle_selection(self, selected, version_id):
        """toggle select for delete of versions"""
        print(f"Toggle called: {selected} for version_id: {version_id}")
        if selected:
            self.selected_version_ids.add(version_id)
        else:
            self.selected_version_ids.remove(version_id)

    def filter_components(self, component_id):
        """filter by component"""
        self.component_id = component_id
        self.rebuild_rows()

    def filter_reset(self):
        """rebuild rows in original state"""
        self.component_id = None
        self.component_name = None
        self.show_deprecated = False
        self.rebuild_rows()
        self.table_selectors.refresh()

    def filter_deprecated(self, show_deprecated):
        """filter out deprecated"""
        self.show_deprecated = show_deprecated
        self.rebuild_rows()

    def rebuild_rows(self):
        """rebuild rows with filters"""
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

    def deprecate_selected(self):
        """deprecate selected versions"""
        db.deprecate_documents_by_ids_in_collection(self.selected_version_ids, db.collection_versions)
        ui.notify(
            f"The selected {len(self.selected_version_ids)} component versions have been deprecated.",
            type="positive"
        )
        from odtp.dashboard.page_components.main import ui_components_list
        ui_components_list.refresh()

    def activate_selected(self):
        """activate selected versions"""
        db.activate_documents_by_ids_in_collection(self.selected_version_ids, db.collection_versions)
        ui.notify(
            f"The selected {len(self.selected_version_ids)} component versions have been activated.",
            type="positive"
        )
        from odtp.dashboard.page_components.main import ui_components_list
        ui_components_list.refresh()
