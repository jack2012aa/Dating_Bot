from models import database
from flask import current_app

def has_empty_column(userID: str):
    '''
    Return whether user's editting book has a empty column(s).
    If anything wrong happens, return True
    '''

    database.ping(True)
    cursor = database.cursor()
    sql = f"SELECT count(*) FROM editting_books WHERE userID = '{userID}' AND name IS NOT NULL AND summary IS NOT NULL AND photo IS NOT NULL AND category IS NOT NULL;"
    
    try:
        cursor.execute(sql)
        result = cursor.fetchone()[0] == 0
        cursor.close()
        return result
    except Exception as err:
        cursor.close()
        current_app.logger.error(f"{type(err)}, {str(err.args)}, {userID}")
        return True