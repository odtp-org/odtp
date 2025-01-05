from bson import ObjectId
import odtp.mongodb.db as db


def validate_execution_name_unique(execution_name, digital_twin_id):
    if len(execution_name) < 6:
        return False
    print(f"validating {execution_name}")
    print(f"with {digital_twin_id}")
    executions = db.get_collection(db.collection_executions, query={"digitalTwinRef": ObjectId(digital_twin_id)})
    print(executions)
    execution_names = {execution.get("title") for execution in executions}
    if execution_name in execution_names:
        return False
    return True
