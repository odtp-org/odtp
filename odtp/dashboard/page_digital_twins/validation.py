import odtp.mongodb.db as db


def validate_digital_twin_name_unique(digital_twin_name, user_id):
    digital_twins = db.get_collection(db.collection_digital_twins, query={"userRef": user_id})
    digital_twin_names = {digital_twin.get("name") for digital_twin in digital_twins}
    if digital_twin_name in digital_twin_names:
        return False
    return True
