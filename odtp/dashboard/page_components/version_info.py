from nicegui import ui
from pydantic import BaseModel
from typing import Any
import inspect

class DynamicUI:
    def render_model(self, model: BaseModel, title: str = "Model Details"):
        """Renders a Pydantic model in NiceGUI dynamically."""
        with ui.column().classes("w-full p-4"):
            ui.label(title).classes("text-lg font-bold")
            self._render_fields(model.dict(by_alias=True), model.__class__)

    def _render_fields(self, data: dict, schema: BaseModel):
        """Recursively render fields from the Pydantic model."""
        for field_name, value in data.items():
            field_info = schema.__fields__[field_name]

            with ui.row().classes("w-full items-start gap-4"):
                ui.label(field_info.alias or field_name).classes("font-semibold text-sm w-1/3 truncate")

                if isinstance(value, dict):
                    with ui.column().classes("w-2/3"):
                        ui.expansion("Details").classes("w-full").with_content(lambda: self._render_fields(value, field_info.type_))
                elif isinstance(value, list):
                    with ui.column().classes("w-2/3"):
                        if all(isinstance(v, BaseModel) for v in value):
                            for index, item in enumerate(value):
                                with ui.expansion(f"Item {index + 1}").classes("w-full"):
                                    self._render_fields(item.dict(), item.__class__)
                        else:
                            ui.label(str(value)).classes("text-sm")
                elif isinstance(value, BaseModel):
                    with ui.column().classes("w-2/3"):
                        self._render_fields(value.dict(), value.__class__)
                else:
                    ui.label(str(value)).classes("text-sm w-2/3 truncate")
