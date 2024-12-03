import pandas as pd
from nicegui import ui

import odtp.dashboard.utils.helpers as helpers

def ui_table_layout(digital_twins):
    if not digital_twins:
            return
    ui.markdown(
        """
        #### Users digital twins
        """
    )
    if not digital_twins:
        return
    df = pd.DataFrame(data=digital_twins)
    df["_id"] = df["_id"].astype("string")
    df["executions"] = (
        df["executions"].apply(helpers.pd_lists_to_counts).astype("string")
    )
    df = df[["_id", "name", "status", "created_at", "updated_at", "executions"]]
    ui.table.from_pandas(df)
