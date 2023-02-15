from models import database
from flask import current_app
from datetime import datetime

def insert_invitation(invitorID: str, invitor_upload_time: str, invitedID: str, invited_upload_time: str):
    '''Insert invitation. Return false if the invitation already exist'''

    cursor = database.cursor()
    sql = f"INSERT INTO invitations (invitorID, invitor_upload_time, invitedID, invited_upload_time) VALUES ('{invitorID}', '{invitor_upload_time}', '{invitedID}', '{invited_upload_time}');"
    try:
        cursor.execute(sql)
        database.commit()
        cursor.close()
        current_app.logger.debug(f"[{datetime.now()}] Call: insert_invitation({invitorID}, {invitor_upload_time}, {invitedID}, {invited_upload_time}), sql = {sql}")
        return True
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"[{datetime.now()}] Call: insert_invitation({invitorID}, {invitor_upload_time}, {invitedID}, {invited_upload_time}), sql = {sql}, {type(err)}, {str(err.args)}")
        return False
