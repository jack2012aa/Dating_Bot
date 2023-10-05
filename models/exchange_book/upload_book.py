from models import database
from flask import current_app

def upload_book(userID: str):
    '''Move a book from editting_books to books. Move its tags from editting_tags to book tags. Delete the old one'''

    sql = f"CALL upload_book('{userID}')"
    try:
        database.ping(True)
        cursor = database.cursor()
        cursor.execute(sql)
        database.commit()
        cursor.close()
        current_app.logger.debug(f"userID: {userID}")
        return True
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args)}, userID: {userID}")
        return False