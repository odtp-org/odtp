import logging

from nicegui import ui

import odtp.dashboard.page_workflows.add as add
import odtp.dashboard.page_workflows.detail as detail

log = logging.getLogger(__name__)


def content() -> None:
    ui_workarea()
    ui_tabs()


@ui.refreshable
def ui_tabs():
    with ui.tabs() as tabs:
        list = ui.tab("Manage Workflows")
        show_workflow = ui.tab("Workflow Details")
        add_workflow = ui.tab("Add Workflow")
    with ui.tab_panels(tabs, value=list).classes("w-full"):
        with ui.tab_panel(list):
            ui_workflow_list()
        with ui.tab_panel(show_workflow):
            ui_workflow_detail()
        with ui.tab_panel(add_workflow):
            ui_add_workflow()


@ui.refreshable
def ui_workflow_list():
    #table.WorkflowTable()
    pass


@ui.refreshable
def ui_workflow_detail():
    with ui.column().classes("w-full"):
        #detail.WorkflowDisplay()
        pass


@ui.refreshable
def ui_add_workflow():
    with ui.column().classes("w-full"):
        add.WorkflowForm()


@ui.refreshable
def ui_workarea():
    ui.markdown(
        """
        ## Manage Workflows
        ODTP Workflows are Templates for Executions:

        - Workflows are not user specific
        - Only tagged Versions of Components can be added

        Learn more at the
        [Documentation of ODTP](https://odtp-org.github.io/odtp-manuals)
        """
    )