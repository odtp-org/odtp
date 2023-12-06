
from odtp.initial_setup import odtpDatabase

odtpDB = odtpDatabase()
odtpDB.run_initial_setup()

# Save all collections as JSON
odtpDB.dbManager.export_all_collections_as_json('odtpDB.json')

# Deletion
odtpDB.deleteAll()
