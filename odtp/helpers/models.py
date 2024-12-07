from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union


# Define Pydantic models for the nested structures
class DataInput(BaseModel):
    name: str
    type: str
    path: str
    description: str


class DataOutput(BaseModel):
    description: str
    name: str
    path: str
    type: str


class Parameter(BaseModel):
    name: str
    datatype: str
    description: str
    default_value: Optional[str] = Field(alias="default-value")
    options: Optional[List[str]] = None
    allow_custom_value: Optional[bool] = Field(alias="allow-custom-value", default=None)


class Port(BaseModel):
    name: str
    description: str
    port_value: int = Field(alias="port-value")


class Tool(BaseModel):
    tool_author: str = Field(alias="tool-author")
    tool_license: str = Field(alias="tool-license")
    tool_name: str = Field(alias="tool-name")
    tool_repository: str = Field(alias="tool-repository")
    tool_version: str = Field(alias="tool-version")


class Devices(BaseModel):
    gpu: bool


class OdtpDotYamlSchema(BaseModel):
    build_args: Optional[Union[dict, str]] = Field(alias="build-args", default=None)
    component_author: str = Field(alias="component-author")
    component_description: str = Field(alias="component-description")
    component_license: str = Field(alias="component-license")
    component_name: str = Field(alias="component-name")
    component_repository: str = Field(alias="component-repository")
    component_type: str = Field(alias="component-type")
    component_version: str = Field(alias="component-version")
    data_inputs: Optional[List[DataInput]] = Field(alias="data-inputs", default=None)
    data_output: Optional[List[DataOutput]] = Field(alias="data-output", default=None)
    devices: Devices
    parameters: Optional[List[Parameter]] = None
    ports: Optional[List[Port]] = None
    schema_input: Optional[Union[dict, str]] = Field(alias="schema-input", default=None)
    schema_output: Optional[Union[dict, str]] = Field(alias="schema-output", default=None)
    secrets: Optional[List[Parameter]] = None
    tags: List[str]
    tools: Optional[List[Tool]] = None

    @validator("component_type")
    def validate_component_type(cls, value):
        allowed_types = {"ephemeral", "persistent", "interactive"}
        if value not in allowed_types:
            raise ValueError(f"component-type must be one of {allowed_types}")
        return value
