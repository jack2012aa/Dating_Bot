from models import database
from flask import current_app
from datetime import datetime

def accept_invitation(invitorID:str, invitor_upload_time: str, invitedID: str, invited_upload_time: str):
    '''Accept invitation and expire all other invitations'''

    try:
        cursor = database.cursor()
        cursor.execute(f"UPDATE invitations SET accept = 'T', expired = 'T' WHERE invitorID = '{invitorID}' AND invitedID = '{invitedID}' AND invited_upload_time = '{invited_upload_time}' AND invitor_upload_time = '{invitor_upload_time}';")

        #Insert into revert list
        cursor.execute(f"INSERT INTO revert_invitations_list (invitorID, invitor_upload_time, invitedID, invited_upload_time) SELECT invitorID, invitor_upload_time, invitedID, invited_upload_time FROM invitations WHERE (invitorID = '{invitorID}' OR invitedID = '{invitedID}' OR invitorID = '{invitedID}' OR invitedID = '{invitorID}') AND accept = 'F' AND deny = 'F' AND expired = 'F';")
        cursor.execute(f"INSERT INTO revert_books_list (userID, upload_time) SELECT userID, upload_time FROM books WHERE (userID = '{invitorID}' AND upload_time = '{invitor_upload_time}') OR (userID = '{invitedID}' AND upload_time = '{invited_upload_time}');")

        #Set expired/blocked
        cursor.execute(f"UPDATE invitations SET expired = 'T' WHERE (invitorID = '{invitorID}' OR invitedID = '{invitedID}' OR invitorID = '{invitedID}' OR invitedID = '{invitorID}') AND accept = 'F' AND deny = 'F' AND expired = 'F';")
        cursor.execute(f"UPDATE books SET blocked = 'T' WHERE userID = '{invitorID}' AND upload_time = '{invitor_upload_time}';")
        cursor.execute(f"UPDATE books SET blocked = 'T' WHERE userID = '{invitedID}' AND upload_time = '{invited_upload_time}';")
        database.commit()
        cursor.close()
        current_app.logger.debug(f"[{datetime.now()}] Call: accept_invitation({invitorID}, {invitor_upload_time}, {invitedID}, {invited_upload_time})")
        return True
    except Exception as err:
        current_app.logger.error(f"[{datetime.now()}] Call: accept_invitation({invitorID}, {invitor_upload_time}, {invitedID}, {invited_upload_time}), {type(err)}, {str(err.args)}")
        cursor.close()
        return False