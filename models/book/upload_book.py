from models import database
from flask import current_app
from datetime import datetime

def upload_book(userID: str):
    '''Move a book from editting_books to books. Move its tags from editting_tags to book tags. Delete the old one'''

    try:
        cursor = database.cursor()
        cursor.execute(f"INSERT INTO books (userID, name, summary, photo, category) SELECT userID, name, summary, photo, category FROM editting_books WHERE userID = '{userID}';")
        cursor.execute(f"DELETE FROM editting_books WHERE userID = '{userID}';")
        database.commit()
        cursor.execute(f"SELECT upload_time FROM books WHERE userID = '{userID}' AND blocked = 'F';")
        upload_time = cursor.fetchall()[0][0]
        cursor.execute(f"SELECT tag FROM editting_tags WHERE userID = '{userID}';")
        tags = list(map(lambda x: x[0], cursor.fetchall()))
        cursor.execute(f"DELETE FROM editting_tags WHERE userID = '{userID}';")
        for tag in tags:
            cursor.execute(f"INSERT INTO book_tags (userID, tag, upload_time) VALUES ('{userID}', '{tag}', '{upload_time}');")
        database.commit()
        cursor.close()
        current_app.logger.debug(f"[{datetime.now()}] Call: upload_book({userID})")
        return True
    except Exception as err:
        current_app.logger.error(f"[{datetime.now()}] SQL error. Call: upload_book({userID}), {type(err)}, {str(err.args)}")
        cursor.close()
        return False