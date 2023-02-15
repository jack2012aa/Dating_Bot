from models import database
from flask import current_app
from datetime import datetime

def exist_book(userID: str, upload_time: str):
    '''Return whether book [userID, upload_time] is in 'books' table, ignoring blocked.'''

    cursor = database.cursor()
    sql = f"SELECT count(*) FROM books WHERE userID = '{userID}' AND upload_time = '{upload_time}';"
    cursor.execute(sql)
    result = cursor.fetchone()[0] == 1
    current_app.logger.debug(f"[{datetime.now()}] Call: exist_book({userID}, {upload_time}), sql = {sql}, result = {result}")
    return result