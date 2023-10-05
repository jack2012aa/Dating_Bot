from models import database
from flask import current_app
from datetime import datetime

def get_exchanged_book_and_lineID(userID: str):
    '''Return book [userID, upload_time] and lineID whose exchange book with user'''

    cursor = database.cursor()
    sql = f"SELECT a.invitedID, a.invited_upload_time, b.lineID, a.invitorID, a.invitor_upload_time, c.lineID FROM invitations AS a JOIN friends AS b ON a.invitedID = b.userID JOIN friends AS c ON a.invitorID = c.userID WHERE (invitedID = '{userID}' OR invitorID = '{userID}') AND accept = 'T' ORDER BY checked_time DESC LIMIT 1;"
    cursor.execute(sql)
    result = cursor.fetchall()[0]
    cursor.close()
    

    if result[0] != userID:
        return [result[0], result[1], result[2]]
    return [result[3], result[4], result[5]]