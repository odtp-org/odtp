from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union

class Author(BaseModel):
    name: str
    orcid: Optional[str] = None

class ComponentRepository(BaseModel):
    url: str
    doi: Optional[str] = None

class ToolAuthor(BaseModel):
    name: str
    orcid: Optional[str] = None

class ToolRepository(BaseModel):
    url: str
    doi: Optional[str] = None

class Tool(BaseModel):
    tool_name: str = Field(alias="tool-name")
    tool_authors: Optional[List[ToolAuthor]] = Field(alias="tool-authors", default=None)
    tool_version: str = Field(alias="tool-version")
    tool_repository: ToolRepository = Field(alias="tool-repository")
    tool_license: str = Field(alias="tool-license")

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

class Device(BaseModel):
    type: str
    required: bool

class OdtpDotYamlSchema(BaseModel):
    """Model for odtp.yml parsing"""
    schema_version: str = Field(alias="schema-version")
    component_name: str = Field(alias="component-name")
    component_version: str = Field(alias="component-version")
    component_license: str = Field(alias="component-license")
    component_type: str = Field(alias="component-type")
    component_description: str = Field(alias="component-description")
    component_authors: List[Author] = Field(alias="component-authors")
    component_repository: ComponentRepository = Field(alias="component-repository")
    component_docker_image: str = Field(alias="component-docker-image")
    tags: List[str]
    tools: Optional[List[Tool]] = None
    secrets: Optional[Union[List[Parameter], None]] = None
    build_args: Optional[Union[dict, str]] = Field(alias="build-args", default=None)
    ports: Optional[List[Port]] = None
    parameters: Optional[List[Parameter]] = None
    data_inputs: Optional[List[DataInput]] = Field(alias="data-inputs", default=None)
    data_output: Optional[List[DataOutput]] = Field(alias="data-output", default=None)
    schema_input: Optional[Union[dict, str]] = Field(alias="schema-input", default=None)
    schema_output: Optional[Union[dict, str]] = Field(alias="schema-output", default=None)
    devices: List[Device]

    @validator("component_type")
    def validate_component_type(cls, value):
        allowed_types = {"ephemeral", "persistent", "interactive"}
        if value not in allowed_types:
            raise ValueError(f"component-type must be one of {allowed_types}")
        return value
