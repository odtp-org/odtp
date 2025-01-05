import odtp.mongodb.db as db


def validate_execution_name_unique(execution_name):
    executions = db.get_collection(db.collection_executions)
    execution_names = {execution.get("title") for execution in executions}
    if execution_name in execution_names:
        return False
    return True
