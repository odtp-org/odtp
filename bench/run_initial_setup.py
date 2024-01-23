import sys
import json
sys.path.append('..')

from odtp.setup import mongodbDatabase

odtpDB = mongodbDatabase()
odtpDB.run_initial_setup()

# Save all collections as JSON
all_data_as_json = odtpDB.dbManager.get_all_collections(as_json=True)
with open("odtpDB.json", 'w') as json_file:
    print(all_data_as_json)

# Deletion
odtpDB.deleteAll()
