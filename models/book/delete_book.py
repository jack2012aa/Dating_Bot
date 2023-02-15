from models import database
from flask import current_app
from datetime import datetime

def delete_book(userID: str, upload_time: str):
    '''Block the book and expire all related invitations'''

    cursor = database.cursor()
    sql1 = f"UPDATE invitations SET expired = 'T' WHERE (invitedID = '{userID}' AND invited_upload_time = '{upload_time}') OR (invitorID = '{userID}' AND invitor_upload_time = '{upload_time}');"
    sql2 = f"UPDATE books SET blocked = 'T' WHERE userID = '{userID}' AND upload_time = '{upload_time}';"

    try:
        cursor.execute(sql1)
        cursor.execute(sql2)
        database.commit()
        cursor.close()
        current_app.logger.debug(f"[{datetime.now()}] Call: delete_book({userID}, {upload_time}), sql1 = {sql1}, sql2 = {sql2}")
        return True
    except Exception as err:
        current_app.logger.error(f"[{datetime.now()}] SQL error. Call: delete_book({userID}, {upload_time}), sql1 = {sql1}, sql2 = {sql2}, {type(err)}, {str(err.args)}")
        return False