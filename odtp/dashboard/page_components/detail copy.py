from pprint import pprint
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
        components = db.get_collection(db.collection_components, include_deprecated=False)
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
            include_deprecated=False,
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
        """UI element for displaying version info in a user-friendly format."""
        if not self.version:
            return
        with ui.card().classes('w-full p-4'):
            if "commitHash" in self.version:
                ui.label(f"Commit Hash: {self.version['commitHash']}").classes('mb-2 text-gray-700')
            if "tools" in self.version:
                self.display_tools(self.version.get("tools"))

    def display_tools(self, tools):
        """Display the tools section in a compact format."""
        for tool in tools:
            with ui.row().classes("justify-between items-center mb-2"):
                ui.label(tool.get('tool-name', 'Unknown Tool')).classes("font-bold text-gray-800")
                ui.label(f"Version: {tool.get('tool-version', 'N/A')}").classes("text-sm text-gray-600")

            # Authors Section
            authors = tool.get('tool-authors', [])
            if authors:
                author_labels = [
                    f"{author['name']} ({ui.link('ORCID', author['orchid']).classes('text-blue-500 underline')})"
                    if author.get('orchid') else author['name']
                    for author in authors
                ]
                ui.label(f"Authors: {', '.join(author_labels)}").classes("text-sm text-gray-700 mb-1")

            # License
            ui.label(f"License: {tool.get('tool-license', 'Unknown')}").classes("text-sm text-gray-700 mb-1")

            # Repository Section
            repository = tool.get('tool-repository', {})
            repo_details = []
            if repository.get('url'):
                repo_details.append(ui.link("Repository URL", repository['url']).classes("text-blue-500 underline"))
            if repository.get('doi'):
                repo_details.append(f"DOI: {repository['doi']}")
            if repo_details:
                ui.label(" | ".join(repo_details)).classes("text-sm text-gray-700")

"""
 'tools': [{'tool-authors': [{'name': 'Sebastian Hörl',
                              'orchid': 'https://orcid.org/0000-0002-9018-432X'},
                             {'name': 'S. and M. Balac',
                              'orchid': 'https://orcid.org/0000-0002-6099-7442'}],
            'tool-license': 'GPL-2.0 License',
            'tool-name': 'eqasim-org/ile-de-france',
            'tool-repository': {'doi': None,
                                'url': 'https://github.com/eqasim-org/ile-de-france'},
            'tool-version': 'fb1112d2a7d1817746be84413da584c391059ad1'},
           {'tool-authors': [{'name': 'Sebastian Hörl',
                              'orchid': 'https://orcid.org/0000-0002-9018-432X'},
                             {'name': 'S. and M. Balac',
                              'orchid': 'https://orcid.org/0000-0002-6099-7442'}],
            'tool-license': 'GPL-2.0 License',
            'tool-name': 'ivt-vpl/populations/ch-zh-synpop',
            'tool-repository': {'doi': None,
                                'url': 'https://gitlab.ethz.ch/ivt-vpl/populations/ch-zh-synpop'},
            'tool-version': '4658daa2e441dcda132622e7fcb47da1df8c47d6'}],
"""