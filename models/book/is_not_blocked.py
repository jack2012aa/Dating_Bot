from models import database
from flask import current_app
from datetime import datetime

def is_not_blocked(userID: str, upload_time: str):
    '''Return whether a book is blocked. If the book doesn't exist, return false'''

    cursor = database.cursor()
    sql = f"SELECT count(*) FROM books WHERE userID = '{userID}' AND upload_time = '{upload_time}' AND blocked = 'F';"
    cursor.execute(sql)
    result = cursor.fetchone()[0] == 1
    cursor.close()
    current_app.logger.debug(f"[{datetime.now()}] Call: is_not_blocked({userID}, {upload_time}), sql = {sql}, result = {result}")
    return result