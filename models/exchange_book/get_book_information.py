from models import database
from flask import current_app

def get_book_information(userID: str, upload_time: str = None, fields = [], all: bool = False):
    '''
    Return book info.
    Return [name, summary, photo, category] if all == True.
    Return [None] if the field is NULL or something wrong happens.
    :param str userID: line user id
    :param str upload_time: book's uploaded time
    :param list fields: ["userID", "name", "summary", "photo", "category"]
    :param bool all: search on all fields
    '''

    database.ping(True)
    cursor = database.cursor()
    if all:
        sql = f"SELECT name, summary, photo, category FROM books WHERE userID = '{userID}' AND upload_time = '{upload_time}';"
    else:
        fields = ",".join(fields)
        sql = f"SELECT {fields} FROM books WHERE userID = '{userID}' AND upload_time = '{upload_time}';"

    try:
        cursor.execute(sql)
        current_app.logger.debug(f"userID: {userID}, upload_time: {upload_time}, fields: {fields}, all: {all}, sql: {sql}")
        result = cursor.fetchone()
        cursor.close()
        if result == None:
            return [None]
        return list(result)
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, upload_time: {upload_time}, fields: {fields}, all: {all}, sql: {sql}")
        return [None]