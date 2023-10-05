from . import Book, get_book_tags
from models import database
from flask import current_app

def get_book(userID: str, upload_time: str):
    '''
    Return a Book in database. If the book doesn't exist return None
    '''

    sql = f"SELECT userID, upload_time, name, summary, photo, category FROM books WHERE userID = '{userID}' AND upload_time = '{upload_time}';"
    database.ping(True)
    cursor = database.cursor()
    
    try:
        current_app.logger.debug(f"userID: {userID}, upload_time: {upload_time}, sql: {sql}")
        cursor.execute(sql)
        book = cursor.fetchone()
        cursor.close()

        if book == None:
            return None

        tags = get_book_tags.get_book_tags(userID, upload_time)
        return Book(book[0], book[1], book[2], book[3], book[4], book[5], tags)
        
    except Exception as err:
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}, upload_time: {upload_time}, sql: {sql}")
        cursor.close()
        return None