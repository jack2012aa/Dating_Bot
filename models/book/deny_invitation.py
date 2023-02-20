from models import database
from flask import current_app
from datetime import datetime

def deny_invitation(invitorID: str, invitor_upload_time: str, invitedID: str, invited_upload_time: str):

    try:
        cursor = database.cursor()
        cursor.execute(f"UPDATE invitations SET deny = 'T', expired = 'T' WHERE invitorID = '{invitorID}' AND invitedID = '{invitedID}' AND invited_upload_time = '{invited_upload_time}' AND invitor_upload_time = '{invitor_upload_time}';")
        database.commit()
        cursor.close()
        
        return True
    except Exception as err:
        
        cursor.close()
        return False