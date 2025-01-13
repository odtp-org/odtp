import os
from nicegui import ui, events
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.helpers.secrets as secrets
import odtp.dashboard.page_users.storage as storage
from odtp.helpers.settings import ODTP_PASSWORD

SECRETS_DIR = "secrets"


class Workarea():
    def __init__(self):
        self.current_user = storage.storage_get_current_user()
        self.ui_workarea()
        self.ui_secrets()

    def ui_workarea(self):
        with ui.row().classes("w-full"):
            ui.markdown(
                """
                ## Manage Users
                """
            )
        current_user = storage.storage_get_current_user()
        if not current_user:
            return
        with ui.row():
            ui.markdown(
                f"""
                #### Current Selection
                - **user**: {current_user.get("user_name")}
                - **work directory**: {current_user.get("workdir")}
                """
            )
        with ui.column():
            ui.button(
                "Manage digital twins",
                on_click=lambda: ui.open(ui_theme.PATH_DIGITAL_TWINS),
                icon="link",
            )
            ui.upload(
                on_upload=self.handle_upload,
                label="upload secrets (store encrypted)"
            ).classes('max-w-full')

    @ui.refreshable
    def ui_secrets(self):
        secrets_path = os.path.join(self.current_user.get("workdir"), SECRETS_DIR)
        if os.path.exists(secrets_path):
            with ui.grid(columns="5px auto"):
                for file in os.listdir(secrets_path):
                    ui.icon("check").classes("text-teal text-lg 20px")
                    ui.label(f"secrets uploaded: {file}")

    async def handle_upload(self, event):
        """Handle file upload and encrypt the file."""
        content = event.content.read().decode('utf-8')
        dir_path = os.path.join(self.current_user["workdir"], SECRETS_DIR)
        file_path = os.path.join(dir_path, event.name)
        os.makedirs(dir_path, exist_ok=True)

        salt, iv, encrypted_data = secrets.encrypt_text(content, ODTP_PASSWORD)
        # Save the encrypted data to a file
        self.encrypted_file_path = file_path
        with open(self.encrypted_file_path, "wb") as f:
            f.write(salt + iv + encrypted_data)

        ui.notify(f"Encrypted file saved to: {self.encrypted_file_path}", type="positive")
        self.ui_secrets.refresh()
