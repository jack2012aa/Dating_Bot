from models import database
from flask import current_app
from datetime import datetime

def get_book_tags(userID: str, upload_time: str):
    '''Return all tags of the book. If it doesn't have tag return None'''

    cursor = database.cursor()
    sql = f"SELECT tag FROM book_tags WHERE userID = '{userID}' AND upload_time = '{upload_time}';"
    cursor.execute(sql)
    tags = list(map(lambda x: x[0], cursor.fetchall()))
    cursor.close()
    current_app.logger.debug(f"[{datetime.now()}] Call: get_book_tags({userID}, {upload_time}), sql = {sql}, result = {tags}")
    if len(tags) == 0:
        return [None]
    else:
        return tags