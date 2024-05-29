from nicegui import ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.validators as validators
import odtp.mongodb.db as db


class ContainerWorkflow(object):
    def __init__(self, versions, version_tags):
        self.container = ui.row().classes("w-full")
        self.select_options = self.get_select_options()
        self.versions = versions
        self.version_tags = version_tags
        self.add_buttons()
        if self.version_tags:
            self.prefill()
        else:
            self.add_step()

    def get_select_options(self):
        component_versions = db.get_collection_sorted(
            collection=db.collection_versions,
            sort_tuples=[
                ("component.componentName", db.ASCENDING),
                ("component_version", db.DESCENDING),
            ],
        )
        select_options = {}
        for version in component_versions:
            version_display_name = helpers.get_execution_step_display_name(
                component_name=version["component"]["componentName"],
                component_version=version["component_version"],
            )
            select_options[(str(version["_id"]), version_display_name)] = (
                f"{version_display_name}"
            )
        return select_options

    def add_step(self, value=""):
        with self.container:
            ui.select(
                self.select_options,
                label="component versions",
                validation={
                    f"Please provide an component version": lambda value: validators.validate_required_input(
                        value
                    )
                },
                value=value,
            ).classes("w-full bg-violet-100")

    def remove_step(self):
        if list(self.container) and len(list(self.container)) > 1:
            self.container.remove(-1)

    def prefill(self):
        if self.version_tags:
            for index, version_tag in enumerate(self.version_tags):
                self.add_step(value=(str(self.versions[index]), version_tag))

    def add_buttons(self):
        with ui.grid(columns=2):
            ui.button(
                "Add workflow step",
                on_click=self.add_step,
                icon="add",
            ).props(
                "flat"
            ).classes("w-full")
            ui.button(
                "Remove workflow step",
                on_click=self.remove_step,
                icon="remove",
            ).props("flat").classes("w-full")

    def get_steps(self):
        steps = []
        for item in self.container:
            if item and item.tag == "nicegui-select":
                steps.append(item)
        return steps
