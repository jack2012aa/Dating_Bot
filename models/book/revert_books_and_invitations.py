from models import database
from flask import current_app
from datetime import datetime

def revert_books_and_invitations():
    '''Revert books and invitations expired last day'''

    try:
        cursor = database.cursor()
        cursor.execute("UPDATE books SET blocked = 'F' WHERE (userID, upload_time) IN (SELECT userID, upload_time FROM revert_books_list);")
        cursor.execute("UPDATE invitations SET expired = 'F' WHERE (invitorID, invitor_upload_time, invitedID, invited_upload_time) IN (SELECT (invitorID, invitor_upload_time, invitedID, invited_upload_time) FROM revert_invitations_list);")
        cursor.execute("DELETE FROM revert_books_list;")
        cursor.execute("DELETE FROM revert_invitations_list;")
        database.commit()
        cursor.close()
        current_app.logger.info(f"[{datetime.now()}] Revert successfully")
        return True
    except Exception as err:
        current_app.logger.info(f"[{datetime.now()}] Revert failure, {type(err)}, {str(err.args)}")
        cursor.close()
        return False