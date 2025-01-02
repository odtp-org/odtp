import odtp.mongodb.db as db


def validate_digital_twin_name_unique(digital_twin_name):
    digital_twins = db.get_collection(db.collection_digital_twins)
    digital_twin_names = {digital_twin.get("name") for digital_twin in digital_twins}
    if digital_twin_name in digital_twin_names:
        return False
    return True
