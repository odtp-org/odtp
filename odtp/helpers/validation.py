from odtp.helpers.models import OdtpDotYamlSchema
from pydantic import ValidationError


class OdtpYmlException(Exception):
    """For the GUI it is important that the error message can be rendered"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


def validate_odtp_yml_file(yaml_data):
    """validates the odtp.yml file against the schema and provides
    information on errors that occur"""
    try:
        validated_data = OdtpDotYamlSchema(**yaml_data)
        return validated_data
    except ValidationError as ve:
        error_details = "\n".join(
            [f"{err['loc']}: {err['msg']} (type: {err['type']})" for err in ve.errors()]
        )
        raise OdtpYmlException(f"Validation failed for odtp.yml:\n{error_details}")
    except Exception as e:
        raise OdtpYmlException(f"Unexpected error during odtp.yml validation: {e}")
