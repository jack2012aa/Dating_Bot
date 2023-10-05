from models import database
from flask import current_app

def get_book_tags(userID: str, upload_time: str):
    '''
    Return all tags of the book. If it doesn't have tag or something wrong happens return [None].
    '''

    database.ping(True)
    cursor = database.cursor()
    sql = f"SELECT tag FROM book_tags WHERE userID = '{userID}' AND upload_time = '{upload_time}';"
    try:
        cursor.execute(sql)
        tags = list(map(lambda x: x[0], cursor.fetchall()))
        cursor.close()
        current_app.logger.debug(f"userID: {userID}, upload_time: {upload_time}, sql: {sql}")
        if len(tags) == 0:
            return [None]
        else:
            return tags
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, upload_time: {upload_time}, sql: {sql}")
        return [None]