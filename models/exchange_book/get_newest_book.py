from . import Book, get_book_tags
from models import database
from flask import current_app

def get_newest_book(userID: str):
    '''
    Return user's newest book.
    If something wrong happens return None.
    :Return Book object
    '''

    database.ping(True)
    cursor = database.cursor()
    sql = f"SELECT userID, upload_time, name, summary, photo, category FROM books WHERE userID = '{userID}' ORDER BY upload_time DESC LIMIT 1;"
    try:
        current_app.logger.debug(f"userID: {userID}, sql = {sql}")
        cursor.execute(sql)
        book = list(cursor.fetchone())
        book.append(get_book_tags.get_book_tags(book[0], book[1]))
        cursor.close()
        return Book(book[0], book[1], book[2], book[3], book[4], book[5], book[6])
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, sql = {sql}")
        return None