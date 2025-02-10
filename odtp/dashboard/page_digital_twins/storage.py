import json
from nicegui import app
import odtp.dashboard.utils.storage as storage


def get_current_user_from_storage():
    return storage.get_active_object_from_storage(storage.CURRENT_USER)


def storage_get_current_digital_twin():
    return storage.get_active_object_from_storage(storage.CURRENT_DIGITAL_TWIN)


def set_current_digital_twin(db_digital_twin):
    current_digital_twin = json.dumps({
        "digital_twin_id": str(db_digital_twin["_id"]),
        "digital_twin_name": db_digital_twin["name"],
        "created_at": db_digital_twin["created_at"].strftime("%Y-%m-%d"),
        "updated_at": db_digital_twin["updated_at"].strftime("%Y-%m-%d"),
        "execution_count": str(len(db_digital_twin["executions"]))
    })
    app.storage.user[storage.CURRENT_DIGITAL_TWIN] = current_digital_twin
    storage.reset_storage_keep(
        [
            storage.CURRENT_USER,
            storage.CURRENT_DIGITAL_TWIN,
        ]
    )
