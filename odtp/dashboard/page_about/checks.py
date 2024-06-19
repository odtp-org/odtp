import logging
import odtp.mongodb.db as db
import odtp.helpers.git as odtp_git
from odtp.storage import s3Manager
import odtp.helpers.settings as settings
from nicegui import ui
import boto3


log = logging.getLogger(__name__)


def ui_checks():
    with ui.row():
        ui_mongo_check()
    with ui.row():
        ui_git_check()
    with ui.row():
        ui_check_s3()


def ui_mongo_check():
    try:   
        server_info = db.check_connection()
        ui.icon("check").classes("text-teal text-lg")
        ui.label("Mongo DB").classes("text-teal")     
    except Exception as e:
        ui.icon("clear").classes("text-red text-lg")
        ui.label("Mongo DB connection failed").classes("text-red")
        log.exception(f"mongo db connection failed with {e}, server_info: {server_info}")
        raise settings.OdtpSettingsException(f"mongo db connection failed with {e}, server_info: {server_info}")


def ui_git_check():
    response = odtp_git.test_token()
    if response.status_code == 200:
        ui.icon("check").classes("text-teal text-lg")
        ui.label("Github Token").classes("text-teal")  
    else:
        ui.icon("clear").classes("text-red text-lg")
        ui.label("Github Token not valid").classes("text-red")    


def ui_check_s3():
    s3 = s3Manager()
    try:
        s3.test_connection()
        ui.icon("check").classes("text-teal text-lg")
        ui.label("S3").classes("text-teal")          
    except Exception as e:    
        ui.icon("clear").classes("text-red text-lg")
        ui.label("Storage connection failed").classes("text-red")
        log.exception(f"Storage connection failed with {e}, server_info: {server_info}")
        raise settings.OdtpSettingsException(f"Storage connection failed with {e}, server_info: {server_info}")