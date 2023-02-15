from models import database
from flask import current_app
from datetime import datetime

def get_all_invitations(userID: str):
    '''Return user's all invitations [invitorID, invitor_upload_time, invitedID, invited_upload_time]. If no invitation return None'''

    cursor = database.cursor()
    sql = f"SELECT invitorID, invitor_upload_time, invitedID, invited_upload_time FROM invitations WHERE invitedID = '{userID}' AND expired = 'F' AND deny = 'F';"
    cursor.execute(sql)
    result = list(map(lambda x: list(x), cursor.fetchall()))
    cursor.close
    current_app.logger.debug(f"[{datetime.now()}] Call: get_all_invitations({userID}), sql = {sql}")
    if len(result) == 0:
        return None
    return result