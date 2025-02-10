import os
from nicegui import ui
import odtp.dashboard.utils.ui_theme as ui_theme
import odtp.dashboard.utils.helpers as helpers
import odtp.helpers.secrets as secrets
import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.page_users.storage as storage
from odtp.helpers.settings import ODTP_PASSWORD, ODTP_SECRETS_DIR


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
        if not self.current_user:
            return
        file_dict = helpers.get_secrets_files(self.current_user.get("workdir"))
        if file_dict:
            with ui.column():
                ui.label("Uploaded Secrets Files:").classes("font-bold")
                for value in file_dict.values():
                    ui.label(f"📄 {value} ")
        else:
            ui.label("No files found in the secrets directory.")

    async def handle_upload(self, event):
        """Handle file upload and encrypt the file."""
        content = event.content.read().decode('utf-8')
        file_path = os.path.join(self.current_user["workdir"], ODTP_SECRETS_DIR, event.name)

        salt, iv, encrypted_data = secrets.encrypt_text(content, ODTP_PASSWORD)
        # Save the encrypted data to a file
        self.encrypted_file_path = file_path
        with open(self.encrypted_file_path, "wb") as f:
            f.write(salt + iv + encrypted_data)

        ui.notify(f"Encrypted file saved to: {self.encrypted_file_path}", type="positive")
        self.ui_secrets.refresh()
