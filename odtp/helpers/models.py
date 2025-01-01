from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union

# Define Pydantic models for the nested structures
class ComponentAuthor(BaseModel):
    name: str
    orcid: Optional[str] = None

class ToolAuthor(BaseModel):
    name: str
    orcid: Optional[str] = None

class ToolRepository(BaseModel):
    url: str
    doi: Optional[str] = None

class DataInput(BaseModel):
    name: str
    type: str
    path: str
    description: str

class Tool(BaseModel):
    tool_name: str = Field(alias="tool-name")
    tool_authors: List[ToolAuthor] = Field(alias="tool-authors")
    tool_version: Optional[str] = Field(alias="tool-version", default=None)
    tool_repository: ToolRepository = Field(alias="tool-repository")
    tool_license: str = Field(alias="tool-license")

class Parameter(BaseModel):
    name: str
    datatype: str
    description: str
    default_value: Optional[Union[str, int, float, bool]] = Field(alias="default-value")
    options: Optional[List[str]] = None
    allow_custom_value: Optional[bool] = Field(alias="allow-custom-value", default=None)

class DataOutput(BaseModel):
    name: str
    type: str
    path: str
    description: str

class Device(BaseModel):
    type: str
    required: bool

class Port(BaseModel):
    name: str
    description: str
    port_value: int = Field(alias="port-value")

class OdtpDotYamlSchema(BaseModel):
    schema_version: str = Field(alias="schema-version")
    component_name: str = Field(alias="component-name")
    component_version: str = Field(alias="component-version")
    component_license: str = Field(alias="component-license")
    component_type: str = Field(alias="component-type")
    component_description: str = Field(alias="component-description")
    component_authors: List[ComponentAuthor] = Field(alias="component-authors")
    component_repository: ToolRepository = Field(alias="component-repository")
    component_docker_image: Optional[str] = Field(alias="component-docker-image", default=None)
    tags: List[str]
    tools: Optional[List[Tool]] = None
    secrets: Optional[dict] = None
    build_args: Optional[dict] = Field(alias="build-args", default=None)
    ports: Optional[List[Port]] = Field(default=None)
    parameters: Optional[List[Parameter]] = None
    data_inputs: Optional[List[DataInput]] = Field(alias="data-inputs", default=None)
    data_output: Optional[List[DataOutput]] = Field(alias="data-output", default=None)
    schema_input: Optional[dict] = Field(alias="schema-input", default=None)
    schema_output: Optional[dict] = Field(alias="schema-output", default=None)
    devices: Optional[List[Device]] = None

    @validator("component_type")
    def validate_component_type(cls, value):
        allowed_types = {"ephemeral", "persistent", "interactive"}
        if value not in allowed_types:
            raise ValueError(f"component-type must be one of {allowed_types}")
        return value
