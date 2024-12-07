from odtp.helpers.models import OdtpDotYamlSchema
from pydantic import ValidationError


class OdtpYmlException(Exception):
    pass


def validate_odtp_yml_file(yaml_data):
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
