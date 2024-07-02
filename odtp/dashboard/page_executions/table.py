import pandas as pd
from nicegui import app, ui

import odtp.dashboard.utils.helpers as helpers
import odtp.dashboard.utils.ui_theme as ui_theme




def ui_table_layout(executions):
    if not executions:
        ui_theme.ui_no_items_yet("Executions")
        return
    df = pd.DataFrame(data=executions)
    df["_id"] = df["_id"].astype("string")
    df["createdAt"] = df["createdAt"]
    df["start_timestamp"] = df["start_timestamp"].fillna('')
    df["end_timestamp"] = df["end_timestamp"].fillna('')
    df["steps"] = df["steps"].apply(helpers.pd_lists_to_counts).astype("string")
    df = df[["createdAt", "title", "steps", "start_timestamp", "end_timestamp"]]
    df = df.sort_values(by="createdAt", ascending=False)
    ui.table.from_pandas(df)
