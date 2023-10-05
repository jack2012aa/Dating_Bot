from models import database
from flask import current_app
from datetime import datetime

def is_expired(invitorID: str, invitor_upload_time: str, invitedID: str, invited_upload_time: str):
    '''Return whether an invitation is expired. If the invitation isn't exist, return True'''

    cursor = database.cursor()
    sql = f"SELECT expired FROM invitations WHERE invitorID = '{invitorID}' AND invitedID = '{invitedID}' AND invited_upload_time = '{invited_upload_time}' AND invitor_upload_time = '{invitor_upload_time}';"
    cursor.execute(sql)
    expired = cursor.fetchone()
    if expired == None:
        return True
    result = expired[0] == "T"
    cursor.close()
    
    return result