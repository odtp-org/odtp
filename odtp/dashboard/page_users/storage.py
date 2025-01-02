import json
from nicegui import app
import odtp.dashboard.utils.storage as storage


def storage_set_current_user(user_id, user_name, workdir):
    current_user = json.dumps(
        {"user_id": user_id, "user_name": user_name, "workdir": workdir}
    )
    app.storage.user[storage.CURRENT_USER] = current_user
    storage.reset_storage_keep([storage.CURRENT_USER])


def storage_get_current_user():
    current_user = storage.get_active_object_from_storage((storage.CURRENT_USER))
    print(current_user)
    return current_user
