from models import database
from flask import current_app
from datetime import datetime

def has_invitation(invitorID: str, invitor_upload_time, invitedID:str, invited_upload_time: str, accept = None, deny = None, expired = None):
    '''
    Return whether has a (un)accepted, (un)denied and (un)expired invitation.
    If accept, deny, expired = None, then won't filter on them.
    '''

    if accept == True:
        accept = "AND accept = 'T'"
    elif accept == False:
        accept = "AND accept = 'F'"
    else:
        accept = ""

    if deny == True:
        deny = "AND deny = 'T'"
    elif deny == False:
        deny = "AND deny = 'F'"
    else:
        deny = ""

    if expired == True:
        expired = "AND expired = 'T'"
    elif expired == False:
        expired = "AND expired = 'F'"
    else:
        expired = ""

    sql = f"SELECT * FROM invitations WHERE invitorID = '{invitorID}' AND invitedID = '{invitedID}' AND invited_upload_time = '{invited_upload_time}' AND invitor_upload_time = '{invitor_upload_time}' {accept} {deny} {expired};"
    cursor = database.cursor()
    cursor.execute(sql)
    result = len(cursor.fetchall()) != 0
    cursor.close()
    
    return result